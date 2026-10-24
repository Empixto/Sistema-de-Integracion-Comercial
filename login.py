import sys  # Permite cerrar la aplicación tras varios intentos fallidos.
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QMessageBox
)  # Controles de la pantalla de acceso.
from PySide6.QtCore import Qt, QTimer, Signal  # Alineación, aviso de acceso y temporizador.

class LoginWindow(QWidget):
    # Permite ingresar al sistema y avisa cuando el acceso es correcto.
    login_exitoso = Signal()

    def __init__(self):
        # Prepara la ventana de acceso.
        super().__init__()
        
        # Datos que se deben ingresar para acceder.
        self.USUARIO_CORRECTO = "admin"
        self.CLAVE_CORRECTA = "1111"
        
        # Lleva la cuenta de los intentos disponibles y los que fallaron.
        self.max_intentos = 3
        self.intentos_restantes = self.max_intentos
        self.contador_intentos_fallidos = 0
        
        # Recuerda si el acceso fue aprobado.
        self.bandera_acceso_concedido = False
        
        # Arma y acomoda los elementos de la pantalla.
        self.init_ui()

    def init_ui(self):
        # Crea los controles de la pantalla de acceso.
        self.setWindowTitle("Empi SIGC - Login")
        self.resize(900, 650)
        self.setMinimumSize(600, 500)
        
        # Define los colores y la apariencia de la pantalla.
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f6f9; /* Fondo gris claro. */
                color: #212529;
                font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            }
            QFrame#card {
                background-color: #ffffff; /* Fondo blanco para el recuadro del formulario. */
                border-radius: 10px;
                border: 1px solid #cbd5e1;
            }
            QLabel#title {
                font-size: 26px;
                font-weight: bold;
                color: #0b2545; /* Azul oscuro para el título. */
            }
            QLabel#subtitle {
                font-size: 14px;
                color: #64748b;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #94a3b8;
                border-radius: 6px;
                padding: 12px 14px;
                font-size: 14px;
                color: #0f172a;
            }
            QLineEdit:focus {
                border: 2px solid #0071dc; /* Resalta el campo que se está usando. */
            }
            QPushButton#btn_login {
                background-color: #ff9900; /* Naranja para destacar el botón. */
                color: #11111b;
                font-weight: bold;
                font-size: 15px;
                border-radius: 6px;
                padding: 12px;
                border: none;
            }
            QPushButton#btn_login:hover {
                background-color: #e88b00; /* Cambia el color al pasar el cursor. */
            }
            QLabel#status_error {
                color: #dc2626; /* Rojo para indicar un problema. */
                font-size: 13px;
                font-weight: bold;
            }
            QLabel#status_success {
                color: #16a34a; /* Verde para indicar que todo salió bien. */
                font-size: 13px;
                font-weight: bold;
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
            }
        """)

        # Coloca el formulario en el centro de la ventana.
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Agrupa los campos y el botón dentro de un recuadro.
        card = QFrame()
        card.setObjectName("card")
        card.setFixedWidth(420)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 35, 30, 35)
        card_layout.setSpacing(15)

        # Añade el título y el nombre del sistema.
        lbl_title = QLabel("Bienvenido")
        lbl_title.setObjectName("title")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_subtitle = QLabel("Inicie sesión con su usuario y contraseña para continuar.")
        lbl_subtitle.setObjectName("subtitle")
        lbl_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Espacio para escribir el nombre de usuario.
        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Nombre de usuario")
        
        # Espacio para escribir la contraseña sin mostrarla.
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Contraseña")
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)

        # Crea el botón para intentar ingresar.
        btn_login = QPushButton("Iniciar Sesión")
        btn_login.setObjectName("btn_login")
        btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_login.clicked.connect(self.validar_acceso)  # Revisa los datos al presionar el botón.

        # Aquí se mostrarán mensajes sobre el resultado del intento.
        self.lbl_mensaje = QLabel("")
        self.lbl_mensaje.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_mensaje.setWordWrap(True)

        # También se puede intentar ingresar con la tecla Enter.
        self.txt_password.returnPressed.connect(self.validar_acceso)
        self.txt_usuario.returnPressed.connect(self.validar_acceso)

        # Coloca los elementos dentro del recuadro.
        card_layout.addWidget(lbl_title)
        card_layout.addWidget(lbl_subtitle)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.txt_usuario)
        card_layout.addWidget(self.txt_password)
        card_layout.addSpacing(5)
        card_layout.addWidget(btn_login)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.lbl_mensaje)

        # Coloca el recuadro en el centro de la ventana.
        main_layout.addWidget(card)

    def validar_acceso(self):
        # Lee las credenciales sin espacios al inicio o al final.
        usuario = self.txt_usuario.text().strip()
        clave = self.txt_password.text().strip()

        # Pide completar ambos espacios si alguno está vacío.
        if not usuario or not clave:
            self.lbl_mensaje.setObjectName("status_error")
            self.lbl_mensaje.setStyle(self.lbl_mensaje.style())
            self.lbl_mensaje.setText("Por favor, ingrese tanto el usuario como la contraseña.")
            return

        if self.intentos_restantes <= 0:
            return

        # Compara lo escrito con los datos de acceso correctos.
        if usuario == self.USUARIO_CORRECTO and clave == self.CLAVE_CORRECTA:
            self.bandera_acceso_concedido = True
            self.lbl_mensaje.setObjectName("status_success")
            self.lbl_mensaje.setStyle(self.lbl_mensaje.style())
            self.lbl_mensaje.setText("Acceso concedido. Abriendo el sistema...")

            # Evita que se vuelvan a enviar datos mientras cambia la pantalla.
            self.txt_usuario.setEnabled(False)
            self.txt_password.setEnabled(False)

            # Espera un momento y luego abre la pantalla principal.
            QTimer.singleShot(800, self.abrir_menu_principal)
            return

        # Cuenta este fallo y resta una oportunidad.
        self.contador_intentos_fallidos += 1
        self.intentos_restantes -= 1

        # Muestra un mensaje distinto según queden intentos o no.
        if self.intentos_restantes > 0:
            self.lbl_mensaje.setObjectName("status_error")
            self.lbl_mensaje.setStyle(self.lbl_mensaje.style())
            self.lbl_mensaje.setText(
                f"Credenciales incorrectas.\nQuedan {self.intentos_restantes} intento(s) disponibles."
            )
            self.txt_password.clear()
            self.txt_password.setFocus()
            return

        # Informa que ya no quedan intentos.
        self.lbl_mensaje.setObjectName("status_error")
        self.lbl_mensaje.setStyle(self.lbl_mensaje.style())
        self.lbl_mensaje.setText("Acceso bloqueado. Límite superado.")

        self.txt_usuario.setEnabled(False)
        self.txt_password.setEnabled(False)

        # Avisa que se alcanzó el límite y cierra la aplicación.
        QMessageBox.critical(
            self,
            "Acceso Bloqueado",
            f"Ha superado el máximo de {self.max_intentos} intentos permitidos. El sistema se cerrará."
        )
        sys.exit()

    def abrir_menu_principal(self):
        # Avisa que el acceso fue aprobado.
        self.login_exitoso.emit()