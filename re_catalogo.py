from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QGridLayout, QDialog, QFormLayout, QInputDialog
)
from PySide6.QtCore import Qt
from database import (
    cargar_productos_db, guardar_producto_db, actualizar_producto_db,
    eliminar_producto_db, obtener_producto_por_item, actualizar_stock_producto_db
)

PREFIJOS_DEPARTAMENTO = {
    "Laptops": "75",
    "Periféricos": "21",
    "Almacenamiento": "44",
    "Cámaras": "33",
    "Monitores": "88",
    "Audio": "59",
    "Conectividad": "61",
    "Impresión": "19",
    "Energía": "92",
}


class DialogoGestionProducto(QDialog):
    """Diálogo formal para Añadir o Editar un producto validando los prefijos de departamento."""

    def __init__(self, producto=None, parent=None):
        """Prepara el formulario y carga los valores si se está editando."""
        super().__init__(parent)
        self.producto = producto
        self.is_edit = producto is not None
        self.setWindowTitle("Editar producto" if self.is_edit else "Registrar producto")
        self.setFixedSize(450, 360)
        self.setStyleSheet("background-color: #f4f6f9; color: #0f172a; font-family: 'Segoe UI', sans-serif;")

        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.txt_item = QLineEdit()
        self.txt_item.setPlaceholderText("Ejemplo: 754821 (6 dígitos)")

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Nombre comercial del producto")

        self.txt_precio = QLineEdit()
        self.txt_precio.setPlaceholderText("Precio en Quetzales (Q)")

        self.txt_stock = QLineEdit()
        self.txt_stock.setPlaceholderText("Cantidad inicial en inventario")

        self.cmb_departamento = QComboBox()
        # La lista visible se genera desde el mismo mapa que valida los códigos.
        self.cmb_departamento.addItems(
            [
                f"{nombre} (Prefijo {prefijo})"
                for nombre, prefijo in PREFIJOS_DEPARTAMENTO.items()
            ]
        )

        # En edición se conserva el código, que identifica al producto de forma única.
        if self.is_edit:
            self.txt_item.setText(str(producto[0]))
            self.txt_item.setEnabled(False) # Clave primaria inalterable
            self.txt_nombre.setText(str(producto[1]))
            self.txt_precio.setText(str(producto[2]))
            self.txt_stock.setText(str(producto[3]))

            # Se selecciona el departamento guardado para mostrar el valor vigente.
            dept_actual = producto[4]
            # El texto visible incluye el prefijo, por eso se busca por nombre.
            for i in range(self.cmb_departamento.count()):
                # Se detiene la búsqueda al hallar la opción del producto.
                if dept_actual in self.cmb_departamento.itemText(i):
                    self.cmb_departamento.setCurrentIndex(i)
                    break
            self.txt_stock.setEnabled(False) # El stock se gestiona desde el módulo dedicado de stock

        btn_layout = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar Registro")
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #0071dc; color: #ffffff; font-weight: bold;
                padding: 10px 15px; border-radius: 6px; border: none;
            }
            QPushButton:hover { background-color: #005bb5; }
        """)
        self.btn_guardar.clicked.connect(self.validar_y_guardar)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #64748b; color: #ffffff; font-weight: bold;
                padding: 10px 15px; border-radius: 6px; border: none;
            }
            QPushButton:hover { background-color: #475569; }
        """)
        self.btn_cancelar.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(self.btn_cancelar)

        layout.addRow(QLabel("Código (6 dígitos):"), self.txt_item)
        layout.addRow(QLabel("Nombre del producto:"), self.txt_nombre)
        layout.addRow(QLabel("Departamento:"), self.cmb_departamento)
        layout.addRow(QLabel("Precio unitario (Q):"), self.txt_precio)
        # El inventario inicial solo se solicita al registrar un producto nuevo.
        if not self.is_edit:
            layout.addRow(QLabel("Stock Inicial:"), self.txt_stock)
        layout.addRow(btn_layout)

    def validar_y_guardar(self):
        """Valida los datos y crea o actualiza el producto seleccionado."""
        item = self.txt_item.text().strip()
        nombre = self.txt_nombre.text().strip()
        precio_str = self.txt_precio.text().strip()

        # Relaciona cada departamento con el prefijo obligatorio de sus códigos.
        dept_texto = self.cmb_departamento.currentText()
        # Se obtiene el nombre y prefijo de la opción visible en el menú.
        dept_nombre, prefijo = next(
            (
                (nombre, codigo)
                for nombre, codigo in PREFIJOS_DEPARTAMENTO.items()
                if nombre in dept_texto
            ),
            ("Energía", "92"),
        )

        # El código debe tener exactamente seis caracteres numéricos.
        if not item.isdigit() or len(item) != 6:
            QMessageBox.critical(
                self,
                "Código no válido",
                "El código debe contener exactamente seis dígitos.",
            )
            return

        # Los dos primeros dígitos deben corresponder al departamento elegido.
        if not item.startswith(prefijo):
            QMessageBox.critical(
                self,
                "Código no válido",
                f"El código del departamento {dept_nombre} debe comenzar "
                f"con el prefijo {prefijo}.",
            )
            return

        # El nombre y el precio son necesarios en cualquier tipo de registro.
        if not nombre or not precio_str:
            QMessageBox.warning(
                self,
                "Datos incompletos",
                "Complete el nombre y el precio del producto.",
            )
            return

        # La conversión rechaza precios que no sean numéricos.
        try:
            precio = float(precio_str)
            # Un precio cero o negativo no representa un producto vendible.
            if precio <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.critical(
                self,
                "Precio no válido",
                "Ingrese un precio en quetzales mayor que cero.",
            )
            return

        # El inventario se valida solo para productos nuevos; en edición se preserva.
        if not self.is_edit:
            stock_str = self.txt_stock.text().strip()
            # La conversión rechaza cantidades que no sean números enteros.
            try:
                stock = int(stock_str)
                # Las unidades disponibles no pueden ser negativas.
                if stock < 0:
                    raise ValueError
            except ValueError:
                QMessageBox.critical(
                    self,
                    "Inventario no válido",
                    "Ingrese una cantidad inicial de unidades igual o mayor que cero.",
                )
                return

            # Se evita registrar un código que ya identifica otro producto.
            if obtener_producto_por_item(item):
                QMessageBox.critical(
                    self,
                    "Código duplicado",
                    f"El código {item} ya está registrado en el catálogo.",
                )
                return

            guardar_producto_db(item, nombre, precio, stock, dept_nombre)
        else:
            # La edición de datos comerciales no cambia las existencias actuales.
            prod_antiguo = obtener_producto_por_item(item)
            actualizar_producto_db(item, nombre, precio, prod_antiguo[3], dept_nombre)

        self.accept()


