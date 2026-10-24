import sqlite3
import os
from datetime import datetime

# Nombre del archivo donde se guardan los datos de la aplicación.
DB_NAME = "gestion_comercial.db"

def inicializar_bd():
    # Crea las tablas necesarias en la base de datos del proyecto.
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, DB_NAME)
    
    conexion = sqlite3.connect(db_path)
    cursor = conexion.cursor()
    
    # Tabla de Clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            edad INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            pago TEXT NOT NULL
        )
    """)
    
    # Tabla de Ventas (Con columna fecha)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            producto TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            subtotal REAL NOT NULL,
            descuento REAL NOT NULL,
            recargo REAL NOT NULL,
            metodo_pago TEXT NOT NULL,
            total REAL NOT NULL,
            fecha TEXT NOT NULL
        )
    """)
    
    # Tabla para Cierres de Caja
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cierres_caja (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT UNIQUE NOT NULL,
            total_ingresos REAL NOT NULL,
            total_ventas INTEGER NOT NULL,
            estado TEXT NOT NULL
        )
    """)
    
    conexion.commit()
    conexion.close()

# Guarda un cliente nuevo en la base de datos.
def guardar_cliente_db(nombre, edad, tipo, pago):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, DB_NAME)
    conexion = sqlite3.connect(db_path)
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO clientes (nombre, edad, tipo, pago) VALUES (?, ?, ?, ?)", (nombre, edad, tipo, pago))
    conexion.commit()
    conexion.close()

# Devuelve todos los clientes guardados.
def cargar_clientes_db():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, DB_NAME)
    conexion = sqlite3.connect(db_path)
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, edad, tipo, pago FROM clientes")
    registros = cursor.fetchall()
    conexion.close()
    return registros

# Elimina el cliente que corresponde al identificador recibido.
def eliminar_cliente_db(cliente_id):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, DB_NAME)
    conexion = sqlite3.connect(db_path)
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
    conexion.commit()
    conexion.close()

# Guarda una venta e incluye la fecha en que se registró.
def guardar_venta_db(cliente, producto, cantidad, precio, subtotal, descuento, recargo, metodo_pago, total, fecha_personalizada):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, DB_NAME)
    conexion = sqlite3.connect(db_path)
    cursor = conexion.cursor()
    cursor.execute(
        """INSERT INTO ventas (cliente, producto, cantidad, precio, subtotal, descuento, recargo, metodo_pago, total, fecha) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (cliente, producto, cantidad, precio, subtotal, descuento, recargo, metodo_pago, total, fecha_personalizada)
    )
    conexion.commit()
    conexion.close()

# Devuelve las ventas guardadas con sus datos en el orden esperado por la aplicación.
def cargar_ventas_db():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, DB_NAME)
    conexion = sqlite3.connect(db_path)
    cursor = conexion.cursor()
    cursor.execute("SELECT id, cliente, producto, cantidad, precio, total, metodo_pago, fecha, subtotal, descuento, recargo FROM ventas ORDER BY id ASC")
    registros = cursor.fetchall()
    conexion.close()
    return registros

# Registra el cierre de caja y los totales del día.
def registrar_cierre_caja(fecha, total_ingresos, total_ventas):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, DB_NAME)
    conexion = sqlite3.connect(db_path)
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO cierres_caja (fecha, total_ingresos, total_ventas, estado) VALUES (?, ?, ?, 'CERRADO')",
        (fecha, total_ingresos, total_ventas)
    )
    conexion.commit()
    conexion.close()

# Indica si la caja ya fue cerrada en la fecha recibida.
def caja_esta_cerrada(fecha):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, DB_NAME)
    conexion = sqlite3.connect(db_path)
    cursor = conexion.cursor()
    cursor.execute("SELECT estado FROM cierres_caja WHERE fecha = ?", (fecha,))
    registro = cursor.fetchone()
    conexion.close()
    return registro is not None and registro[0] == "CERRADO"