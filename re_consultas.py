from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt
from datetime import datetime
from database import cargar_ventas_db

class ConsultasWidget(QWidget):
    """Módulo de consulta de ventas filtrado por búsqueda de fecha exacta."""
    def __init__(self):
        """Prepara la pantalla y muestra inicialmente todas las ventas."""
        super().__init__()
        self.init_ui()
        self.cargar_todas_ventas()

    def showEvent(self, event):
        """Recarga las ventas cada vez que se vuelve a mostrar la pantalla."""
        super().showEvent(event)
        self.cargar_todas_ventas()

    def init_ui(self):
        """Construye el filtro de fecha y la tabla de resultados."""
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
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                color: #0f172a;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        lbl_titulo = QLabel("Consulta Detallada de Ventas")
        lbl_titulo.setObjectName("titulo_modulo")
        layout.addWidget(lbl_titulo)

        filtro_frame = QFrame()
        filtro_frame.setStyleSheet("background-color: #ffffff; border-radius: 8px; border: 1px solid #cbd5e1;")
        f_layout = QHBoxLayout(filtro_frame)
        f_layout.setContentsMargins(15, 12, 15, 12)

        lbl_filtro = QLabel("Buscar por fecha (AAAA-MM-DD):")
        lbl_filtro.setStyleSheet("font-weight: bold; color: #1e293b;")

        self.txt_fecha = QLineEdit()
        self.txt_fecha.setPlaceholderText("Ejemplo: 2026-11-01")
        self.txt_fecha.setFixedWidth(160)

        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_buscar.setStyleSheet("""
            QPushButton { background-color: #0071dc; color: #ffffff; font-weight: bold; border-radius: 6px; padding: 8px 14px; border: none; }
            QPushButton:hover { background-color: #005bb5; color: #ffffff; }
        """)
        self.btn_buscar.clicked.connect(self.buscar_por_fecha)

        self.btn_todos = QPushButton("Mostrar todo")
        self.btn_todos.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_todos.setStyleSheet("""
            QPushButton { background-color: #64748b; color: #ffffff; font-weight: bold; border-radius: 6px; padding: 8px 14px; border: none; }
            QPushButton:hover { background-color: #475569; color: #ffffff; }
        """)
        self.btn_todos.clicked.connect(self.cargar_todas_ventas)

        f_layout.addWidget(lbl_filtro)
        f_layout.addWidget(self.txt_fecha)
        f_layout.addWidget(self.btn_buscar)
        f_layout.addWidget(self.btn_todos)
        f_layout.addStretch()
        layout.addWidget(filtro_frame)

        self.tabla_consultas = QTableWidget()
        self.tabla_consultas.setColumnCount(6)
        self.tabla_consultas.setHorizontalHeaderLabels([
            "Fecha", "Cliente", "Productos Adquiridos", "Método Pago", "Descuento", "Total (Q)"
        ])
        self.tabla_consultas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabla_consultas)

    def cargar_todas_ventas(self):
        """Limpia el filtro y presenta todas las líneas de venta agrupadas."""
        self.txt_fecha.clear()
        ventas = cargar_ventas_db()
        self.poblar_tabla(ventas)

    def buscar_por_fecha(self):
        """Valida la fecha y muestra solo las ventas registradas ese día."""
        fecha_busq = self.txt_fecha.text().strip()
        # La conversión rechaza fechas inexistentes o con formato incorrecto.
        try:
            # La conversión rechaza fechas inexistentes o con formato incorrecto.
            datetime.strptime(fecha_busq, "%Y-%m-%d")
        except ValueError:
            QMessageBox.warning(
                self,
                "Fecha no válida",
                "Ingrese una fecha válida con el formato AAAA-MM-DD.",
            )
            return

        # Se filtran las ventas ya cargadas por la fecha exacta seleccionada.
        ventas = cargar_ventas_db()
        ventas_filtradas = [v for v in ventas if v[8] == fecha_busq]

        # Se informa cuando el filtro no encuentra registros y se vacía la tabla.
        if not ventas_filtradas:
            QMessageBox.information(self, "Sin resultados", f"No hay ventas registradas el {fecha_busq}.")
            self.tabla_consultas.setRowCount(0)
            return

        self.poblar_tabla(ventas_filtradas)

    def poblar_tabla(self, ventas):
        """Agrupa líneas por ticket y muestra un registro por transacción."""
        agrupadas = {}
        # Cada grupo conserva los datos comunes y acumula productos e importes.
        for reg in ventas:
            g_id = reg[1]
            # Se crea un resumen solo la primera vez que aparece cada ticket.
            if g_id not in agrupadas:
                agrupadas[g_id] = {
                    "fecha": reg[8], "cliente": reg[2], "metodo": reg[7],
                    "productos": [], "total_desc": 0.0, "total_ticket": 0.0
                }
            agrupadas[g_id]["productos"].append(f"- {reg[3]} (Cantidad: {reg[4]})")
            agrupadas[g_id]["total_desc"] += reg[10]
            agrupadas[g_id]["total_ticket"] += reg[6]

        lista_final = list(agrupadas.values())
        self.tabla_consultas.setRowCount(len(lista_final))
        # Cada ticket agrupado se escribe en una fila de la tabla.
        for idx, item in enumerate(lista_final):
            prod_texto = "\n".join(item["productos"])
            self.tabla_consultas.setItem(idx, 0, QTableWidgetItem(item["fecha"]))
            self.tabla_consultas.setItem(idx, 1, QTableWidgetItem(item["cliente"]))
            self.tabla_consultas.setItem(idx, 2, QTableWidgetItem(prod_texto))
            self.tabla_consultas.setItem(idx, 3, QTableWidgetItem(item["metodo"]))
            self.tabla_consultas.setItem(idx, 4, QTableWidgetItem(f"Q{item['total_desc']:.2f}"))
            self.tabla_consultas.setItem(idx, 5, QTableWidgetItem(f"Q{item['total_ticket']:.2f}"))
