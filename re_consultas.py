from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from database import cargar_ventas_db

class ConsultasWidget(QWidget):
    def __init__(self):
        # Prepara la pantalla y carga las ventas disponibles.
        super().__init__()
        self.init_ui()
        self.cargar_fechas_disponibles()
        self.filtrar_por_fecha()

    def showEvent(self, event):
        # Actualiza las fechas y la tabla cada vez que se abre la pantalla.
        super().showEvent(event)
        self.cargar_fechas_disponibles()
        self.filtrar_por_fecha()

    def init_ui(self):
        # Crea el filtro de fechas y la tabla de resultados.
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
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        lbl_titulo = QLabel("Consulta detallada de ventas por fecha")
        lbl_titulo.setObjectName("titulo_modulo")
        layout.addWidget(lbl_titulo)

        # Filtro para elegir la fecha de las ventas.
        filtro_frame = QFrame()
        filtro_frame.setStyleSheet("background-color: #ffffff; border-radius: 8px; border: 1px solid #cbd5e1;")
        f_layout = QHBoxLayout(filtro_frame)
        f_layout.setContentsMargins(15, 12, 15, 12)
        
        lbl_filtro = QLabel("Filtrar ventas por fecha:")
        lbl_filtro.setStyleSheet("font-weight: bold; color: #1e293b;")
        
        self.cmb_fechas = QComboBox()
        self.cmb_fechas.currentIndexChanged.connect(self.filtrar_por_fecha)

        f_layout.addWidget(lbl_filtro)
        f_layout.addWidget(self.cmb_fechas, 1)
        layout.addWidget(filtro_frame)

        # Tabla con los datos de las ventas.
        self.tabla_consultas = QTableWidget()
        self.tabla_consultas.setColumnCount(8)
        self.tabla_consultas.setHorizontalHeaderLabels([
            "ID", "Fecha", "Cliente", "Producto", "Cantidad", "Subtotal (Q)", "Pago", "Total (Q)"
        ])
        self.tabla_consultas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabla_consultas)

    def cargar_fechas_disponibles(self):
        # Llena el filtro con las fechas que tienen ventas.
        self.cmb_fechas.blockSignals(True)
        self.cmb_fechas.clear()
        self.cmb_fechas.addItem("Todas las fechas")
        fechas = dict.fromkeys(venta[7] for venta in cargar_ventas_db())
        for fecha in fechas:
            self.cmb_fechas.addItem(fecha)
        self.cmb_fechas.blockSignals(False)

    def filtrar_por_fecha(self):
        # Muestra todas las ventas o solo las de la fecha seleccionada.
        fecha_sel = self.cmb_fechas.currentText()
        ventas = cargar_ventas_db()
        ventas_filtradas = [
            venta for venta in ventas
            if fecha_sel == "Todas las fechas" or venta[7] == fecha_sel
        ]

        self.tabla_consultas.setRowCount(len(ventas_filtradas))
        for idx, v in enumerate(ventas_filtradas):
            valores = (str(v[0]), v[7], v[1], v[2], str(v[3]), f"Q{v[8]:.2f}", v[6], f"Q{v[5]:.2f}")
            for columna, valor in enumerate(valores):
                self.tabla_consultas.setItem(idx, columna, QTableWidgetItem(valor))