class CatalogoWidget(QWidget):
    """Pantalla para consultar y administrar el catálogo de productos."""

    def __init__(self):
        """Construye la pantalla del catálogo y carga los productos actuales."""
        super().__init__()
        self.init_ui()
        self.cargar_datos()

    def showEvent(self, event):
        """Actualiza el catálogo cuando la sección vuelve a mostrarse."""
        super().showEvent(event)
        self.cargar_datos()

    def init_ui(self):
        """Construye la búsqueda, los controles de inventario y la tabla."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f6f9; color: #212529; font-family: 'Segoe UI', sans-serif;
            }
            QLabel#titulo_modulo {
                font-size: 22px; font-weight: bold; color: #0b2545;
            }
            QLineEdit, QComboBox {
                background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 8px; font-size: 13px; color: #0f172a;
            }
            QTableWidget {
                background-color: #ffffff; border-radius: 8px; border: 1px solid #cbd5e1;
            }
            QHeaderView::section {
                background-color: #004b87; color: #ffffff; font-weight: bold; padding: 6px; border: none;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        lbl_titulo = QLabel("Catálogo de Productos")
        lbl_titulo.setObjectName("titulo_modulo")
        layout.addWidget(lbl_titulo)

        # La barra superior permite buscar rápidamente un código de producto.
        top_bar = QFrame()
        top_bar.setStyleSheet("background-color: #ffffff; border-radius: 8px; border: 1px solid #cbd5e1;")
        tb_layout = QHBoxLayout(top_bar)
        tb_layout.setContentsMargins(15, 12, 15, 12)

        lbl_busq = QLabel("Buscar por código:")
        lbl_busq.setStyleSheet("font-weight: bold; color: #1e293b;")

        self.txt_busqueda_item = QLineEdit()
        self.txt_busqueda_item.setPlaceholderText("Ingrese un código de 6 dígitos")
        self.txt_busqueda_item.setFixedWidth(200)

        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_buscar.setStyleSheet("""
            QPushButton { background-color: #0071dc; color: #ffffff; font-weight: bold; padding: 8px 14px; border-radius: 6px; border: none; }
            QPushButton:hover { background-color: #005bb5; }
        """)
        self.btn_buscar.clicked.connect(self.ejecutar_busqueda_item)

        self.btn_mostrar_todos = QPushButton("Mostrar todo")
        self.btn_mostrar_todos.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mostrar_todos.setStyleSheet("""
            QPushButton { background-color: #64748b; color: #ffffff; font-weight: bold; padding: 8px 14px; border-radius: 6px; border: none; }
            QPushButton:hover { background-color: #475569; }
        """)
        self.btn_mostrar_todos.clicked.connect(self.cargar_datos)

        tb_layout.addWidget(lbl_busq)
        tb_layout.addWidget(self.txt_busqueda_item)
        tb_layout.addWidget(self.btn_buscar)
        tb_layout.addWidget(self.btn_mostrar_todos)
        tb_layout.addStretch()
        layout.addWidget(top_bar)

        # Los botones permiten crear, editar, ajustar existencias o eliminar productos.
        btn_layout = QHBoxLayout()

        self.btn_nuevo = QPushButton("Agregar producto")
        self.btn_nuevo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_nuevo.setStyleSheet("""
            QPushButton { background-color: #16a34a; color: #ffffff; font-weight: bold; padding: 9px 14px; border-radius: 6px; border: none; }
            QPushButton:hover { background-color: #15803d; }
        """)
        self.btn_nuevo.clicked.connect(self.abrir_crear_producto)

        self.btn_editar = QPushButton("Editar producto")
        self.btn_editar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_editar.setStyleSheet("""
            QPushButton { background-color: #0284c7; color: #ffffff; font-weight: bold; padding: 9px 14px; border-radius: 6px; border: none; }
            QPushButton:hover { background-color: #0369a1; }
        """)
        self.btn_editar.clicked.connect(self.editar_por_busqueda)

        self.btn_stock = QPushButton("Editar inventario")
        self.btn_stock.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stock.setStyleSheet("""
            QPushButton { background-color: #9333ea; color: #ffffff; font-weight: bold; padding: 9px 14px; border-radius: 6px; border: none; }
            QPushButton:hover { background-color: #7e22ce; }
        """)
        self.btn_stock.clicked.connect(self.gestionar_editar_stock)

        self.btn_eliminar = QPushButton("Eliminar producto")
        self.btn_eliminar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_eliminar.setStyleSheet("""
            QPushButton { background-color: #dc2626; color: #ffffff; font-weight: bold; padding: 9px 14px; border-radius: 6px; border: none; }
            QPushButton:hover { background-color: #b91c1c; }
        """)
        self.btn_eliminar.clicked.connect(self.eliminar_por_busqueda)

        btn_layout.addWidget(self.btn_nuevo)
        btn_layout.addWidget(self.btn_editar)
        btn_layout.addWidget(self.btn_stock)
        btn_layout.addWidget(self.btn_eliminar)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # La tabla presenta los datos principales de cada producto.
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["Código", "Nombre del producto", "Precio unitario (Q)", "Unidades", "Departamento"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabla)

    def cargar_datos(self):
        """Carga todos los productos y restablece el campo de búsqueda."""
        self.txt_busqueda_item.clear()
        productos = cargar_productos_db()
        self.poblar_tabla(productos)

    def poblar_tabla(self, productos):
        """Muestra en la tabla los registros recibidos desde la base de datos."""
        self.tabla.setRowCount(len(productos))
        # Cada producto se convierte en una fila con sus cinco columnas.
        for idx, p in enumerate(productos):
            self.tabla.setItem(idx, 0, QTableWidgetItem(str(p[0])))
            self.tabla.setItem(idx, 1, QTableWidgetItem(str(p[1])))
            self.tabla.setItem(idx, 2, QTableWidgetItem(f"Q{p[2]:.2f}"))
            self.tabla.setItem(idx, 3, QTableWidgetItem(str(p[3])))
            self.tabla.setItem(idx, 4, QTableWidgetItem(str(p[4])))

    def ejecutar_busqueda_item(self):
        """Busca el producto por código y muestra un mensaje si no existe."""
        item_buscado = self.txt_busqueda_item.text().strip()
        # No se consulta la base de datos hasta recibir un código.
        if not item_buscado:
            QMessageBox.warning(self, "Código requerido", "Ingrese un código de producto para realizar la búsqueda.")
            return

        prod = obtener_producto_por_item(item_buscado)
        # Un resultado válido se muestra solo; si no existe, se informa al usuario.
        if prod:
            self.poblar_tabla([prod])
        else:
            QMessageBox.critical(self, "Producto no encontrado", f"El código {item_buscado} no existe en el catálogo.")
            self.cargar_datos()

    def abrir_crear_producto(self):
        """Abre el formulario de alta y actualiza la lista si se guarda."""
        dialogo = DialogoGestionProducto(parent=self)
        # Solo se recarga el catálogo cuando se confirmó el registro.
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            self.cargar_datos()
            QMessageBox.information(self, "Registro completado", "El producto se agregó correctamente al catálogo.")

    def editar_por_busqueda(self):
        """Solicita un código, abre su formulario y guarda los cambios confirmados."""
        item, ok = QInputDialog.getText(self, "Editar producto", "Ingrese el código del producto (6 dígitos):")
        # Si se cancela el cuadro o se deja vacío, no se modifica ningún producto.
        if ok and item.strip():
            prod = obtener_producto_por_item(item.strip())
            # El formulario de edición solo se abre si existe ese producto.
            if prod:
                dialogo = DialogoGestionProducto(producto=prod, parent=self)
                # Se actualiza la tabla solo si el diálogo confirmó los cambios.
                if dialogo.exec() == QDialog.DialogCode.Accepted:
                    self.cargar_datos()
                    QMessageBox.information(self, "Actualización completada", "El producto se actualizó correctamente.")
            else:
                QMessageBox.critical(self, "Producto no encontrado", f"El código {item.strip()} no existe en el sistema.")

    def gestionar_editar_stock(self):
        """Solicita un producto y actualiza sus existencias con un valor válido."""
        item, ok = QInputDialog.getText(self, "Editar inventario", "Ingrese el código del producto (6 dígitos):")
        # Solo se continúa cuando se confirmó un código no vacío.
        if ok and item.strip():
            prod = obtener_producto_por_item(item.strip())
            # No se solicita una cantidad si el código no corresponde a un producto.
            if prod:
                # Se muestra el inventario actual para ayudar a indicar el nuevo valor.
                nuevo_stock_str, ok_stock = QInputDialog.getText(
                    self, "Actualizar inventario",
                    f"Producto: {prod[1]}\nUnidades actuales: {prod[3]}\n\nIngrese la nueva cantidad:",
                )
                # La cantidad solo se valida después de confirmar el segundo cuadro.
                if ok_stock and nuevo_stock_str.strip():
                    # Se convierte el texto para rechazar valores no enteros.
                    try:
                        nuevo_stock = int(nuevo_stock_str.strip())
                        # Se rechazan cantidades negativas antes de actualizar la base.
                        if nuevo_stock < 0:
                            raise ValueError

                        actualizar_stock_producto_db(prod[0], nuevo_stock)
                        self.cargar_datos()
                        QMessageBox.information(self, "Inventario actualizado", f"El producto [{prod[0]}] ahora tiene {nuevo_stock} unidades.")
                    except ValueError:
                        QMessageBox.critical(self, "Cantidad no válida", "Ingrese un número entero igual o mayor que cero.")
            else:
                QMessageBox.critical(self, "Producto no encontrado", f"El código {item.strip()} no existe en el sistema.")

    def eliminar_por_busqueda(self):
        """Pide confirmación antes de eliminar el producto buscado."""
        item, ok = QInputDialog.getText(self, "Eliminar producto", "Ingrese el código del producto (6 dígitos):")
        # Si el usuario cancela o deja vacío el código, no se inicia la búsqueda.
        if ok and item.strip():
            prod = obtener_producto_por_item(item.strip())
            # El diálogo de confirmación solo se presenta para códigos existentes.
            if prod:
                resp = QMessageBox.question(
                    self, "Confirmar eliminación",
                    f"¿Confirma la eliminación del producto [{prod[0]}] {prod[1]}?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                # La eliminación permanente requiere la confirmación explícita.
                if resp == QMessageBox.StandardButton.Yes:
                    eliminar_producto_db(prod[0])
                    self.cargar_datos()
                    QMessageBox.information(self, "Eliminación completada", "El producto se eliminó correctamente del sistema.")
            else:
                QMessageBox.critical(self, "Producto no encontrado", f"El código {item.strip()} no existe en el sistema.")
