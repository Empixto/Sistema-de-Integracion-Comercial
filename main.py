import sys  # Inicia la aplicación y la cierra al terminar.
from PySide6.QtWidgets import QApplication  # Permite mostrar las ventanas.
from login import LoginWindow  # Pantalla de acceso.
from dashboard import DashboardWindow  # Ventana principal.
from database import inicializar_bd  # Prepara la base de datos.

# Controla el paso de la pantalla de acceso a la ventana principal.
class AppController:
    """Coordina el paso de la pantalla de acceso a la ventana principal."""

    def __init__(self):
        """Prepara los datos y presenta la pantalla de inicio de sesión."""
        # Prepara la base de datos y muestra la pantalla de acceso.
        inicializar_bd()

        self.login_window = LoginWindow()

        # Abre la ventana principal cuando el acceso es correcto.
        self.login_window.login_exitoso.connect(self.mostrar_dashboard)

        self.login_window.show()

    def mostrar_dashboard(self):
        """Cambia al panel principal conservando el tamaño de la ventana."""
        # Conserva el tamaño y la posición de la ventana actual.
        login_geo = self.login_window.geometry()
        is_maximized = self.login_window.isMaximized()

        # Reemplaza el acceso por la ventana principal.
        self.login_window.close()

        self.dashboard_window = DashboardWindow()

        # Se conserva el estado maximizado para evitar un cambio inesperado de tamaño.
        if is_maximized:
            self.dashboard_window.showMaximized()
        else:
            self.dashboard_window.setGeometry(login_geo)
            self.dashboard_window.show()

# Inicia la aplicación cuando se ejecuta este archivo.
if __name__ == "__main__":
    # Qt procesa los eventos de la interfaz hasta que el usuario cierra la aplicación.
    app = QApplication(sys.argv)
    controller = AppController()
    sys.exit(app.exec())
