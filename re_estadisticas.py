from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QMessageBox, QDialog, QGridLayout
)
from PySide6.QtCore import Qt
from datetime import datetime
from database import cargar_ventas_db, cargar_clientes_db

# Los gráficos son opcionales; el módulo conserva una alternativa de texto.
try:
    from PySide6.QtCharts import QChart, QChartView, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis, QPieSeries
    HAS_CHARTS = True
except ImportError:
    # La interfaz puede mostrar los indicadores aunque Qt Charts no esté instalado.
    HAS_CHARTS = False


class DialogoClientesModal(QDialog):
    """Diálogo modal con analítica de clientes y gráfico de pastel."""
    def __init__(self, parent=None):
        """Calcula la distribución de clientes y presenta sus cantidades."""
        super().__init__(parent)
        self.setWindowTitle("Análisis global de clientes")
        self.setFixedSize(500, 420)
        self.setStyleSheet("""
            QDialog {
                background-color: #f4f6f9;
                color: #0f172a;
                font-family: 'Segoe UI', sans-serif;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        lbl_tit = QLabel("Distribución de Clientes por Clasificación")
        lbl_tit.setStyleSheet("font-size: 16px; font-weight: bold; color: #0b2545;")
        layout.addWidget(lbl_tit)

        clientes = cargar_clientes_db()
        # Cada clasificación se cuenta por separado para construir el gráfico.
        regulares = sum(1 for c in clientes if c[3] == "Regular")
        frecuentes = sum(1 for c in clientes if c[3] == "Frecuente")
        corporativos = sum(1 for c in clientes if c[3] == "Corporativo")

        # Si Qt Charts está instalado, se usa un gráfico; de lo contrario, texto.
        if HAS_CHARTS:
            series = QPieSeries()
            series.append(f"Regulares ({regulares})", regulares)
            series.append(f"Frecuentes ({frecuentes})", frecuentes)
            series.append(f"Corporativos ({corporativos})", corporativos)

            chart = QChart()
            chart.addSeries(series)
            chart.setTitle("Clasificación de Cartera de Clientes")
            chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
            chart.legend().setVisible(True)

            chart_view = QChartView(chart)
            chart_view.setRenderHint(chart_view.renderHints().Antialiasing)
            layout.addWidget(chart_view)
        else:
            lbl_fallback = QLabel(f"Regulares: {regulares}\nFrecuentes: {frecuentes}\nCorporativos: {corporativos}")
            layout.addWidget(lbl_fallback)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #64748b;
                color: #ffffff;
                font-weight: bold;
                padding: 8px 14px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #475569;
                color: #ffffff;
            }
        """)
        btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(btn_cerrar)


