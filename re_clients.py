from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QGridLayout
)  # Incluye las piezas necesarias para crear formularios, tablas y avisos.
from PySide6.QtCore import Qt  # Permite alinear el contenido y cambiar el cursor.
from database import guardar_cliente_db, cargar_clientes_db, eliminar_cliente_db  # Incluye las acciones para guardar, mostrar y eliminar clientes.

class ClientesWidget(QWidget):
    """Pantalla para registrar, consultar y eliminar clientes."""

    # Permite registrar, consultar y eliminar clientes.
    def __init__(self):
        """Inicializa los datos y construye la pantalla de gestión de clientes."""
        # Prepara la pantalla de clientes.
        super().__init__()

        # Guarda los clientes y las cantidades por tipo.
        self.lista_clientes = []
        self.contador_total_clientes = 0
        self.contador_regulares = 0
        self.contador_frecuentes = 0
        self.contador_corporativos = 0

        self.init_ui()
        self.cargar_datos_iniciales()

    def showEvent(self, event):
        """Actualiza los datos cada vez que se muestra esta sección."""
        # Actualiza los datos al abrir esta pantalla.
        super().showEvent(event)
        self.cargar_datos_iniciales()

    def init_ui(self):
        """Crea el formulario, los indicadores, los filtros y la tabla."""
        # Crea el formulario, los contadores y la tabla de clientes.
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f6f9; /* Fondo gris claro. */
                color: #212529;            /* Texto oscuro para que se lea bien. */
                font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            }
            QLabel#module_title {
                font-size: 26px;
                font-weight: bold;
                color: #0b2545; /* Azul oscuro para el título. */
            }
            QFrame#form_card {
                background-color: #ffffff; /* Fondo blanco para los recuadros. */
                border-radius: 8px;
                border: 1px solid #cbd5e1;
            }
            QLabel.form_label {
                color: #1e293b;
                font-size: 14px;
                font-weight: 600;
            }
            QLineEdit, QComboBox {
                background-color: #ffffff;
                border: 1px solid #94a3b8;
                border-radius: 6px;
                padding: 10px 12px;
                color: #0f172a;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #0071dc; /* Resalta el espacio seleccionado. */
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #0f172a;
                selection-background-color: #0071dc;
                selection-color: #ffffff;
            }
            QPushButton#btn_guardar {
                background-color: #ff9900; /* Naranja para destacar el botón de registro. */
                color: #11111b;
                font-size: 15px;
                font-weight: bold;
                border-radius: 6px;
                padding: 12px;
                border: none;
            }
            QPushButton#btn_guardar:hover {
                background-color: #e88b00;
            }
            QPushButton#btn_eliminar {
                background-color: #dc2626; /* Rojo para destacar la acción de eliminar. */
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                padding: 10px 16px;
                border: none;
            }
            QPushButton#btn_eliminar:hover {
                background-color: #b91c1c;
            }
            QTableWidget {
                background-color: #ffffff;
                color: #0f172a;
                gridline-color: #e2e8f0;
                border-radius: 8px;
                border: 1px solid #cbd5e1;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #004b87; /* Azul para el encabezado de la tabla. */
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
                padding: 8px;
                border: 1px solid #003366;
            }
            QMessageBox {
                background-color: #ffffff;
            }
            QMessageBox QLabel {
                color: #0f172a;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: #0071dc;
                color: #ffffff;
                font-weight: bold;
                border-radius: 4px;
                padding: 6px 16px;
                min-width: 70px;
            }
            QMessageBox QPushButton:hover {
                background-color: #005bb5;
            }
        """)

        # Organiza el contenido de la pantalla.
        layout = QVBoxLayout(self)
        layout.setSpacing(18)

        # Título de la pantalla.
        lbl_title = QLabel("Registro y Gestión de Clientes")
        lbl_title.setObjectName("module_title")
        layout.addWidget(lbl_title)

        # Contadores de clientes por tipo.
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)

        # Crea una tarjeta para cada contador.
        card_tot, self.lbl_val_total = self._crear_tarjeta_stat("Total Clientes", "0", "#0071dc")
        card_reg, self.lbl_val_reg = self._crear_tarjeta_stat("Regulares", "0", "#16a34a")
        card_frec, self.lbl_val_frec = self._crear_tarjeta_stat("Frecuentes", "0", "#d97706")
        card_corp, self.lbl_val_corp = self._crear_tarjeta_stat("Corporativos", "0", "#7c3aed")

        stats_layout.addWidget(card_tot)
        stats_layout.addWidget(card_reg)
        stats_layout.addWidget(card_frec)
        stats_layout.addWidget(card_corp)
        layout.addLayout(stats_layout)

        # Formulario para registrar clientes.
        form_frame = QFrame()
        form_frame.setObjectName("form_card")
        form_grid = QGridLayout(form_frame)
        form_grid.setContentsMargins(20, 20, 20, 20)
        form_grid.setSpacing(12)

        # Etiquetas de los campos del formulario.
        lbl_nom = QLabel("Nombre:")
        lbl_nom.setProperty("class", "form_label")
        lbl_ed = QLabel("Edad:")
        lbl_ed.setProperty("class", "form_label")
        lbl_tp = QLabel("Tipo Cliente:")
        lbl_tp.setProperty("class", "form_label")
        lbl_pg = QLabel("Pago Preferido:")
        lbl_pg.setProperty("class", "form_label")

        # Campos para ingresar los datos del cliente.
        self.txt_cliente_nombre = QLineEdit()
        self.txt_cliente_nombre.setPlaceholderText("Ej. María García")

        self.txt_cliente_edad = QLineEdit()
        self.txt_cliente_edad.setPlaceholderText("Ej. 30")

        self.cmb_cliente_tipo = QComboBox()
        self.cmb_cliente_tipo.addItems(["Seleccione el tipo", "Regular", "Frecuente", "Corporativo"])

        self.cmb_pago_preferido = QComboBox()
        self.cmb_pago_preferido.addItems(["Seleccione el medio de pago", "Efectivo", "Tarjeta", "Transferencia"])

        # Botón para guardar el cliente.
        btn_guardar_cliente = QPushButton("Registrar Cliente")
        btn_guardar_cliente.setObjectName("btn_guardar")
        btn_guardar_cliente.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_guardar_cliente.clicked.connect(self.registrar_cliente_logica)

        # Organiza los campos del formulario.
        form_grid.addWidget(lbl_nom, 0, 0)
        form_grid.addWidget(self.txt_cliente_nombre, 0, 1)
        form_grid.addWidget(lbl_ed, 0, 2)
        form_grid.addWidget(self.txt_cliente_edad, 0, 3)

        form_grid.addWidget(lbl_tp, 1, 0)
        form_grid.addWidget(self.cmb_cliente_tipo, 1, 1)
        form_grid.addWidget(lbl_pg, 1, 2)
        form_grid.addWidget(self.cmb_pago_preferido, 1, 3)

        form_grid.addWidget(btn_guardar_cliente, 2, 0, 1, 4)
        layout.addWidget(form_frame)

        # Formulario para buscar y eliminar clientes.
        eliminar_frame = QFrame()
        eliminar_frame.setObjectName("form_card")
        eliminar_layout = QHBoxLayout(eliminar_frame)
        eliminar_layout.setContentsMargins(15, 12, 15, 12)
        eliminar_layout.setSpacing(10)

        lbl_buscar = QLabel("Buscar y eliminar por nombre:")
        lbl_buscar.setProperty("class", "form_label")

        self.txt_eliminar_nombre = QLineEdit()
        self.txt_eliminar_nombre.setPlaceholderText("Ingrese el nombre exacto del cliente")
        # Permite iniciar la búsqueda con Enter.
        self.txt_eliminar_nombre.returnPressed.connect(self.eliminar_cliente_por_nombre_logica)

        btn_eliminar_cliente = QPushButton("Eliminar cliente")
        btn_eliminar_cliente.setObjectName("btn_eliminar")
        btn_eliminar_cliente.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_eliminar_cliente.clicked.connect(self.eliminar_cliente_por_nombre_logica)

        eliminar_layout.addWidget(lbl_buscar)
        eliminar_layout.addWidget(self.txt_eliminar_nombre, 1)
        eliminar_layout.addWidget(btn_eliminar_cliente)

        layout.addWidget(eliminar_frame)

        # Tabla con los clientes registrados.
        self.tabla_clientes = QTableWidget()
        self.tabla_clientes.setColumnCount(5)
        self.tabla_clientes.setHorizontalHeaderLabels(["No.", "Nombre", "Edad", "Tipo de Cliente", "Pago Preferido"])
        self.tabla_clientes.verticalHeader().setVisible(False)

        header = self.tabla_clientes.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.tabla_clientes)

    def _crear_tarjeta_stat(self, titulo, valor_inicial, color_destacado):
        """Crea una tarjeta visual y devuelve la tarjeta junto con su contador."""
        # Crea una tarjeta para mostrar un contador.
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #cbd5e1;
            }
        """)
        l = QVBoxLayout(card)
        l.setContentsMargins(14, 12, 14, 12)

        lbl_val = QLabel(valor_inicial)
        lbl_val.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color_destacado};")

        lbl_t = QLabel(titulo)
        lbl_t.setStyleSheet("font-size: 13px; font-weight: 600; color: #475569;")

        l.addWidget(lbl_val)
        l.addWidget(lbl_t)
        return card, lbl_val

    def cargar_datos_iniciales(self):
        """Carga los clientes y calcula cuántos pertenecen a cada clasificación."""
        # Carga los clientes y cuenta cuántos hay de cada tipo.
        self.lista_clientes = []
        self.contador_total_clientes = 0
        self.contador_regulares = 0
        self.contador_frecuentes = 0
        self.contador_corporativos = 0

        registros_db = cargar_clientes_db()

        # Recorre los registros una vez para actualizar la lista y los contadores.
        for registro in registros_db:
            c_id, nombre, edad, tipo, pago = registro

            self.contador_total_clientes += 1
            # Cada cliente incrementa el contador de su clasificación.
            if tipo == "Regular":
                self.contador_regulares += 1
            # Se suma el contador de clientes frecuentes cuando esa es su categoría.
            elif tipo == "Frecuente":
                self.contador_frecuentes += 1
            # Se contabiliza a los clientes corporativos por separado.
            elif tipo == "Corporativo":
                self.contador_corporativos += 1

            self.lista_clientes.append({
                "id": c_id,
                "nombre": nombre,
                "edad": edad,
                "tipo": tipo,
                "pago": pago
            })

        self._actualizar_tabla()
        self._actualizar_contadores()

    def registrar_cliente_logica(self):
        """Valida los campos y guarda el cliente si todos los datos son correctos."""
        # Valida los datos y registra al cliente.
        nombre = self.txt_cliente_nombre.text().strip()
        edad_str = self.txt_cliente_edad.text().strip()
        tipo = self.cmb_cliente_tipo.currentText()
        pago = self.cmb_pago_preferido.currentText()

        # Los datos obligatorios deben existir antes de comprobar su formato.
        if not nombre or not edad_str:
            QMessageBox.warning(self, "Campos Incompletos", "Debe ingresar el nombre y la edad del cliente.")
            return

        # Se rechazan nombres con números para evitar datos evidentemente inválidos.
        if any(caracter.isdigit() for caracter in nombre):
            QMessageBox.warning(self, "Nombre Inválido", "El nombre del cliente no puede contener números.")
            return

        # La edad debe contener dígitos antes de convertirla a un número.
        if not edad_str.isdigit():
            QMessageBox.warning(self, "Edad Inválida", "La edad debe ser un número entero mayor que 0 y menor o igual que 100.")
            return

        edad = int(edad_str)
        # Se limita la edad a un rango razonable y mayor que cero.
        if not 0 < edad <= 100:
            QMessageBox.warning(self, "Edad Inválida", "La edad debe ser un número entero mayor que 0 y menor o igual que 100.")
            return

        # No se permite guardar las opciones iniciales de los menús desplegables.
        if tipo == "Seleccione el tipo" or pago == "Seleccione el medio de pago":
            QMessageBox.warning(self, "Selección Requerida", "Debe seleccionar un tipo de cliente y un método de pago válido.")
            return

        # Guarda el cliente y actualiza la pantalla.
        guardar_cliente_db(nombre, edad, tipo, pago)
        self.cargar_datos_iniciales()

        # Limpia los campos para un nuevo registro.
        self.txt_cliente_nombre.clear()
        self.txt_cliente_edad.clear()
        self.cmb_cliente_tipo.setCurrentIndex(0)
        self.cmb_pago_preferido.setCurrentIndex(0)

        QMessageBox.information(self, "Registro completado", f"El cliente «{nombre}» se registró correctamente.")

    def eliminar_cliente_por_nombre_logica(self):
        """Busca un cliente por nombre y pide confirmación antes de eliminarlo."""
        # Busca al cliente por nombre y solicita confirmación para eliminarlo.
        nombre_buscar = self.txt_eliminar_nombre.text().strip()

        # Un nombre vacío no permite identificar de forma segura al cliente.
        if not nombre_buscar:
            QMessageBox.warning(
                self,
                "Campo Vacío",
                "Por favor, ingrese el nombre del cliente que desea eliminar."
            )
            return

        # Busca el nombre sin distinguir mayúsculas y minúsculas.
        cliente_encontrado = next(
            (
                cliente for cliente in self.lista_clientes
                if cliente["nombre"].lower() == nombre_buscar.lower()
            ),
            None
        )

        # Solo se solicita confirmación cuando la búsqueda encontró un cliente.
        if cliente_encontrado is None:
            QMessageBox.warning(
                self,
                "No Encontrado",
                f"No se encontró ningún cliente registrado con el nombre '{nombre_buscar}'."
            )
        else:
            cliente_id = cliente_encontrado["id"]
            nombre_real = cliente_encontrado["nombre"]

            # Confirma la eliminación antes de modificar los datos.
            confirmacion = QMessageBox.question(
                self,
                "Confirmar Eliminación",
                f"¿Está seguro de que desea eliminar permanentemente al cliente '{nombre_real}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            # La base de datos se modifica únicamente si el usuario confirma.
            if confirmacion == QMessageBox.StandardButton.Yes:
                eliminar_cliente_db(cliente_id)
                self.cargar_datos_iniciales()
                self.txt_eliminar_nombre.clear()

                QMessageBox.information(
                    self,
                    "Eliminado",
                    f"El cliente '{nombre_real}' fue eliminado correctamente de la base de datos."
                )

    def _actualizar_tabla(self):
        """Reemplaza las filas de la tabla con los clientes cargados."""
        # Muestra los datos de los clientes en la tabla.
        self.tabla_clientes.setRowCount(len(self.lista_clientes))

        # Cada registro se presenta en una fila con sus cinco datos visibles.
        for idx, cli in enumerate(self.lista_clientes):
            item_no = QTableWidgetItem(str(idx + 1))
            item_nom = QTableWidgetItem(cli["nombre"])
            item_ed = QTableWidgetItem(str(cli["edad"]))
            item_tp = QTableWidgetItem(cli["tipo"])
            item_pg = QTableWidgetItem(cli["pago"])

            item_no.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # El número de fila se centra y todos los valores usan texto legible.
            for item in [item_no, item_nom, item_ed, item_tp, item_pg]:
                item.setForeground(Qt.GlobalColor.black)

            self.tabla_clientes.setItem(idx, 0, item_no)
            self.tabla_clientes.setItem(idx, 1, item_nom)
            self.tabla_clientes.setItem(idx, 2, item_ed)
            self.tabla_clientes.setItem(idx, 3, item_tp)
            self.tabla_clientes.setItem(idx, 4, item_pg)

    def _actualizar_contadores(self):
        """Actualiza las tarjetas con los contadores calculados desde la base."""
        # Actualiza los valores de las tarjetas.
        self.lbl_val_total.setText(str(self.contador_total_clientes))
        self.lbl_val_reg.setText(str(self.contador_regulares))
        self.lbl_val_frec.setText(str(self.contador_frecuentes))
        self.lbl_val_corp.setText(str(self.contador_corporativos))
