"""
Script para detectar automáticamente la estructura de la base de datos
"""

import sys
import json
from typing import List, Dict, Optional

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
    
    def connect(self) -> bool:
        """Intentar conectar a MySQL"""
        try:
            print(f"🔗 Intentando conectar a {self.host}:{self.port}...")
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port
            )
            print("✅ Conexión exitosa!")
            return True
        except Error as e:
            print(f"❌ Error de conexión: {e}")
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
            print(f"❌ Error al obtener tablas de {database}: {e}")
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
            print(f"❌ Error al obtener estructura de {table}: {e}")
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
    
    def get_sample_data(self, database: str, table: str, limit: int = 5) -> List[Dict]:
        """Obtener muestra de datos de una tabla"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(f"USE {database}")
            cursor.execute(f"SELECT * FROM {table} LIMIT {limit}")
            data = cursor.fetchall()
            cursor.close()
            return data
        except Error as e:
            print(f"⚠️  No se pudieron obtener datos de {table}: {e}")
            return []
    
    def close(self):
        """Cerrar conexión"""
        if self.connection:
            self.connection.close()
    
    def generate_report(self) -> Dict:
        """Generar reporte completo de la estructura"""
        report = {
            'host': self.host,
            'connection_status': 'connected' if self.connection else 'failed',
            'databases': {}
        }
        
        databases = self.get_databases()
        
        for db in databases:
            print(f"\n📊 Analizando base de datos: {db}")
            tables = self.get_tables(db)
            print(f"   Tablas encontradas: {len(tables)}")
            
            report['databases'][db] = {
                'tables': {}
            }
            
            for table in tables:
                print(f"   📋 Tabla: {table}")
                
                structure = self.get_table_structure(db, table)
                if structure:
                    row_count = structure.get('row_count', 0)
                    print(f"      Filas: {row_count}")
                    print(f"      Columnas: {len(structure.get('columns', []))}")
                    
                    # Mostrar nombres de columnas
                    for col in structure.get('columns', [])[:5]:
                        col_type = col.get('Type', 'unknown')
                        print(f"        - {col.get('Field', 'unknown')} ({col_type})")
                    
                    # Obtener muestra de datos
                    sample = self.get_sample_data(db, table, 2)
                    
                    report['databases'][db]['tables'][table] = {
                        'columns': structure.get('columns', []),
                        'row_count': row_count,
                        'sample_data': sample
                    }
        
        return report


def main():
    """Función principal"""
    print("=" * 70)
    print("🔍 DETECTOR AUTOMÁTICO DE ESTRUCTURA DE BASE DE DATOS")
    print("=" * 70)
    
    # Intentar conectar con diferentes hosts posibles
    hosts_to_try = [
        'localhost',
        '127.0.0.1',
        'condominiosvenezuela.com',
        'mysql.condominiosvenezuela.com',
        'db.condominiosvenezuela.com',
        'sql.condominiosvenezuela.com',
    ]
    
    user = '17868751'
    password = 'V17868751'
    
    detector = None
    
    for host in hosts_to_try:
        print(f"\n🔄 Intentando con host: {host}")
        detector = DatabaseDetector(host, user, password)
        
        if detector.connect():
            print(f"✅ ¡Conexión exitosa con {host}!")
            break
        else:
            detector.close()
    
    if not detector or not detector.connection:
        print("\n" + "=" * 70)
        print("❌ No se pudo conectar a ningún host")
        print("=" * 70)
        print("\n📝 Por favor proporciona:")
        print("   1. El host exacto del servidor MySQL")
        print("   2. El puerto (si es diferente a 3306)")
        print("   3. O acceso a phpMyAdmin para ver la estructura")
        sys.exit(1)
    
    # Generar reporte
    print("\n" + "=" * 70)
    print("📊 ANALIZANDO ESTRUCTURA...")
    print("=" * 70)
    
    report = detector.generate_report()
    
    # Guardar reporte
    report_file = 'database_structure.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n✅ Reporte guardado en: {report_file}")
    
    # Mostrar resumen
    print("\n" + "=" * 70)
    print("📋 RESUMEN")
    print("=" * 70)
    
    for db_name, db_info in report.get('databases', {}).items():
        print(f"\n🗄️  Base de datos: {db_name}")
        for table_name, table_info in db_info.get('tables', {}).items():
            columns = table_info.get('columns', [])
            row_count = table_info.get('row_count', 0)
            print(f"   📋 {table_name} ({row_count} filas)")
            print(f"      Campos: {', '.join([col.get('Field', '?') for col in columns[:10]])}")
    
    detector.close()
    print("\n✅ ¡Análisis completado!")


if __name__ == '__main__':
    main()