class EstadisticasWidget(QWidget):
    """Módulo de estadísticas filtrado estrictamente por búsqueda de fecha."""
    def __init__(self):
        """Inicializa la pantalla de indicadores y muestra los datos globales."""
        super().__init__()
        self.init_ui()
        self.cargar_estadisticas_general()

    def showEvent(self, event):
        """Actualiza las estadísticas cuando se vuelve a mostrar la sección."""
        super().showEvent(event)
        self.cargar_estadisticas_general()

    def init_ui(self):
        """Construye el filtro, las tarjetas de indicadores y el gráfico."""
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
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                color: #0f172a;
            }
            QFrame.kpi_card {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #cbd5e1;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        lbl_titulo = QLabel("Estadísticas y Análisis Comercial")
        lbl_titulo.setObjectName("titulo_modulo")
        layout.addWidget(lbl_titulo)

        # El filtro permite consultar estadísticas de una fecha específica.
        search_frame = QFrame()
        search_frame.setStyleSheet("background-color: #ffffff; border-radius: 8px; border: 1px solid #cbd5e1;")
        s_layout = QHBoxLayout(search_frame)
        s_layout.setContentsMargins(15, 12, 15, 12)

        lbl_busq = QLabel("Buscar por fecha (AAAA-MM-DD):")
        lbl_busq.setStyleSheet("font-weight: bold; color: #1e293b;")

        self.txt_fecha_busq = QLineEdit()
        self.txt_fecha_busq.setPlaceholderText("Ejemplo: 2026-11-01")
        self.txt_fecha_busq.setFixedWidth(160)

        self.btn_buscar = QPushButton("Buscar fecha")
        self.btn_buscar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_buscar.setStyleSheet("""
            QPushButton { background-color: #0071dc; color: #ffffff; font-weight: bold; border-radius: 6px; padding: 8px 14px; border: none; }
            QPushButton:hover { background-color: #005bb5; color: #ffffff; }
        """)
        self.btn_buscar.clicked.connect(self.ejecutar_busqueda_fecha)

        self.btn_todos = QPushButton("Mostrar todo")
        self.btn_todos.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_todos.setStyleSheet("""
            QPushButton { background-color: #64748b; color: #ffffff; font-weight: bold; border-radius: 6px; padding: 8px 14px; border: none; }
            QPushButton:hover { background-color: #475569; color: #ffffff; }
        """)
        self.btn_todos.clicked.connect(self.cargar_estadisticas_general)

        self.btn_clientes = QPushButton("Ver Analítica de Clientes")
        self.btn_clientes.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clientes.setStyleSheet("""
            QPushButton { background-color: #0071dc; color: #ffffff; font-weight: bold; border-radius: 6px; padding: 8px 14px; border: none; }
            QPushButton:hover { background-color: #005bb5; color: #ffffff; }
        """)
        self.btn_clientes.clicked.connect(self.abrir_modal_clientes)

        s_layout.addWidget(lbl_busq)
        s_layout.addWidget(self.txt_fecha_busq)
        s_layout.addWidget(self.btn_buscar)
        s_layout.addWidget(self.btn_todos)
        s_layout.addStretch()
        s_layout.addWidget(self.btn_clientes)
        layout.addWidget(search_frame)

        # Las tarjetas resumen los principales indicadores comerciales.
        grid_kpi = QGridLayout()
        grid_kpi.setSpacing(12)

        self.lbl_kpi_clientes = self.crear_tarjeta_kpi(grid_kpi, "Clientes Registrados (Global)", "0", 0, 0)
        self.lbl_kpi_ventas = self.crear_tarjeta_kpi(grid_kpi, "Ventas Realizadas", "0", 0, 1)
        self.lbl_kpi_productos = self.crear_tarjeta_kpi(grid_kpi, "Productos Vendidos", "0", 0, 2)
        self.lbl_kpi_total = self.crear_tarjeta_kpi(grid_kpi, "Total Vendido", "Q0.00", 0, 3)

        self.lbl_kpi_prom = self.crear_tarjeta_kpi(grid_kpi, "Promedio de Venta", "Q0.00", 1, 0)
        self.lbl_kpi_mayor = self.crear_tarjeta_kpi(grid_kpi, "Venta Mayor", "Q0.00", 1, 1)
        self.lbl_kpi_menor = self.crear_tarjeta_kpi(grid_kpi, "Venta Menor", "Q0.00", 1, 2)
        self.lbl_kpi_pago = self.crear_tarjeta_kpi(grid_kpi, "Método con mayor ingreso", "Sin ventas", 1, 3)

        layout.addLayout(grid_kpi)

        # Este contenedor permite reemplazar el gráfico tras cada consulta.
        self.chart_frame = QFrame()
        self.chart_frame.setStyleSheet("background-color: #ffffff; border-radius: 8px; border: 1px solid #cbd5e1;")
        self.c_layout = QVBoxLayout(self.chart_frame)
        self.c_layout.setContentsMargins(15, 15, 15, 15)
        layout.addWidget(self.chart_frame, 1)

    def crear_tarjeta_kpi(self, grid, titulo, valor_inicial, fila, col):
        """Crea una tarjeta de indicador y devuelve su etiqueta de valor."""
        frame = QFrame()
        frame.setProperty("class", "kpi_card")
        v_layout = QVBoxLayout(frame)
        v_layout.setContentsMargins(10, 8, 10, 8)

        lbl_val = QLabel(valor_inicial)
        lbl_val.setStyleSheet("font-size: 20px; font-weight: bold; color: #0071dc;")

        lbl_tit = QLabel(titulo)
        lbl_tit.setStyleSheet("font-size: 12px; font-weight: 600; color: #64748b;")

        v_layout.addWidget(lbl_val)
        v_layout.addWidget(lbl_tit)
        grid.addWidget(frame, fila, col)
        return lbl_val

    def cargar_estadisticas_general(self):
        """Carga las ventas y clientes para mostrar cifras globales."""
        self.txt_fecha_busq.clear()
        ventas = cargar_ventas_db()
        clientes = cargar_clientes_db()
        self.procesar_y_mostrar(ventas, len(clientes))

    def ejecutar_busqueda_fecha(self):
        """Valida la fecha y calcula estadísticas con las ventas de ese día."""
        fecha_busq = self.txt_fecha_busq.text().strip()
        # La conversión rechaza fechas inexistentes o con formato incorrecto.
        try:
            # La conversión verifica que la fecha exista y tenga el formato esperado.
            datetime.strptime(fecha_busq, "%Y-%m-%d")
        except ValueError:
            QMessageBox.warning(
                self,
                "Fecha no válida",
                "Ingrese una fecha válida con el formato AAAA-MM-DD "
                "(por ejemplo, 2026-11-01).",
            )
            return

        # Las estadísticas del día se calculan sobre sus ventas y la cartera global.
        ventas = cargar_ventas_db()
        ventas_filtradas = [v for v in ventas if v[8] == fecha_busq]
        clientes = cargar_clientes_db()

        # No se recalculan los indicadores con una lista vacía.
        if not ventas_filtradas:
            QMessageBox.information(self, "Sin resultados", f"No hay ventas registradas el {fecha_busq}.")
            return

        self.procesar_y_mostrar(ventas_filtradas, len(clientes))

    def procesar_y_mostrar(self, ventas, total_clientes):
        """Calcula los indicadores y actualiza las tarjetas y el gráfico."""
        # Cada ticket puede tener varias líneas, por lo que primero se agrupa.
        totales_por_ticket = {}
        total_productos_cnt = sum(int(v[4]) for v in ventas)
        cnt_efec = 0.0
        cnt_tarj = 0.0
        cnt_trans = 0.0

        # Una pasada acumula totales por ticket y ventas por medio de pago.
        for venta in ventas:
            ticket = venta[1]
            importe = float(venta[6])
            totales_por_ticket[ticket] = totales_por_ticket.get(ticket, 0.0) + importe
            # Cada importe se acumula según el método usado en la transacción.
            if venta[7] == "Efectivo":
                cnt_efec += importe
            # Se acumulan los pagos con tarjeta en su indicador específico.
            elif venta[7] == "Tarjeta":
                cnt_tarj += importe
            # Se acumulan las transferencias en su indicador específico.
            elif venta[7] == "Transferencia":
                cnt_trans += importe

        totales_tickets = list(totales_por_ticket.values())
        total_ventas_cnt = len(totales_por_ticket)

        suma_totales = sum(totales_tickets)
        venta_maxima = max(totales_tickets) if totales_tickets else 0.0
        venta_menor = min(totales_tickets) if totales_tickets else 0.0
        promedio = (suma_totales / total_ventas_cnt) if total_ventas_cnt > 0 else 0.0

        metodos_conteo = {"Efectivo": cnt_efec, "Tarjeta": cnt_tarj, "Transferencia": cnt_trans}
        # Se elige el método con mayor importe; sin ventas se muestra N/A.
        metodo_mayor_ingreso = (
            max(metodos_conteo, key=metodos_conteo.get)
            if any(metodos_conteo.values())
            else "Sin ventas"
        )

        self.lbl_kpi_clientes.setText(str(total_clientes))
        self.lbl_kpi_ventas.setText(str(total_ventas_cnt))
        self.lbl_kpi_productos.setText(str(total_productos_cnt))
        self.lbl_kpi_total.setText(f"Q{suma_totales:,.2f}")
        self.lbl_kpi_prom.setText(f"Q{promedio:,.2f}")
        self.lbl_kpi_mayor.setText(f"Q{venta_maxima:,.2f}")
        self.lbl_kpi_menor.setText(f"Q{venta_menor:,.2f}")
        self.lbl_kpi_pago.setText(metodo_mayor_ingreso)

        # Se eliminan los gráficos anteriores antes de insertar los resultados nuevos.
        while self.c_layout.count():
            item = self.c_layout.takeAt(0)
            # Los widgets antiguos se destruyen para liberar recursos de interfaz.
            if item.widget():
                item.widget().deleteLater()

        # El gráfico se crea solo cuando el módulo opcional Qt Charts está disponible.
        if HAS_CHARTS:
            bar_set = QBarSet("Ingresos por Método de Pago")
            bar_set << cnt_efec << cnt_tarj << cnt_trans

            series = QBarSeries()
            series.append(bar_set)

            chart = QChart()
            chart.addSeries(series)
            chart.setTitle("Distribución de Ingresos (Quetzales)")
            chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

            categories = ["Efectivo", "Tarjeta", "Transferencia"]
            axis_x = QBarCategoryAxis()
            axis_x.append(categories)
            chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            series.attachAxis(axis_x)

            axis_y = QValueAxis()
            chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
            series.attachAxis(axis_y)

            chart_view = QChartView(chart)
            chart_view.setRenderHint(chart_view.renderHints().Antialiasing)
            self.c_layout.addWidget(chart_view)

    def abrir_modal_clientes(self):
        """Abre la ventana modal con la distribución de clientes."""
        dialogo = DialogoClientesModal(self)
        dialogo.exec()
