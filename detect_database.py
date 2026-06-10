"""
Script mejorado para detectar automáticamente la estructura de la base de datos
Con manejo robusto de errores y más hosts a probar
"""

import sys
import json
from typing import List, Dict, Optional
import socket

try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:
    print("❌ Error: mysql-connector-python no está instalado")
    print("Instala con: pip install mysql-connector-python")
    sys.exit(1)


class DatabaseDetector:
    """Detector automático de estructura de base de datos"""
    
    def __init__(self, host: str, user: str, password: str, port: int = 3306):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.connection = None
        self.databases = []
    
    def test_host_connectivity(self) -> bool:
        """Verificar si el host es alcanzable"""
        try:
            socket.create_connection((self.host, self.port), timeout=2)
            return True
        except (socket.timeout, socket.error):
            return False
    
    def connect(self) -> bool:
        """Intentar conectar a MySQL"""
        try:
            print(f"  🔗 Probando conexión a {self.host}:{self.port}...", end=" ", flush=True)
            
            # Verificar conectividad primero
            if not self.test_host_connectivity():
                print("❌ Host no alcanzable")
                return False
            
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                connection_timeout=5
            )
            print("✅")
            return True
        except Error as e:
            print(f"❌ ({str(e)[:50]}...)")
            return False
        except Exception as e:
            print(f"❌ ({str(e)[:50]}...)")
            return False
    
    def get_databases(self) -> List[str]:
        """Obtener lista de bases de datos"""
        if not self.connection:
            return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            cursor.close()
            
            # Filtrar bases de datos del sistema
            user_databases = [
                db for db in databases 
                if db not in ['information_schema', 'mysql', 'performance_schema', 'sys']
            ]
            
            return user_databases
        except Error as e:
            print(f"❌ Error al obtener bases de datos: {e}")
            return []
    
    def get_tables(self, database: str) -> List[str]:
        """Obtener lista de tablas en una base de datos"""
        if not self.connection:
            return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"USE {database}")
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            cursor.close()
            return tables
        except Error as e:
            return []
    
    def get_table_structure(self, database: str, table: str) -> Dict:
        """Obtener estructura detallada de una tabla"""
        if not self.connection:
            return {}
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(f"USE {database}")
            cursor.execute(f"DESCRIBE {table}")
            columns = cursor.fetchall()
            cursor.close()
            
            structure = {
                'table': table,
                'columns': columns,
                'row_count': self.get_row_count(database, table)
            }
            return structure
        except Error as e:
            return {}
    
    def get_row_count(self, database: str, table: str) -> int:
        """Obtener cantidad de filas en una tabla"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"USE {database}")
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Error:
            return 0
    
    def get_sample_data(self, database: str, table: str, limit: int = 3) -> List[Dict]:
        """Obtener muestra de datos de una tabla"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(f"USE {database}")
            cursor.execute(f"SELECT * FROM {table} LIMIT {limit}")
            data = cursor.fetchall()
            cursor.close()
            
            # Convertir Decimal a string para JSON
            for row in data:
                for key in row:
                    if hasattr(row[key], '__float__'):
                        row[key] = float(row[key])
            
            return data
        except Error as e:
            return []
    
    def close(self):
        """Cerrar conexión"""
        if self.connection:
            self.connection.close()
    
    def generate_report(self) -> Dict:
        """Generar reporte completo de la estructura"""
        report = {
            'host': self.host,
            'user': self.user,
            'connection_status': 'connected' if self.connection else 'failed',
            'databases': {}
        }
        
        databases = self.get_databases()
        
        if not databases:
            print("⚠️  No se encontraron bases de datos")
            return report
        
        for db in databases:
            print(f"\n  📊 Base de datos: {db}")
            tables = self.get_tables(db)
            print(f"     Tablas encontradas: {len(tables)}")
            
            report['databases'][db] = {
                'tables': {}
            }
            
            for table in tables:
                structure = self.get_table_structure(db, table)
                if structure:
                    row_count = structure.get('row_count', 0)
                    columns_info = structure.get('columns', [])
                    
                    print(f"     📋 {table} ({row_count} filas, {len(columns_info)} campos)")
                    
                    # Mostrar nombres de columnas
                    col_names = [col.get('Field', 'unknown') for col in columns_info]
                    print(f"        Campos: {', '.join(col_names)}")
                    
                    # Obtener muestra de datos
                    sample = self.get_sample_data(db, table, 2)
                    
                    report['databases'][db]['tables'][table] = {
                        'columns': columns_info,
                        'row_count': row_count,
                        'sample_data': sample
                    }
        
        return report


