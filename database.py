import sqlite3
import os

DB_NAME = "gestion_comercial.db"


def _conectar_bd():
    """Abre la base de datos ubicada junto a este archivo."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, DB_NAME)
    return sqlite3.connect(db_path)


def inicializar_bd():
    """Crea las tablas necesarias y carga productos si el catálogo está vacío."""
    conexion = _conectar_bd()
    cursor = conexion.cursor()

    # Cada tabla almacena un tipo de información que usa la aplicación.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            edad INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            pago TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            item TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL,
            departamento TEXT NOT NULL
        )
    """)

    # Los productos de ejemplo se agregan solo al crear un catálogo vacío.
    cursor.execute("SELECT COUNT(*) FROM productos")
    # Se consulta el contador para no duplicar los datos iniciales.
    if cursor.fetchone()[0] == 0:
        productos_iniciales = [
            ("754812", "Laptop Gamer Pro 15", 9687.50, 15, "Laptops"),
            ("759203", "Laptop Ultrabook Slim", 7362.50, 20, "Laptops"),
            ("218452", "Mouse Inalámbrico Ergonómico", 197.63, 50, "Periféricos"),
            ("213907", "Mouse Gamer RGB 16DPI", 348.75, 40, "Periféricos"),
            ("443219", "Memoria USB 32GB Kingston", 77.42, 100, "Almacenamiento"),
            ("339104", "Cámara Web HD 1080p", 348.75, 35, "Cámaras"),
            ("881240", "Monitor 24 pulgadas IPS", 1240.00, 20, "Monitores"),
            ("597301", "Audífonos Gamer con Micrófono", 426.25, 35, "Audio"),
            ("614082", "Hub USB-C 7 en 1", 271.25, 45, "Conectividad"),
            ("195230", "Impresora Multifuncional Tinta", 1123.75, 10, "Impresión"),
            ("924713", "Power Bank 20000mAh", 325.50, 35, "Energía")
        ]
        cursor.executemany(
            """INSERT INTO productos
               (item, nombre, precio, stock, departamento)
               VALUES (?, ?, ?, ?, ?)""",
            productos_iniciales,
        )

    # El identificador de grupo permite reunir las líneas de un mismo ticket.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_grupo TEXT NOT NULL,
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

    # Se conserva un resumen diario independiente de las líneas de venta.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cierres_caja (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT UNIQUE NOT NULL,
            ventas_realizadas INTEGER NOT NULL,
            productos_vendidos INTEGER NOT NULL,
            efectivo REAL NOT NULL,
            tarjeta REAL NOT NULL,
            transferencia REAL NOT NULL,
            descuentos REAL NOT NULL,
            recargos REAL NOT NULL,
            total_vendido REAL NOT NULL,
            venta_mayor REAL NOT NULL,
            venta_menor REAL NOT NULL,
            promedio_venta REAL NOT NULL,
            estado TEXT NOT NULL
        )
    """)

    conexion.commit()
    conexion.close()

def cargar_productos_db():
    """Devuelve los productos ordenados por su código de catálogo."""
    conexion = _conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("SELECT item, nombre, precio, stock, departamento FROM productos ORDER BY item ASC")
    res = cursor.fetchall()
    conexion.close()
    return res

def obtener_producto_por_item(item):
    """Devuelve el producto que coincide con el código indicado, si existe."""
    conexion = _conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("SELECT item, nombre, precio, stock, departamento FROM productos WHERE item = ?", (item,))
    res = cursor.fetchone()
    conexion.close()
    return res

def guardar_cliente_db(nombre, edad, tipo, pago):
    """Guarda un cliente nuevo con sus datos de contacto y preferencias."""
    conexion = _conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO clientes (nombre, edad, tipo, pago) VALUES (?, ?, ?, ?)", (nombre, edad, tipo, pago))
    conexion.commit()
    conexion.close()

def cargar_clientes_db():
    """Devuelve los clientes registrados y sus datos principales."""
    conexion = _conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, edad, tipo, pago FROM clientes")
    res = cursor.fetchall()
    conexion.close()
    return res

def guardar_venta_db(venta_grupo, cliente, producto, cantidad, precio, subtotal, descuento, recargo, metodo_pago, total, fecha):
    """Guarda una línea de venta junto con los importes y datos del ticket."""
    conexion = _conectar_bd()
    cursor = conexion.cursor()
    cursor.execute(
        """INSERT INTO ventas (venta_grupo, cliente, producto, cantidad, precio, subtotal, descuento, recargo, metodo_pago, total, fecha)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (venta_grupo, cliente, producto, cantidad, precio, subtotal, descuento, recargo, metodo_pago, total, fecha)
    )
    conexion.commit()
    conexion.close()

