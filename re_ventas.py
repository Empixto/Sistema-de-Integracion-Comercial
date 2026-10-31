from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QGridLayout, QInputDialog
)
from PySide6.QtCore import Qt
from datetime import datetime
import uuid
from database import guardar_venta_db, cargar_ventas_db, cargar_clientes_db, caja_esta_cerrada, obtener_producto_por_item

class VentasWidget(QWidget):
    """Módulo avanzado de ventas con carrito múltiple y agrupación de productos en celda."""
    def __init__(self):
        """Inicializa el carrito y carga la pantalla de ventas."""
        super().__init__()
        self.cliente_actual = None
        self.tipo_cliente_actual = "Regular"
        self.carrito_items = []

        self.init_ui()
        self.cargar_datos_tabla_recientes()

    def showEvent(self, event):
        """Actualiza el historial al volver a mostrar el módulo."""
        super().showEvent(event)
        self.cargar_datos_tabla_recientes()

    def init_ui(self):
        """Construye el formulario de venta, el carrito y el historial."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f6f9; color: #212529; font-family: 'Segoe UI', sans-serif;
            }
            QLabel#titulo_modulo {
                font-size: 22px; font-weight: bold; color: #0b2545;
            }
            QFrame#tarjeta_seccion {
                background-color: #ffffff; border-radius: 8px; border: 1px solid #cbd5e1;
            }
            QLabel.etiqueta_campo {
                color: #1e293b; font-size: 13px; font-weight: 600;
            }
            QLineEdit, QComboBox {
                background-color: #ffffff; border: 1px solid #94a3b8; border-radius: 6px; padding: 7px 10px; font-size: 13px; color: #0f172a;
            }
            QLineEdit:focus, QComboBox:focus { border: 2px solid #0071dc; }
            QPushButton#btn_accion {
                background-color: #0071dc; color: #ffffff; font-weight: bold; border-radius: 6px; padding: 8px 14px; border: none;
            }
            QPushButton#btn_accion:hover { background-color: #005bb5; }
            QPushButton#btn_registrar {
                background-color: #16a34a; color: #ffffff; font-size: 14px; font-weight: bold; border-radius: 6px; padding: 10px; border: none;
            }
            QPushButton#btn_registrar:hover { background-color: #15803d; }
            QPushButton#btn_quitar {
                background-color: #dc2626; color: #ffffff; font-weight: bold; border-radius: 6px; padding: 6px 10px; border: none;
            }
            QPushButton#btn_quitar:hover { background-color: #b91c1c; }
            QTableWidget {
                background-color: #ffffff; border-radius: 8px; border: 1px solid #cbd5e1;
            }
            QHeaderView::section {
                background-color: #004b87; color: #ffffff; font-weight: bold; padding: 6px; border: none;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        lbl_titulo = QLabel("Registro y Facturación de Ventas")
        lbl_titulo.setObjectName("titulo_modulo")
        layout.addWidget(lbl_titulo)

        # La primera sección identifica al cliente y establece la fecha de venta.
        cli_frame = QFrame()
        cli_frame.setObjectName("tarjeta_seccion")
        c_layout = QHBoxLayout(cli_frame)
        c_layout.setContentsMargins(15, 12, 15, 12)

        lbl_c = QLabel("Buscar Cliente:")
        lbl_c.setProperty("class", "etiqueta_campo")
        self.txt_cliente_busqueda = QLineEdit()
        self.txt_cliente_busqueda.setPlaceholderText("Ingrese el nombre del cliente")

        self.btn_buscar_cli = QPushButton("Buscar")
        self.btn_buscar_cli.setObjectName("btn_accion")
        self.btn_buscar_cli.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_buscar_cli.clicked.connect(self.buscar_cliente)

        self.lbl_cliente_info = QLabel("Cliente: No seleccionado")
        self.lbl_cliente_info.setStyleSheet("font-weight: bold; color: #0284c7;")

        lbl_f = QLabel("Fecha (AAAA-MM-DD):")
        lbl_f.setProperty("class", "etiqueta_campo")
        self.txt_fecha = QLineEdit()
        self.txt_fecha.setText(datetime.now().strftime("%Y-%m-%d"))
        self.txt_fecha.setFixedWidth(110)

        c_layout.addWidget(lbl_c)
        c_layout.addWidget(self.txt_cliente_busqueda, 1)
        c_layout.addWidget(self.btn_buscar_cli)
        c_layout.addWidget(self.lbl_cliente_info, 1)
        c_layout.addWidget(lbl_f)
        c_layout.addWidget(self.txt_fecha)
        layout.addWidget(cli_frame)

        # La segunda sección busca productos y permite administrar el carrito.
        prod_frame = QFrame()
        prod_frame.setObjectName("tarjeta_seccion")
        p_layout = QHBoxLayout(prod_frame)
        p_layout.setContentsMargins(15, 12, 15, 12)

        lbl_i = QLabel("Código del producto:")
        lbl_i.setProperty("class", "etiqueta_campo")
        self.txt_item = QLineEdit()
        self.txt_item.setPlaceholderText("Ejemplo: 754821")
        self.txt_item.setFixedWidth(130)

        self.btn_agregar_prod = QPushButton("Buscar y Añadir al Carrito")
        self.btn_agregar_prod.setObjectName("btn_accion")
        self.btn_agregar_prod.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_agregar_prod.clicked.connect(self.agregar_producto_carrito)

        self.btn_quitar_prod = QPushButton("Quitar producto seleccionado")
        self.btn_quitar_prod.setObjectName("btn_quitar")
        self.btn_quitar_prod.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_quitar_prod.clicked.connect(self.quitar_producto_carrito)

        p_layout.addWidget(lbl_i)
        p_layout.addWidget(self.txt_item)
        p_layout.addWidget(self.btn_agregar_prod)
        p_layout.addWidget(self.btn_quitar_prod)
        p_layout.addStretch()
        layout.addWidget(prod_frame)

        self.tabla_carrito = QTableWidget()
        self.tabla_carrito.setColumnCount(5)
        self.tabla_carrito.setHorizontalHeaderLabels(["Item", "Descripción", "Cant.", "Precio Unit. (Q)", "Subtotal (Q)"])
        self.tabla_carrito.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_carrito.setMaximumHeight(150)
        layout.addWidget(self.tabla_carrito)

        # El resumen y el pago muestran los importes antes de registrar la venta.
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)

        resumen_frame = QFrame()
        resumen_frame.setObjectName("tarjeta_seccion")
        r_layout = QVBoxLayout(resumen_frame)
        r_layout.setContentsMargins(15, 12, 15, 12)
        r_layout.setSpacing(6)

        lbl_res_titulo = QLabel("Resumen financiero de la venta")
        lbl_res_titulo.setStyleSheet("font-size: 14px; font-weight: bold; color: #0b2545;")

        self.lbl_subtotal_pre = QLabel("Subtotal: Q0.00")
        self.lbl_descuento_pre = QLabel("Descuento: Q0.00 (0.0%)")
        self.lbl_recargo_pre = QLabel("Recargo Tarjeta: Q0.00")
        self.lbl_total_pre = QLabel("Total a Pagar: Q0.00")
        self.lbl_total_pre.setStyleSheet("font-size: 16px; font-weight: bold; color: #16a34a;")

        r_layout.addWidget(lbl_res_titulo)
        r_layout.addWidget(self.lbl_subtotal_pre)
        r_layout.addWidget(self.lbl_descuento_pre)
        r_layout.addWidget(self.lbl_recargo_pre)
        r_layout.addWidget(self.lbl_total_pre)
        bottom_layout.addWidget(resumen_frame, 1)

        pago_frame = QFrame()
        pago_frame.setObjectName("tarjeta_seccion")
        pg_layout = QGridLayout(pago_frame)
        pg_layout.setContentsMargins(15, 12, 15, 12)
        pg_layout.setSpacing(10)

        lbl_pago = QLabel("Método de pago:"); lbl_pago.setProperty("class", "etiqueta_campo")
        self.cmb_pago = QComboBox()
        self.cmb_pago.addItems(["Efectivo", "Tarjeta", "Transferencia"])
        self.cmb_pago.currentIndexChanged.connect(self.actualizar_calculos_pre_venta)
        # Al cambiar de medio de pago también se habilita o deshabilita el campo de efectivo.
        self.cmb_pago.currentIndexChanged.connect(self.verificar_metodo_pago)

        lbl_efec = QLabel("Efectivo Recibido (Q):"); lbl_efec.setProperty("class", "etiqueta_campo")
        self.txt_efectivo = QLineEdit()
        self.txt_efectivo.setPlaceholderText("Monto recibido en efectivo")

        btn_registrar = QPushButton("Procesar Venta y Facturar")
        btn_registrar.setObjectName("btn_registrar")
        btn_registrar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_registrar.clicked.connect(self.procesar_venta)

        pg_layout.addWidget(lbl_pago, 0, 0); pg_layout.addWidget(self.cmb_pago, 0, 1)
        pg_layout.addWidget(lbl_efec, 1, 0); pg_layout.addWidget(self.txt_efectivo, 1, 1)
        pg_layout.addWidget(btn_registrar, 2, 0, 1, 2)
        bottom_layout.addWidget(pago_frame, 1)

        layout.addLayout(bottom_layout)

        # El historial presenta una fila por cada ticket, no por producto.
        lbl_sub_recientes = QLabel("Historial de Transacciones (Agrupadas)")
        lbl_sub_recientes.setStyleSheet("font-size: 14px; font-weight: bold; color: #0b2545; margin-top: 5px;")
        layout.addWidget(lbl_sub_recientes)

        self.tabla_recientes = QTableWidget()
        self.tabla_recientes.setColumnCount(5)
        self.tabla_recientes.setHorizontalHeaderLabels(["Fecha", "Cliente", "Productos Adquiridos", "Método Pago", "Total Facturado (Q)"])
        self.tabla_recientes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_recientes.setMaximumHeight(150)
        layout.addWidget(self.tabla_recientes)

        self.verificar_metodo_pago()

    def buscar_cliente(self):
        """Busca el cliente por nombre y actualiza sus datos para la venta."""
        nombre_busq = self.txt_cliente_busqueda.text().strip().lower()
        # No se buscan registros si no se escribió un nombre.
        if not nombre_busq:
            QMessageBox.warning(self, "Nombre requerido", "Ingrese el nombre del cliente.")
            return

        clientes = cargar_clientes_db()
        encontrado = None
        # La comparación no distingue mayúsculas para facilitar la búsqueda.
        for c in clientes:
            # Se termina el recorrido en cuanto se encuentra la coincidencia.
            if c[1].lower() == nombre_busq:
                encontrado = c
                break

        # Se guarda el cliente seleccionado o se limpia el estado si no existe.
        if encontrado:
            self.cliente_actual = encontrado[1]
            self.tipo_cliente_actual = encontrado[3]
            self.lbl_cliente_info.setText(f"Cliente: {self.cliente_actual} ({self.tipo_cliente_actual})")
            self.actualizar_calculos_pre_venta()
        else:
            QMessageBox.critical(self, "Cliente no encontrado", f"No se encontró al cliente «{self.txt_cliente_busqueda.text().strip()}».")
            self.cliente_actual = None
            self.lbl_cliente_info.setText("Cliente: No seleccionado")

    def agregar_producto_carrito(self):
        """Busca un producto, solicita la cantidad y lo agrega al carrito."""
        item_code = self.txt_item.text().strip()
        # Un código es obligatorio para identificar el producto.
        if not item_code:
            QMessageBox.warning(self, "Código requerido", "Ingrese el código del producto.")
            return

        prod = obtener_producto_por_item(item_code)
        # Sin coincidencia no se debe pedir una cantidad ni cambiar el carrito.
        if not prod:
            QMessageBox.critical(self, "Producto no encontrado", f"El código {item_code} no existe.")
            return

        # El cuadro limita la cantidad a las existencias disponibles.
        cantidad, ok = QInputDialog.getInt(self, "Cantidad", f"Artículo: {prod[1]}\nStock: {prod[3]}\n\nIngrese cantidad:", 1, 1, prod[3])
        # Si se cancela la selección, el carrito permanece sin cambios.
        if not ok:
            return

        # Se conserva el precio actual para mantener el cálculo de esta venta.
        self.carrito_items.append({
            "item": prod[0], "nombre": prod[1], "precio": prod[2],
            "cantidad": cantidad, "subtotal": prod[2] * cantidad
        })
        self.txt_item.clear()
        self.actualizar_tabla_carrito()
        self.actualizar_calculos_pre_venta()

    def quitar_producto_carrito(self):
        """Elimina del carrito la fila seleccionada, si existe."""
        fila = self.tabla_carrito.currentRow()
        # Sin una fila seleccionada no hay ningún elemento que eliminar.
        if fila < 0:
            return
        del self.carrito_items[fila]
        self.actualizar_tabla_carrito()
        self.actualizar_calculos_pre_venta()

    def actualizar_tabla_carrito(self):
        """Dibuja nuevamente las filas del carrito con sus subtotales."""
        self.tabla_carrito.setRowCount(len(self.carrito_items))
        # Cada producto del carrito ocupa una fila con cantidad y precio.
        for idx, item in enumerate(self.carrito_items):
            self.tabla_carrito.setItem(idx, 0, QTableWidgetItem(item["item"]))
            self.tabla_carrito.setItem(idx, 1, QTableWidgetItem(item["nombre"]))
            self.tabla_carrito.setItem(idx, 2, QTableWidgetItem(str(item["cantidad"])))
            self.tabla_carrito.setItem(idx, 3, QTableWidgetItem(f"Q{item['precio']:.2f}"))
            self.tabla_carrito.setItem(idx, 4, QTableWidgetItem(f"Q{item['subtotal']:.2f}"))

    def calcular_totales_financieros(self):
        """Calcula el subtotal, descuento por cliente y recargo por tarjeta."""
        sub = sum(i["subtotal"] for i in self.carrito_items)
        porc = 0.0
        # El porcentaje de descuento depende de la categoría y del subtotal.
        if self.tipo_cliente_actual == "Regular":
            # El cliente regular obtiene un descuento según el rango de compra.
            if sub >= 1500 and sub <= 3999.99: porc = 0.05
            # En compras de mayor valor se aplica el porcentaje superior.
            elif sub >= 4000: porc = 0.08
        # La categoría frecuente tiene porcentajes propios para cada rango.
        elif self.tipo_cliente_actual == "Frecuente":
            # Las compras menores reciben el descuento inicial de esta categoría.
            if sub < 1500: porc = 0.05
            # El importe intermedio usa un porcentaje mayor.
            elif sub <= 3999.99: porc = 0.10
            else: porc = 0.15
        # La categoría corporativa usa límites de compra más altos.
        elif self.tipo_cliente_actual == "Corporativo":
            # Se aplica el primer porcentaje para compras menores al umbral.
            if sub < 4000: porc = 0.10
            # El intervalo intermedio obtiene el segundo porcentaje.
            elif sub <= 7999.99: porc = 0.15
            else: porc = 0.20

        # El recargo de tarjeta se aplica después del descuento.
        desc = sub * porc
        sub_desc = sub - desc
        rec = sub_desc * 0.02 if self.cmb_pago.currentText() == "Tarjeta" else 0.0
        return sub, desc, porc, rec, sub_desc + rec

    def actualizar_calculos_pre_venta(self):
        """Refleja en pantalla los totales que se pagarían en ese momento."""
        sub, desc, porc, rec, tot = self.calcular_totales_financieros()
        self.lbl_subtotal_pre.setText(f"Subtotal: Q{sub:.2f}")
        self.lbl_descuento_pre.setText(f"Descuento: Q{desc:.2f} ({porc*100:.1f}%)")
        self.lbl_recargo_pre.setText(f"Recargo Tarjeta: Q{rec:.2f}")
        self.lbl_total_pre.setText(f"Total a Pagar: Q{tot:.2f}")

    def verificar_metodo_pago(self):
        """Permite escribir efectivo recibido solo al pagar en efectivo."""
        # El campo solo se habilita cuando la forma de pago es efectivo.
        if self.cmb_pago.currentText() == "Efectivo":
            self.txt_efectivo.setEnabled(True)
            self.txt_efectivo.setStyleSheet("background-color: #ffffff;")
        else:
            self.txt_efectivo.setEnabled(False)
            self.txt_efectivo.clear()
            self.txt_efectivo.setStyleSheet("background-color: #e2e8f0;")

    def cargar_datos_tabla_recientes(self):
        """Agrupa las líneas registradas y actualiza el historial de tickets."""
        registros = cargar_ventas_db()

        # Se combinan las líneas con el mismo identificador de transacción.
        agrupadas = {}
        # Los datos comunes de cada ticket se guardan una sola vez.
        for reg in registros:
            # reg: id(0), grupo(1), cliente(2), producto(3), cant(4), prec(5), tot(6), metodo(7), fecha(8), ...
            g_id = reg[1]
            # El primer producto de un ticket crea su resumen acumulado.
            if g_id not in agrupadas:
                agrupadas[g_id] = {
                    "fecha": reg[8],
                    "cliente": reg[2],
                    "metodo": reg[7],
                    "productos": [],
                    "total_ticket": 0.0
                }
            agrupadas[g_id]["productos"].append(f"- {reg[3]} (Cantidad: {reg[4]})")
            agrupadas[g_id]["total_ticket"] += reg[6]

        lista_final = list(agrupadas.values())
        self.tabla_recientes.setRowCount(len(lista_final))
        # Cada ticket agrupado se muestra en una fila del historial.
        for idx, item in enumerate(lista_final):
            prod_texto = "\n".join(item["productos"])
            self.tabla_recientes.setItem(idx, 0, QTableWidgetItem(item["fecha"]))
            self.tabla_recientes.setItem(idx, 1, QTableWidgetItem(item["cliente"]))
            self.tabla_recientes.setItem(idx, 2, QTableWidgetItem(prod_texto))
            self.tabla_recientes.setItem(idx, 3, QTableWidgetItem(item["metodo"]))
            self.tabla_recientes.setItem(idx, 4, QTableWidgetItem(f"Q{item['total_ticket']:.2f}"))

    def procesar_venta(self):
        """Valida la operación, guarda sus productos y presenta la factura."""
        fecha_venta = self.txt_fecha.text().strip()
        # Se valida la fecha antes de permitir cualquier registro de venta.
        try:
            # La fecha se verifica antes de consultar el estado de la caja.
            datetime.strptime(fecha_venta, "%Y-%m-%d")
        except ValueError:
            QMessageBox.warning(self, "Fecha no válida", "Ingrese la fecha con el formato AAAA-MM-DD.")
            return

        # Una caja cerrada no debe aceptar transacciones nuevas.
        if caja_esta_cerrada(fecha_venta):
            QMessageBox.critical(self, "Caja cerrada", f"La caja del {fecha_venta} está cerrada. No se permiten nuevas ventas.")
            return

        # La venta debe estar asociada a un cliente válido.
        if not self.cliente_actual:
            QMessageBox.warning(self, "Cliente requerido", "Seleccione un cliente válido.")
            return

        # No se puede facturar un carrito sin productos.
        if not self.carrito_items:
            QMessageBox.warning(self, "Carrito vacío", "Agregue al menos un producto antes de procesar la venta.")
            return

        subtotal, descuento, _, recargo, total_compra = self.calcular_totales_financieros()
        metodo_pago = self.cmb_pago.currentText()

        monto_recibido = 0.0
        cambio = 0.0
        # El efectivo recibido debe cubrir el total de la compra.
        if metodo_pago == "Efectivo":
            efectivo_str = self.txt_efectivo.text().strip()
            # Se exige un importe para calcular si hace falta cambio.
            if not efectivo_str:
                QMessageBox.warning(self, "Dato requerido", "Ingrese el monto de efectivo recibido.")
                return
            # El importe recibido debe poder convertirse a un número.
            try:
                monto_recibido = float(efectivo_str)
            except ValueError:
                QMessageBox.warning(self, "Monto no válido", "Ingrese un monto numérico válido.")
                return

            # Se solicita el monto faltante hasta cubrir el total o cancelar la operación.
            while monto_recibido < total_compra:
                faltante = total_compra - monto_recibido
                nuevo_monto_str, ok = QInputDialog.getText(
                    self, "Efectivo Insuficiente",
                    f"Total: Q{total_compra:.2f}\nIngresado: Q{monto_recibido:.2f}\nFaltante: Q{faltante:.2f}\n\nIngrese cantidad faltante:"
                )
                # Cancelar el cuadro detiene la venta sin guardar el ticket.
                if not ok:
                    return
                # El importe adicional se procesa solo si contiene texto.
                if nuevo_monto_str.strip():
                    # Se valida que el valor ingresado sea numérico.
                    try:
                        monto_adicional = float(nuevo_monto_str.strip())
                        # Un incremento debe ser positivo para avanzar hacia el total.
                        if monto_adicional <= 0:
                            raise ValueError
                        monto_recibido += monto_adicional
                    except ValueError:
                        QMessageBox.warning(
                            self,
                            "Monto no válido",
                            "Ingrese un monto numérico mayor que cero.",
                        )
                else:
                    QMessageBox.warning(
                        self,
                        "Dato requerido",
                        "Ingrese el monto adicional para completar el pago.",
                    )
            cambio = monto_recibido - total_compra

        # Todas las líneas del carrito comparten un identificador de ticket.
        grupo_id = str(uuid.uuid4())
        nombre_cli_factura = self.cliente_actual

        # Se conserva una copia para preparar la factura antes de limpiar el formulario.
        items_factura = list(self.carrito_items)

        num_items = len(self.carrito_items)
        # El descuento y recargo generales se distribuyen entre las líneas guardadas.
        for item in self.carrito_items:
            guardar_venta_db(
                grupo_id,
                nombre_cli_factura,
                item["nombre"],
                item["cantidad"],
                item["precio"],
                item["subtotal"],
                descuento / num_items,
                recargo / num_items,
                metodo_pago,
                item["subtotal"] - (descuento / num_items) + (recargo / num_items),
                fecha_venta
            )

        self.cargar_datos_tabla_recientes()

        # Se limpia el formulario después de guardar todas las líneas de la venta.
        self.carrito_items = []
        self.actualizar_tabla_carrito()
        self.txt_cliente_busqueda.clear()
        self.cliente_actual = None
        self.lbl_cliente_info.setText("Cliente: No seleccionado")
        self.txt_efectivo.clear()
        self.actualizar_calculos_pre_venta()

        # La copia permite generar la factura aunque el carrito ya esté vacío.
        prod_factura = "\n".join([f"  - {i['nombre']} (Cant: {i['cantidad']}) - Q{i['subtotal']:.2f}" for i in items_factura])

        resumen = (
            f"--------------------------------------------------\n"
            f"FACTURA ELECTRÓNICA GENERADA ({fecha_venta})\n"
            f"--------------------------------------------------\n"
            f"Cliente: {nombre_cli_factura}\n"
            f"Productos:\n{prod_factura}\n"
            f"--------------------------------------------------\n"
            f"Subtotal:           Q{subtotal:.2f}\n"
            f"Descuento:          Q{descuento:.2f}\n"
            f"Recargo:            Q{recargo:.2f}\n"
            f"Total Facturado:    Q{total_compra:.2f}\n"
            f"Método de Pago:     {metodo_pago}\n"
        )
        # Solo las compras en efectivo incluyen recibido y cambio en la factura.
        if metodo_pago == "Efectivo":
            resumen += f"Efectivo Recibido:  Q{monto_recibido:.2f}\n"
            resumen += f"Cambio devuelto:    Q{cambio:.2f}\n"
        resumen += f"--------------------------------------------------"

        QMessageBox.information(self, "Venta completada", resumen)
