from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QMessageBox, QLineEdit, QDialog, QFormLayout
)
from PySide6.QtCore import Qt
from datetime import datetime
from database import cargar_ventas_db, caja_esta_cerrada, registrar_cierre_caja

class DialogoPassword(QDialog):
    def __init__(self, parent=None):
        # Prepara la ventana para solicitar autorización.
        super().__init__(parent)
        self.setWindowTitle("Seguridad - Autorización de Cierre")
        self.setFixedSize(320, 150)
        self.setStyleSheet("background-color: #f4f6f9; color: #0f172a; font-family: 'Segoe UI', sans-serif;")
        
        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.lbl_info = QLabel("Ingrese su contraseña para autorizar\nel cierre de caja:")
        self.lbl_info.setStyleSheet("font-weight: bold; color: #0b2545;")
        
        self.txt_pass = QLineEdit()
        self.txt_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_pass.setPlaceholderText("Contraseña...")
        self.txt_pass.setStyleSheet("background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 8px;")
        
        btn_layout = QHBoxLayout()
        self.btn_aceptar = QPushButton("Autorizar")
        self.btn_aceptar.setStyleSheet("background-color: #0071dc; color: #ffffff; font-weight: bold; border-radius: 6px; padding: 8px 15px; border: none;")
        self.btn_aceptar.clicked.connect(self.accept)
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setStyleSheet("background-color: #64748b; color: #ffffff; font-weight: bold; border-radius: 6px; padding: 8px 15px; border: none;")
        self.btn_cancelar.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_aceptar)
        btn_layout.addWidget(self.btn_cancelar)
        
        layout.addRow(self.lbl_info)
        layout.addRow(QLabel("Contraseña:"), self.txt_pass)
        layout.addRow(btn_layout)

    def obtener_password(self):
        # Devuelve la contraseña ingresada sin espacios adicionales.
        return self.txt_pass.text().strip()


