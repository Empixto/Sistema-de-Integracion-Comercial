from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, 
    QScrollArea, QComboBox, QPushButton, QDialog
)
from PySide6.QtCore import Qt
from PySide6.QtCharts import QChart, QChartView, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis, QPieSeries
from PySide6.QtGui import QPainter, QColor
from database import cargar_ventas_db, cargar_clientes_db

# Empezamos modulo de estadisticas

class DialogoAnaliticaClientes(QDialog):
    def __init__(self, reg, frec, corp, total_cli, parent=None):
        # Prepara el resumen gráfico de clientes por tipo.
        super().__init__(parent)
        self.setWindowTitle("Analítica y Clasificación de Clientes")
        self.resize(500, 420)
        self.setStyleSheet("background-color: #f4f6f9; color: #0f172a; font-family: 'Segoe UI', sans-serif;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        lbl_titulo = QLabel("Estadísticas de clientes")
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #0b2545;")
        layout.addWidget(lbl_titulo)

        # Gráfico con la proporción de cada tipo de cliente.
        series = QPieSeries()
        series.append(f"Regulares ({reg})", reg if reg > 0 else 0.0001)
        series.append(f"Frecuentes ({frec})", frec if frec > 0 else 0.0001)
        series.append(f"Corporativos ({corp})", corp if corp > 0 else 0.0001)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"Total de Clientes Registrados: {total_cli}")
        chart.setTitleBrush(QColor("#0b2545"))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setStyleSheet("background: transparent; border-radius: 8px; border: 1px solid #cbd5e1;")
        layout.addWidget(chart_view)

        # Botón para cerrar el resumen.
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #0071dc;
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
                padding: 10px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #005bb5;
            }
        """)
        btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(btn_cerrar)


class EstadisticasWidget(QWidget):
    def __init__(self):
        # Inicializa los contadores y carga las estadísticas.
        super().__init__()
        self.cnt_regulares = 0
        self.cnt_frecuentes = 0
        self.cnt_corporativos = 0
        self.total_clientes_global = 0
        
        self.init_ui()
        self.cargar_fechas_disponibles()
        self.cargar_estadisticas()

    def showEvent(self, event):
        # Actualiza las estadísticas al mostrar la pantalla.
        super().showEvent(event)
        self.cargar_fechas_disponibles()
        self.cargar_estadisticas()

    def init_ui(self):
        # Crea los filtros, las tarjetas y el gráfico de ventas.
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
            QFrame#tarjeta_stat {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #cbd5e1;
            }
            QFrame#tarjeta_grafico {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #cbd5e1;
                padding: 5px;
            }
            QLabel.titulo_stat {
                font-size: 11px;
                font-weight: 600;
                color: #64748b;
            }
            QLabel.valor_stat {
                font-size: 18px;
                font-weight: bold;
                color: #0f172a;
            }
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                color: #0f172a;
            }
            QPushButton#btn_analitica_cli {
                background-color: #0071dc;
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
                border-radius: 6px;
                padding: 9px 15px;
                border: none;
            }
            QPushButton#btn_analitica_cli:hover {
                background-color: #005bb5;
            }
        """)

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(15)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        contenedor = QWidget()
        layout = QVBoxLayout(contenedor)
        layout.setSpacing(15)

        lbl_titulo = QLabel("Estadísticas y análisis comercial")
        lbl_titulo.setObjectName("titulo_modulo")
        layout.addWidget(lbl_titulo)

        # Filtro de fecha y acceso al resumen de clientes.
        bar_frame = QFrame()
        bar_frame.setStyleSheet("background-color: #ffffff; border-radius: 8px; border: 1px solid #cbd5e1;")
        b_layout = QHBoxLayout(bar_frame)
        b_layout.setContentsMargins(15, 10, 15, 10)

        lbl_fec = QLabel("Filtrar Estadísticas por Fecha:")
        lbl_fec.setStyleSheet("font-weight: bold; color: #1e293b;")

        self.cmb_fechas_stats = QComboBox()
        self.cmb_fechas_stats.currentIndexChanged.connect(self.cargar_estadisticas)

        self.btn_clientes_stats = QPushButton("Ver estadísticas de clientes")
        self.btn_clientes_stats.setObjectName("btn_analitica_cli")
        self.btn_clientes_stats.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clientes_stats.setStyleSheet("""
            QPushButton {
                background-color: #0071dc;
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
                border-radius: 6px;
                padding: 9px 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: #005bb5;
            }
        """)
        self.btn_clientes_stats.clicked.connect(self.mostrar_analitica_clientes)

        b_layout.addWidget(lbl_fec)
        b_layout.addWidget(self.cmb_fechas_stats, 1)
        b_layout.addWidget(self.btn_clientes_stats)
        layout.addWidget(bar_frame)

        # Tarjetas con los totales principales.
        grid_stats = QGridLayout()
        grid_stats.setSpacing(12)

        self.lbl_tot_clientes = self._crear_tarjeta(grid_stats, "Clientes Registrados (Global)", "0", 0, 0, "#0071dc")
        self.lbl_tot_ventas = self._crear_tarjeta(grid_stats, "Ventas Realizadas", "0", 0, 1, "#0071dc")
        self.lbl_tot_prod = self._crear_tarjeta(grid_stats, "Productos Vendidos", "0", 0, 2, "#0071dc")
        self.lbl_total_general = self._crear_tarjeta(grid_stats, "Total vendido", "Q0.00", 0, 3, "#16a34a")

        self.lbl_promed_ventas = self._crear_tarjeta(grid_stats, "Promedio de venta", "Q0.00", 1, 0, "#0284c7")
        self.lbl_venta_max = self._crear_tarjeta(grid_stats, "Venta mayor", "Q0.00", 1, 1, "#16a34a")
        self.lbl_venta_min = self._crear_tarjeta(grid_stats, "Venta menor", "Q0.00", 1, 2, "#eab308")
        self.lbl_pago_preferido = self._crear_tarjeta(grid_stats, "Método Más Utilizado", "N/D", 1, 3, "#9333ea")

        layout.addLayout(grid_stats)

        # Gráfico de ingresos por método de pago.
        lbl_sub_graf = QLabel("Distribución Financiera de Ventas por Método de Pago")
        lbl_sub_graf.setStyleSheet("font-size: 16px; font-weight: bold; color: #0b2545; margin-top: 10px;")
        layout.addWidget(lbl_sub_graf)

        self.frame_bar = QFrame()
        self.frame_bar.setObjectName("tarjeta_grafico")
        self.layout_bar_container = QVBoxLayout(self.frame_bar)
        self.layout_bar_container.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.frame_bar)

        scroll.setWidget(contenedor)
        layout_principal.addWidget(scroll)

    def _crear_tarjeta(self, grid, titulo, val_def, fila, col, color="#0f172a"):
        # Agrega una tarjeta de estadística y devuelve su etiqueta de valor.
        card = QFrame()
        card.setObjectName("tarjeta_stat")
        l = QVBoxLayout(card)
        l.setContentsMargins(12, 10, 12, 10)
        l.setSpacing(4)
        
        lbl_v = QLabel(val_def)
        lbl_v.setProperty("class", "valor_stat")
        lbl_v.setStyleSheet(f"color: {color};")
        
        lbl_t = QLabel(titulo)
        lbl_t.setProperty("class", "titulo_stat")
        
        l.addWidget(lbl_v)
        l.addWidget(lbl_t)
        grid.addWidget(card, fila, col)
        return lbl_v

    def cargar_fechas_disponibles(self):
        # Llena el filtro con las fechas que tienen ventas.
        self.cmb_fechas_stats.blockSignals(True)
        self.cmb_fechas_stats.clear()
        self.cmb_fechas_stats.addItem("Todas las fechas")
        fechas = dict.fromkeys(venta[7] for venta in cargar_ventas_db())
        for fecha in fechas:
            self.cmb_fechas_stats.addItem(fecha)
        self.cmb_fechas_stats.blockSignals(False)

    def cargar_estadisticas(self):
        # Calcula los totales y actualiza las tarjetas y el gráfico.
        fecha_sel = self.cmb_fechas_stats.currentText()
        ventas = cargar_ventas_db()
        clientes = cargar_clientes_db()

        self.total_clientes_global = len(clientes)
        self.cnt_regulares = 0
        self.cnt_frecuentes = 0
        self.cnt_corporativos = 0
        for c in clientes:
            tipo = c[3]
            if tipo == "Regular": self.cnt_regulares += 1
            elif tipo == "Frecuente": self.cnt_frecuentes += 1
            elif tipo == "Corporativo": self.cnt_corporativos += 1

        ventas_filtradas = [
            venta for venta in ventas
            if fecha_sel == "Todas las fechas" or venta[7] == fecha_sel
        ]

        total_ventas_cnt = 0
        total_productos_cnt = 0
        suma_totales = 0.0

        cnt_pago_efectivo = 0
        cnt_pago_tarjeta = 0
        cnt_pago_transf = 0

        acc_pago_efectivo = 0.0
        acc_pago_tarjeta = 0.0
        acc_pago_transf = 0.0

        venta_maxima = 0.0
        venta_minima = 999999999.0 if len(ventas_filtradas) > 0 else 0.0

        for v in ventas_filtradas:
            cant = v[3]
            tot = v[5]
            metodo = v[6]

            total_ventas_cnt += 1
            total_productos_cnt += cant
            suma_totales += tot

            if tot > venta_maxima: venta_maxima = tot
            if tot < venta_minima: venta_minima = tot

            if metodo == "Efectivo":
                cnt_pago_efectivo += 1
                acc_pago_efectivo += tot
            elif metodo == "Tarjeta":
                cnt_pago_tarjeta += 1
                acc_pago_tarjeta += tot
            elif metodo == "Transferencia":
                cnt_pago_transf += 1
                acc_pago_transf += tot

        promedio_ventas = (suma_totales / total_ventas_cnt) if total_ventas_cnt > 0 else 0.0
        if len(ventas_filtradas) == 0: venta_minima = 0.0

        metodo_mas_usado = "N/D"
        max_cnt = max(cnt_pago_efectivo, cnt_pago_tarjeta, cnt_pago_transf)
        if max_cnt > 0:
            empates = []
            if cnt_pago_efectivo == max_cnt: empates.append("Efectivo")
            if cnt_pago_tarjeta == max_cnt: empates.append("Tarjeta")
            if cnt_pago_transf == max_cnt: empates.append("Transferencia")
            
            if len(empates) == 1:
                metodo_mas_usado = empates[0]
            else:
                metodo_mas_usado = f"Empate: {' y '.join(empates)}"

        self.lbl_tot_clientes.setText(str(self.total_clientes_global))
        self.lbl_tot_ventas.setText(str(total_ventas_cnt))
        self.lbl_tot_prod.setText(str(total_productos_cnt))
        self.lbl_total_general.setText(f"Q{suma_totales:.2f}")

        self.lbl_promed_ventas.setText(f"Q{promedio_ventas:.2f}")
        self.lbl_venta_max.setText(f"Q{venta_maxima:.2f}")
        self.lbl_venta_min.setText(f"Q{venta_minima:.2f}")
        self.lbl_pago_preferido.setText(metodo_mas_usado)

        self.generar_grafico_barras(acc_pago_efectivo, acc_pago_tarjeta, acc_pago_transf, fecha_sel)

    def mostrar_analitica_clientes(self):
        # Abre el resumen de clientes clasificados por tipo.
        dialogo = DialogoAnaliticaClientes(
            self.cnt_regulares, self.cnt_frecuentes, self.cnt_corporativos, self.total_clientes_global, self
        )
        dialogo.exec()

    def generar_grafico_barras(self, efectivo, tarjeta, transf, fecha):
        # Actualiza el gráfico con los ingresos de cada método de pago.
        while self.layout_bar_container.count():
            item = self.layout_bar_container.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        set_pagos = QBarSet("Ingresos (Q)")
        set_pagos.append([efectivo, tarjeta, transf])
        set_pagos.setColor(QColor("#0071dc"))

        series = QBarSeries()
        series.append(set_pagos)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"Ingresos por Método de Pago - [{fecha}]")
        chart.setTitleBrush(QColor("#0b2545"))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        categorias = ["Efectivo", "Tarjeta", "Transferencia"]
        axis_x = QBarCategoryAxis()
        axis_x.append(categorias)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setTitleText("Monto (Q)")
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        chart.legend().setVisible(False)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(280)
        self.layout_bar_container.addWidget(chart_view)