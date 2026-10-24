from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QGridLayout, QInputDialog
)
from PySide6.QtCore import Qt
from datetime import datetime
from database import guardar_venta_db, cargar_ventas_db, cargar_clientes_db, caja_esta_cerrada

# Pantalla para registrar ventas, calcular descuentos y generar facturas.
class VentasWidget(QWidget):
    def __init__(self):
        # Prepara la pantalla y carga los datos guardados.
        super().__init__()
        self.init_ui()
        self.cargar_datos_iniciales()

    def showEvent(self, event):
        # Actualiza la tabla y la lista de clientes al abrir la pantalla.
        super().showEvent(event)
        self.cargar_datos_iniciales()
        self.actualizar_combo_clientes()

    def init_ui(self):
        # Configura el estilo y los controles de la pantalla.
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f6f9;
                color: #212529;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#titulo_modulo {
                font-size: 22px;
                font-weight: bold;
                color: #0b2545;
            }
            QFrame#tarjeta_form {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #cbd5e1;
            }
            QLabel.etiqueta_campo {
                color: #1e293b;
                font-size: 13px;
                font-weight: 600;
            }
            QLineEdit, QComboBox {
                background-color: #ffffff;
                border: 1px solid #94a3b8;
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 13px;
                color: #0f172a;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #0071dc;
            }
            QPushButton#btn_registrar {
                background-color: #ff9900;
                color: #11111b;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                padding: 10px;
                border: none;
            }
            QPushButton#btn_registrar:hover {
                background-color: #e88b00;
            }
            QTableWidget {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #cbd5e1;
            }
            QHeaderView::section {
                background-color: #004b87;
                color: #ffffff;
                font-weight: bold;
                padding: 6px;
                border: none;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título y formulario para ingresar los datos de la venta.
        lbl_titulo = QLabel("Registro y Facturación de Ventas")
        lbl_titulo.setObjectName("titulo_modulo")
        layout.addWidget(lbl_titulo)

        form_frame = QFrame()
        form_frame.setObjectName("tarjeta_form")
        grid = QGridLayout(form_frame)
        grid.setContentsMargins(15, 15, 15, 15)
        grid.setSpacing(10)

        lbl_cli = QLabel("Cliente:"); lbl_cli.setProperty("class", "etiqueta_campo")
        self.cmb_cliente = QComboBox()
        self.actualizar_combo_clientes()

        lbl_prod = QLabel("Descripción del Producto:"); lbl_prod.setProperty("class", "etiqueta_campo")
        self.txt_producto = QLineEdit()
        self.txt_producto.setPlaceholderText("Ejemplo: laptop empresarial")

        lbl_cant = QLabel("Cantidad:"); lbl_cant.setProperty("class", "etiqueta_campo")
        self.txt_cantidad = QLineEdit()
        self.txt_cantidad.setPlaceholderText("Ejemplo: 4")

        lbl_prec = QLabel("Precio unitario (Q):"); lbl_prec.setProperty("class", "etiqueta_campo")
        self.txt_precio = QLineEdit()
        self.txt_precio.setPlaceholderText("Ejemplo: 162.50")

        lbl_fec = QLabel("Fecha de venta (AAAA-MM-DD):"); lbl_fec.setProperty("class", "etiqueta_campo")
        self.txt_fecha = QLineEdit()
        self.txt_fecha.setText(datetime.now().strftime("%Y-%m-%d"))

        lbl_pago = QLabel("Método de Pago:"); lbl_pago.setProperty("class", "etiqueta_campo")
        self.cmb_pago = QComboBox()
        self.cmb_pago.addItems(["Efectivo", "Tarjeta", "Transferencia"])
        self.cmb_pago.currentIndexChanged.connect(self.verificar_metodo_pago)

        lbl_efec = QLabel("Efectivo recibido (Q):"); lbl_efec.setProperty("class", "etiqueta_campo")
        self.txt_efectivo = QLineEdit()
        self.txt_efectivo.setPlaceholderText("Ingrese el monto recibido")

        btn_guardar = QPushButton("Registrar venta y generar factura")
        btn_guardar.setObjectName("btn_registrar")
        btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_guardar.clicked.connect(self.procesar_venta)

        grid.addWidget(lbl_cli, 0, 0); grid.addWidget(self.cmb_cliente, 0, 1)
        grid.addWidget(lbl_prod, 0, 2); grid.addWidget(self.txt_producto, 0, 3)
        grid.addWidget(lbl_cant, 1, 0); grid.addWidget(self.txt_cantidad, 1, 1)
        grid.addWidget(lbl_prec, 1, 2); grid.addWidget(self.txt_precio, 1, 3)
        grid.addWidget(lbl_fec, 2, 0); grid.addWidget(self.txt_fecha, 2, 1)
        grid.addWidget(lbl_pago, 2, 2); grid.addWidget(self.cmb_pago, 2, 3)
        grid.addWidget(lbl_efec, 3, 0); grid.addWidget(self.txt_efectivo, 3, 1)
        grid.addWidget(btn_guardar, 4, 0, 1, 4)

        layout.addWidget(form_frame)

        # Tabla con las ventas registradas.
        lbl_sub_tabla = QLabel("Transacciones Recientes")
        lbl_sub_tabla.setStyleSheet("font-size: 15px; font-weight: bold; color: #0b2545;")
        layout.addWidget(lbl_sub_tabla)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels([
            "No.", "Fecha", "Cliente", "Producto", "Cantidad", "Método de pago", "Total facturado (Q)"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabla)
        
        self.verificar_metodo_pago()

    def actualizar_combo_clientes(self):
        # Carga los clientes registrados en el selector.
        self.cmb_cliente.clear()
        self.cmb_cliente.addItem("Seleccione Cliente...")
        self.clientes_datos = cargar_clientes_db()
        for c in self.clientes_datos:
            self.cmb_cliente.addItem(f"{c[1]} ({c[3]})")

    def verificar_metodo_pago(self):
        # Solicita efectivo recibido solo cuando el pago es en efectivo.
        if self.cmb_pago.currentText() == "Efectivo":
            self.txt_efectivo.setEnabled(True)
            self.txt_efectivo.setStyleSheet("background-color: #ffffff;")
        else:
            self.txt_efectivo.setEnabled(False)
            self.txt_efectivo.clear()
            self.txt_efectivo.setStyleSheet("background-color: #e2e8f0;")

    def cargar_datos_iniciales(self):
        # Actualiza la tabla con las ventas guardadas.
        registros = cargar_ventas_db()
        self.tabla.setRowCount(len(registros))
        for fila, venta in enumerate(registros):
            valores = (
                str(fila + 1), venta[7], venta[1], venta[2],
                str(venta[3]), venta[6], f"Q{venta[5]:.2f}"
            )
            for columna, valor in enumerate(valores):
                self.tabla.setItem(fila, columna, QTableWidgetItem(valor))

    def procesar_venta(self):
        # Valida los datos, calcula el total y guarda la venta.
        fecha_venta = self.txt_fecha.text().strip()
        
        try:
            datetime.strptime(fecha_venta, "%Y-%m-%d")
        except ValueError:
            QMessageBox.warning(self, "Fecha inválida", "Use el formato AAAA-MM-DD. Ejemplo: 2026-06-01.")
            return

        if caja_esta_cerrada(fecha_venta):
            QMessageBox.critical(self, "Caja cerrada", f"La caja del {fecha_venta} ya está cerrada.\nNo se pueden registrar ventas en esa fecha.")
            return

        index_cli = self.cmb_cliente.currentIndex()
        if index_cli <= 0:
            QMessageBox.warning(self, "Cliente requerido", "Seleccione un cliente registrado.")
            return

        cliente_seleccionado = self.clientes_datos[index_cli - 1]
        nombre_cliente = cliente_seleccionado[1]
        tipo_cliente = cliente_seleccionado[3]

        producto = self.txt_producto.text().strip()
        cant_str = self.txt_cantidad.text().strip()
        prec_str = self.txt_precio.text().strip()
        metodo_pago = self.cmb_pago.currentText()

        if not producto or not cant_str or not prec_str:
            QMessageBox.warning(self, "Datos incompletos", "Complete todos los campos obligatorios.")
            return

        if not any(caracter.isalpha() for caracter in producto):
            QMessageBox.warning(self, "Producto inválido", "La descripción debe incluir letras.")
            return

        if not cant_str.isdigit() or int(cant_str) <= 0:
            QMessageBox.warning(self, "Cantidad inválida", "Ingrese una cantidad entera mayor que cero.")
            return

        try:
            precio_unitario = float(prec_str)
            if precio_unitario <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Precio inválido", "Ingrese un precio unitario mayor que cero.")
            return

        cantidad = int(cant_str)
        subtotal = precio_unitario * cantidad

        porcentaje_descuento = 0.0
        if tipo_cliente == "Regular":
            porcentaje_descuento = 0.08 if subtotal > 499.99 else 0.05 if subtotal >= 200 else 0.0
        elif tipo_cliente == "Frecuente":
            porcentaje_descuento = 0.15 if subtotal > 499.99 else 0.10 if subtotal >= 200 else 0.05
        elif tipo_cliente == "Corporativo":
            porcentaje_descuento = 0.20 if subtotal > 999.99 else 0.15 if subtotal > 499.99 else 0.10

        descuento = subtotal * porcentaje_descuento
        subtotal_con_descuento = subtotal - descuento

        recargo = subtotal_con_descuento * 0.02 if metodo_pago == "Tarjeta" else 0.0
        total_compra = subtotal_con_descuento + recargo

        cambio = monto_recibido = 0.0
        if metodo_pago == "Efectivo":
            efectivo_str = self.txt_efectivo.text().strip()
            if not efectivo_str:
                QMessageBox.warning(self, "Monto requerido", "Ingrese el monto recibido en efectivo.")
                return
            try:
                monto_recibido = float(efectivo_str)
            except ValueError:
                QMessageBox.warning(self, "Monto inválido", "Ingrese un monto válido.")
                return

            while monto_recibido < total_compra:
                respuesta = QMessageBox.warning(
                    self,
                    "Efectivo insuficiente",
                    f"El monto recibido (Q{monto_recibido:.2f}) es menor que el total "
                    f"(Q{total_compra:.2f}).\n¿Desea ingresar otro monto?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                if respuesta == QMessageBox.StandardButton.Yes:
                    nuevo_valor, aceptado = QInputDialog.getDouble(
                        self, "Monto recibido", f"Total por pagar: Q{total_compra:.2f}\nIngrese el monto:",
                        monto_recibido, 0, 100000, 2
                    )
                    if not aceptado:
                        return
                    monto_recibido = nuevo_valor
                else:
                    return

            cambio = monto_recibido - total_compra

        guardar_venta_db(nombre_cliente, producto, cantidad, precio_unitario, subtotal, descuento, recargo, metodo_pago, total_compra, fecha_venta)
        self.cargar_datos_iniciales()

        self.cmb_cliente.setCurrentIndex(0)
        self.txt_producto.clear()
        self.txt_cantidad.clear()
        self.txt_precio.clear()
        self.txt_efectivo.clear()
        self.cmb_pago.setCurrentIndex(0)

        # Prepara el resumen de la compra en quetzales.
        resumen = (
            f"--------------------------------------------------\n"
            f"RESUMEN DE COMPRA ({fecha_venta})\n"
            f"--------------------------------------------------\n"
            f"Cliente: {nombre_cliente}\n"
            f"Tipo de cliente: {tipo_cliente}\n"
            f"Cantidad de productos: {cantidad}\n"
            f"Subtotal:           Q{subtotal:.2f}\n"
            f"Descuento:          Q{descuento:.2f}\n"
            f"Recargo:            Q{recargo:.2f}\n"
            f"Total:              Q{total_compra:.2f}\n"
            f"Forma de pago:      {metodo_pago}\n"
        )
        if metodo_pago == "Efectivo":
            resumen += f"Efectivo recibido:  Q{monto_recibido:.2f}\n"
            resumen += f"Cambio:             Q{cambio:.2f}\n"
        resumen += f"--------------------------------------------------"

        QMessageBox.information(self, "Factura Generada", resumen)