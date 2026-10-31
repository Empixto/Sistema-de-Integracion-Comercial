from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QStackedWidget, QLabel, QFrame
)
from PySide6.QtCore import Qt
from re_clients import ClientesWidget
from re_catalogo import CatalogoWidget      # <--- Nuevo módulo de Catálogo
from re_ventas import VentasWidget
from re_consultas import ConsultasWidget
from re_cierre import CierreCajaWidget
from re_estadisticas import EstadisticasWidget

class DashboardWindow(QMainWindow):
    """Ventana principal que integra los módulos del sistema comercial."""

    def __init__(self):
        """Inicializa la ventana principal y prepara las secciones del sistema."""
        super().__init__()

        self.setWindowTitle("Empi SIGC - Panel principal")
        self.resize(1150, 750)
        self.setMinimumSize(950, 650)

        self.init_ui()

    def cerrar_aplicacion(self):
        """Cierra la ventana principal y finaliza la sesión actual."""
        self.close()

    def init_ui(self):
        """Construye el menú lateral y el contenedor de las pantallas."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f4f6f9;
            }
            QFrame#sidebar {
                background-color: #ffffff;
                border-right: 1px solid #cbd5e1;
            }
            QLabel#sidebar_title {
                font-size: 16px;
                font-weight: bold;
                color: #0b2545;
                padding: 10px;
            }
            QPushButton.nav_button {
                background-color: transparent;
                color: #334155;
                text-align: left;
                padding: 11px 16px;
                font-size: 13px;
                font-weight: 600;
                border-radius: 6px;
                border: none;
            }
            QPushButton.nav_button:hover {
                background-color: #e2e8f0;
                color: #0f172a;
            }
            QPushButton.nav_button_active {
                background-color: #0071dc;
                color: #ffffff;
                text-align: left;
                padding: 11px 16px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton#btn_salir {
                background-color: #dc2626;
                color: #ffffff;
                text-align: left;
                padding: 11px 16px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton#btn_salir:hover {
                background-color: #b91c1c;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # El menú lateral permite acceder a cada módulo de la aplicación.
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(6)

        lbl_menu = QLabel("PANEL PRINCIPAL")
        lbl_menu.setObjectName("sidebar_title")
        sidebar_layout.addWidget(lbl_menu)

        # Cada botón activa el módulo asociado con su posición en el contenedor.
        self.btn_clientes = QPushButton("Gestión de clientes")
        self.btn_clientes.setProperty("class", "nav_button_active")
        self.btn_clientes.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clientes.clicked.connect(lambda: self.cambiar_seccion(0))
        sidebar_layout.addWidget(self.btn_clientes)

        self.btn_catalogo = QPushButton("Catálogo de productos")
        self.btn_catalogo.setProperty("class", "nav_button")
        self.btn_catalogo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_catalogo.clicked.connect(lambda: self.cambiar_seccion(1))
        sidebar_layout.addWidget(self.btn_catalogo)

        self.btn_ventas = QPushButton("Registrar ventas")
        self.btn_ventas.setProperty("class", "nav_button")
        self.btn_ventas.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ventas.clicked.connect(lambda: self.cambiar_seccion(2))
        sidebar_layout.addWidget(self.btn_ventas)

        self.btn_consultas = QPushButton("Consultar ventas")
        self.btn_consultas.setProperty("class", "nav_button")
        self.btn_consultas.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_consultas.clicked.connect(lambda: self.cambiar_seccion(3))
        sidebar_layout.addWidget(self.btn_consultas)

        self.btn_cierre = QPushButton("Cierre de caja")
        self.btn_cierre.setProperty("class", "nav_button")
        self.btn_cierre.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cierre.clicked.connect(lambda: self.cambiar_seccion(4))
        sidebar_layout.addWidget(self.btn_cierre)

        self.btn_estadisticas = QPushButton("Estadísticas y análisis")
        self.btn_estadisticas.setProperty("class", "nav_button")
        self.btn_estadisticas.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_estadisticas.clicked.connect(lambda: self.cambiar_seccion(5))
        sidebar_layout.addWidget(self.btn_estadisticas)

        sidebar_layout.addStretch()

        self.btn_salir = QPushButton("Cerrar sesión")
        self.btn_salir.setObjectName("btn_salir")
        self.btn_salir.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_salir.clicked.connect(self.cerrar_aplicacion)
        sidebar_layout.addWidget(self.btn_salir)

        main_layout.addWidget(sidebar)

        # El contenedor mantiene los módulos disponibles y muestra uno a la vez.
        self.stack_pages = QStackedWidget()

        self.clientes_widget = ClientesWidget()
        self.catalogo_widget = CatalogoWidget()
        self.ventas_widget = VentasWidget()
        self.consultas_widget = ConsultasWidget()
        self.cierre_widget = CierreCajaWidget()
        self.estadisticas_widget = EstadisticasWidget()

        self.stack_pages.addWidget(self.clientes_widget)      # Índice 0
        self.stack_pages.addWidget(self.catalogo_widget)      # Índice 1
        self.stack_pages.addWidget(self.ventas_widget)        # Índice 2
        self.stack_pages.addWidget(self.consultas_widget)     # Índice 3
        self.stack_pages.addWidget(self.cierre_widget)        # Índice 4
        self.stack_pages.addWidget(self.estadisticas_widget)  # Índice 5

        main_layout.addWidget(self.stack_pages)

    def cambiar_seccion(self, index):
        """Muestra el módulo elegido y marca su botón como activo."""
        self.stack_pages.setCurrentIndex(index)

        # El orden de esta lista coincide con el de las páginas del contenedor.
        botones = (
            self.btn_clientes,
            self.btn_catalogo,
            self.btn_ventas,
            self.btn_consultas,
            self.btn_cierre,
            self.btn_estadisticas,
        )
        # Se actualiza el estilo de cada botón para destacar solo la sección activa.
        for i, btn in enumerate(botones):
            # El índice determina cuál botón representa la pantalla visible.
            if i == index:
                btn.setProperty("class", "nav_button_active")
            else:
                btn.setProperty("class", "nav_button")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