# Pantalla para revisar y cerrar la caja de una fecha.
class CierreCajaWidget(QWidget):
    def __init__(self):
        # Prepara la pantalla y carga las fechas disponibles.
        super().__init__()
        self.init_ui()
        self.cargar_fechas_disponibles()

    def showEvent(self, event):
        # Actualiza las fechas cuando se abre la pantalla.
        super().showEvent(event)
        self.cargar_fechas_disponibles()

    def init_ui(self):
        # Crea el selector de fecha y el resumen de caja.
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
            QComboBox, QLineEdit {
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

        lbl_titulo = QLabel("Cierre de caja")
        lbl_titulo.setObjectName("titulo_modulo")
        layout.addWidget(lbl_titulo)

        card_form = QFrame()
        card_form.setStyleSheet("background-color: #ffffff; border-radius: 8px; border: 1px solid #cbd5e1;")
        f_layout = QVBoxLayout(card_form)
        f_layout.setContentsMargins(20, 20, 20, 20)
        f_layout.setSpacing(15)

        lbl_sel = QLabel("Seleccione la fecha que desea cerrar:")
        lbl_sel.setStyleSheet("font-weight: bold; color: #1e293b;")
        
        self.cmb_fechas_cierre = QComboBox()
        self.cmb_fechas_cierre.currentIndexChanged.connect(self.actualizar_info_cierre_seleccionado)

        self.frame_info_cierre = QFrame()
        self.frame_info_cierre.setStyleSheet("background-color: #eff6ff; border-radius: 8px; border: 1px solid #bfdbfe;")
        c_layout = QVBoxLayout(self.frame_info_cierre)
        c_layout.setContentsMargins(15, 12, 15, 12)
        
        self.lbl_estado_titulo = QLabel("Estado de la caja")
        self.lbl_estado_titulo.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e3a8a;")
        
        self.lbl_estado_detalles = QLabel("Seleccione una fecha para ver el resumen.")
        self.lbl_estado_detalles.setStyleSheet("font-size: 13px; color: #334155;")
        
        c_layout.addWidget(self.lbl_estado_titulo)
        c_layout.addWidget(self.lbl_estado_detalles)

        # Botón para confirmar el cierre.
        self.btn_cierre = QPushButton("Cerrar caja")
        self.btn_cierre.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cierre.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                padding: 12px 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #b91c1c;
            }
        """)
        self.btn_cierre.clicked.connect(self.ejecutar_cierre_caja)

        f_layout.addWidget(lbl_sel)
        f_layout.addWidget(self.cmb_fechas_cierre)
        f_layout.addWidget(self.frame_info_cierre)
        f_layout.addWidget(self.btn_cierre)

        layout.addWidget(card_form)
        layout.addStretch()

    def cargar_fechas_disponibles(self):
        # Agrega hoy y las fechas de las ventas registradas.
        self.cmb_fechas_cierre.blockSignals(True)
        self.cmb_fechas_cierre.clear()
        
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        fechas = dict.fromkeys([fecha_hoy, *(venta[7] for venta in cargar_ventas_db())])
        for fecha in fechas:
            self.cmb_fechas_cierre.addItem(fecha)
        self.cmb_fechas_cierre.blockSignals(False)
        self.actualizar_info_cierre_seleccionado()

    def actualizar_info_cierre_seleccionado(self):
        # Muestra el estado y los totales de la fecha seleccionada.
        fecha_sel = self.cmb_fechas_cierre.currentText()
        if not fecha_sel:
            return
        cerrado = caja_esta_cerrada(fecha_sel)
        ventas_dia = [venta for venta in cargar_ventas_db() if venta[7] == fecha_sel]
        tot_dia = sum(venta[5] for venta in ventas_dia)
        cnt_dia = len(ventas_dia)

        if cerrado:
            self.frame_info_cierre.setStyleSheet("background-color: #fef2f2; border-radius: 8px; border: 1px solid #fecaca;")
            self.lbl_estado_titulo.setText(f"Caja cerrada ({fecha_sel})")
            self.lbl_estado_titulo.setStyleSheet("font-size: 14px; font-weight: bold; color: #991b1b;")
            self.lbl_estado_detalles.setText(f"Ventas: {cnt_dia} | Total: Q{tot_dia:.2f}")
        else:
            self.frame_info_cierre.setStyleSheet("background-color: #f0fdf4; border-radius: 8px; border: 1px solid #bbf7d0;")
            self.lbl_estado_titulo.setText(f"Caja abierta ({fecha_sel})")
            self.lbl_estado_titulo.setStyleSheet("font-size: 14px; font-weight: bold; color: #166534;")
            self.lbl_estado_detalles.setText(f"Ventas: {cnt_dia} | Ingresos acumulados: Q{tot_dia:.2f}")

    def ejecutar_cierre_caja(self):
        # Solicita autorización y registra el cierre de la fecha elegida.
        fecha_sel = self.cmb_fechas_cierre.currentText()
        if not fecha_sel:
            return

        if caja_esta_cerrada(fecha_sel):
            QMessageBox.information(self, "Caja cerrada", f"La caja del {fecha_sel} ya está cerrada.")
            return

        dialogo = DialogoPassword(self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            password = dialogo.obtener_password()
            
            # Comprueba la contraseña autorizada para el cierre.
            if password != "1111":
                QMessageBox.warning(self, "Contraseña incorrecta", "La contraseña no es válida. El cierre fue cancelado.")
                return

            ventas_dia = [venta for venta in cargar_ventas_db() if venta[7] == fecha_sel]
            total_dia = sum(venta[5] for venta in ventas_dia)
            ventas_dia_cnt = len(ventas_dia)

            registrar_cierre_caja(fecha_sel, total_dia, ventas_dia_cnt)
            self.actualizar_info_cierre_seleccionado()
            QMessageBox.information(
                self, "Cierre registrado",
                f"Se cerró la caja del {fecha_sel}.\nTotal: Q{total_dia:.2f} | Ventas: {ventas_dia_cnt}"
            )