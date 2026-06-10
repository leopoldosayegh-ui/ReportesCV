"""
Guía de instalación y uso del sistema de reportes
"""

# Instalación rápida

## 1. Clonar el repositorio
```bash
git clone https://github.com/leopoldosayegh-ui/ReportesCV.git
cd ReportesCV
```

## 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

## 3. Configurar base de datos (opcional)
Si deseas usar base de datos en línea en lugar de archivos JSON, edita `config.py`:

```python
DATABASE_CONFIG = {
    'host': 'tu_host.com',
    'user': 'tu_usuario',
    'password': 'tu_contraseña',
    'database': 'condominios_venezuela',
    'port': 3306
}
```

# Uso

## Generar reporte con datos de prueba (JSON)
```bash
python main.py --month 6 --year 2026 --format both
```

## Generar reporte de un edificio específico
```bash
python main.py --month 6 --year 2026 --building "Edificio A" --format both
```

## Generar solo en Excel
```bash
python main.py --month 6 --year 2026 --format excel
```

## Generar solo en PDF
```bash
python main.py --month 6 --year 2026 --format pdf
```

## Usar base de datos en línea
```bash
python main.py --month 6 --year 2026 --data-source database --format both
```

## Ver opciones disponibles
```bash
python main.py --help
```

# Estructura de datos esperada

## Base de Datos (MySQL)

### Tabla: buildings
```sql
CREATE TABLE buildings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabla: units
```sql
CREATE TABLE units (
    id INT PRIMARY KEY AUTO_INCREMENT,
    building_id INT NOT NULL,
    number VARCHAR(20) NOT NULL,
    floor INT,
    type VARCHAR(50),
    owner_name VARCHAR(100),
    monthly_rent DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (building_id) REFERENCES buildings(id)
);
```

### Tabla: payments
```sql
CREATE TABLE payments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    unit_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_date DATE NOT NULL,
    concept VARCHAR(100),
    payment_method VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (unit_id) REFERENCES units(id)
);
```

# Archivos generados

Los reportes se guardan en la carpeta `output/`:
- `Reporte_EdificioA_06_2026.xlsx` - Reporte en Excel
- `Reporte_EdificioA_06_2026.pdf` - Reporte en PDF

# Campos del reporte

Cada reporte contiene:

| Campo | Descripción |
|-------|-------------|
| Unidad | Número identificador del apartamento |
| Propietario | Nombre del dueño |
| Renta Mensual | Monto esperado de la renta |
| Deuda del Mes | Renta no pagada en el mes |
| Pago Recibido | Monto total pagado en el mes |
| Concepto de Pago | Tipo de pago (renta actual, anterior, etc.) |
| Balance | Pago recibido menos deuda |

**TOTALES:**
- Renta Total Esperada
- Deuda Total del Mes
- Total de Pagos Recibidos
- Balance General

# Próximos pasos

1. Proporcionar credenciales de base de datos
2. Validar estructura de tablas en tu sistema
3. Configurar conexión automática
4. Integración con tu aplicación web

¿Necesitas ayuda con algún paso?