def cargar_ventas_db():
    """Devuelve las líneas de venta en el orden en que se registraron."""
    conexion = _conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, venta_grupo, cliente, producto, cantidad, precio, total, metodo_pago, fecha, subtotal, descuento, recargo FROM ventas ORDER BY id ASC")
    res = cursor.fetchall()
    conexion.close()
    return res

def registrar_cierre_caja_detallado(fecha, v_realizadas, p_vendidos, efectivo, tarjeta, transferencia, descuentos, recargos, total_vendido, v_mayor, v_menor, promedio):
    """Guarda o reemplaza el resumen del cierre correspondiente a una fecha."""
    conexion = _conectar_bd()
    cursor = conexion.cursor()
    cursor.execute(
        """INSERT OR REPLACE INTO cierres_caja
           (fecha, ventas_realizadas, productos_vendidos, efectivo, tarjeta, transferencia, descuentos, recargos, total_vendido, venta_mayor, venta_menor, promedio_venta, estado)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'CERRADO')""",
        (fecha, v_realizadas, p_vendidos, efectivo, tarjeta, transferencia, descuentos, recargos, total_vendido, v_mayor, v_menor, promedio)
    )
    conexion.commit()
    conexion.close()


def eliminar_cliente_db(cliente_id):
    """Elimina el cliente que coincide con el identificador recibido."""
    conexion = _conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
    conexion.commit()
    conexion.close()

def guardar_producto_db(item, nombre, precio, stock, departamento):
    """Agrega un producto nuevo al catálogo."""
    conexion = _conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO productos (item, nombre, precio, stock, departamento) VALUES (?, ?, ?, ?, ?)", (item, nombre, precio, stock, departamento))
    conexion.commit()
    conexion.close()

def actualizar_producto_db(item, nombre, precio, stock, departamento):
    """Actualiza los datos descriptivos y el inventario de un producto."""
    conexion = _conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("UPDATE productos SET nombre = ?, precio = ?, stock = ?, departamento = ? WHERE item = ?", (nombre, precio, stock, departamento, item))
    conexion.commit()
    conexion.close()

def actualizar_stock_producto_db(item, nuevo_stock):
    """Actualiza únicamente la cantidad disponible de un producto."""
    conexion = _conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("UPDATE productos SET stock = ? WHERE item = ?", (nuevo_stock, item))
    conexion.commit()
    conexion.close()

def eliminar_producto_db(item):
    """Elimina del catálogo el producto que coincide con el código recibido."""
    conexion = _conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM productos WHERE item = ?", (item,))
    conexion.commit()
    conexion.close()

def obtener_cierre_caja(fecha):
    """Devuelve el cierre guardado para la fecha o None si aún no existe."""
    conexion = _conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM cierres_caja WHERE fecha = ?", (fecha,))
    res = cursor.fetchone()
    conexion.close()
    return res

def caja_esta_cerrada(fecha):
    """Indica si hay un cierre registrado como cerrado para la fecha dada."""
    conexion = _conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("SELECT estado FROM cierres_caja WHERE fecha = ?", (fecha,))
    res = cursor.fetchone()
    conexion.close()
    # La comparación solo es válida si la consulta encontró un registro de cierre.
    return res is not None and res[0] == "CERRADO"