def main():
    """Función principal"""
    print("\n" + "=" * 80)
    print(" " * 15 + "🔍 DETECTOR AUTOMÁTICO DE BASE DE DATOS")
    print("=" * 80)
    
    # Hosts a intentar
    hosts_to_try = [
        ('localhost', 3306),
        ('127.0.0.1', 3306),
        ('condominiosvenezuela.com', 3306),
        ('condominiosvenezuela.com', 5432),
        ('mysql.condominiosvenezuela.com', 3306),
        ('db.condominiosvenezuela.com', 3306),
        ('sql.condominiosvenezuela.com', 3306),
        ('database.condominiosvenezuela.com', 3306),
        ('192.168.1.1', 3306),
    ]
    
    user = '17868751'
    password = 'V17868751'
    
    print(f"\n📝 Usuario: {user}")
    print("🔐 Contraseña: (oculta)")
    print(f"\n🔄 Probando {len(hosts_to_try)} hosts...\n")
    
    detector = None
    connected_host = None
    
    for host, port in hosts_to_try:
        detector = DatabaseDetector(host, user, password, port)
        
        if detector.connect():
            print(f"\n✅ ¡¡CONEXIÓN EXITOSA!!")
            print(f"   Host: {host}:{port}")
            connected_host = (host, port)
            break
        else:
            detector.close()
    
    if not detector or not detector.connection or not connected_host:
        print("\n" + "=" * 80)
        print("❌ No se pudo conectar a ningún host")
        print("=" * 80)
        print("\n📝 SOLUCIÓN:")
        print("   1. Verifica que el host MySQL sea accesible desde tu ubicación")
        print("   2. Confirma el host exacto (ej: mysql.ejemplo.com)")
        print("   3. Confirma el puerto (generalmente 3306)")
        print("   4. Verifica que las credenciales sean correctas")
        print("\n💡 ALTERNATIVA:")
        print("   Accede a phpMyAdmin en tu hosting y comparte la estructura de tablas\n")
        sys.exit(1)
    
    # Generar reporte
    print("\n" + "=" * 80)
    print(" " * 25 + "📊 ANALIZANDO ESTRUCTURA")
    print("=" * 80)
    
    report = detector.generate_report()
    
    # Guardar reporte
    report_file = 'database_structure.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n\n✅ Reporte guardado en: {report_file}\n")
    
    # Mostrar resumen completo
    print("=" * 80)
    print(" " * 30 + "📋 RESUMEN")
    print("=" * 80)
    
    total_tables = 0
    for db_name, db_info in report.get('databases', {}).items():
        print(f"\n🗄️  BASE DE DATOS: {db_name}")
        print("─" * 80)
        for table_name, table_info in db_info.get('tables', {}).items():
            total_tables += 1
            columns = table_info.get('columns', [])
            row_count = table_info.get('row_count', 0)
            sample_data = table_info.get('sample_data', [])
            
            print(f"\n   📋 Tabla: {table_name}")
            print(f"      Filas: {row_count}")
            print(f"      Campos: {len(columns)}")
            
            # Mostrar estructura de columnas
            print(f"      Estructura:")
            for col in columns:
                field = col.get('Field', '?')
                col_type = col.get('Type', 'unknown')
                null = col.get('Null', 'YES')
                key = col.get('Key', '')
                print(f"        • {field}: {col_type} (NULL: {null}, KEY: {key if key else 'NO'})")
            
            # Mostrar datos de ejemplo
            if sample_data:
                print(f"      Ejemplo de datos ({len(sample_data)} filas):")
                for i, row in enumerate(sample_data, 1):
                    print(f"        Fila {i}: {dict(row)}")
    
    print("\n" + "=" * 80)
    print(f"✅ ANÁLISIS COMPLETADO - {total_tables} tablas encontradas")
    print(f"📍 Host conectado: {connected_host[0]}:{connected_host[1]}")
    print("=" * 80 + "\n")
    
    detector.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operación cancelada por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
