from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox, QLineEdit, QDialog, QFormLayout
)
from PySide6.QtCore import Qt
from datetime import datetime
from database import cargar_ventas_db, obtener_cierre_caja, registrar_cierre_caja_detallado


def _calcular_resumen_ventas(ventas_dia):
    """Calcula los indicadores diarios recorriendo cada registro una sola vez.

    Cada venta contiene, entre otros datos, el número de ticket en la posición 1,
    la cantidad de productos en la posición 4, el total en la posición 6, el
    medio de pago en la posición 7, los descuentos en la posición 10 y los
    recargos en la posición 11.
    """
    # Se acumulan los importes por ticket para contar ventas y calcular sus
    # valores mayor, menor y promedio, aunque el ticket tenga varios productos.
    totales_por_ticket = {}
    productos_vendidos = 0
    efectivo = 0.0
    tarjeta = 0.0
    transferencia = 0.0
    descuentos = 0.0
    recargos = 0.0

    # Una sola pasada reúne todos los datos necesarios para el informe.
    for venta in ventas_dia:
        ticket = venta[1]
        importe_venta = float(venta[6])
        medio_pago = venta[7]
        totales_por_ticket[ticket] = (
            totales_por_ticket.get(ticket, 0.0) + importe_venta
        )
        productos_vendidos += int(venta[4])

        # Cada medio de pago se suma únicamente en su propio indicador.
        # Cada medio reconocido se suma solo en su indicador correspondiente.
        if medio_pago == "Efectivo":
            efectivo += importe_venta
        # El siguiente caso contabiliza pagos efectuados con tarjeta.
        elif medio_pago == "Tarjeta":
            tarjeta += importe_venta
        # El último medio admitido es la transferencia.
        elif medio_pago == "Transferencia":
            transferencia += importe_venta

        descuentos += float(venta[10])
        recargos += float(venta[11])

    importes_tickets = list(totales_por_ticket.values())
    cantidad_ventas = len(totales_por_ticket)
    total_vendido = sum(importes_tickets)

    # Cuando no hay tickets, los importes mayor, menor y promedio son cero.
    venta_mayor = max(importes_tickets, default=0.0)
    venta_menor = min(importes_tickets, default=0.0)
    promedio = total_vendido / cantidad_ventas if cantidad_ventas else 0.0

    return {
        "ventas_realizadas": cantidad_ventas,
        "productos_vendidos": productos_vendidos,
        "efectivo": efectivo,
        "tarjeta": tarjeta,
        "transferencia": transferencia,
        "descuentos": descuentos,
        "recargos": recargos,
        "total_vendido": total_vendido,
        "venta_mayor": venta_mayor,
        "venta_menor": venta_menor,
        "promedio": promedio,
    }


class DialogoPassword(QDialog):
    """Cuadro de diálogo que solicita la contraseña para autorizar el cierre."""

    def __init__(self, parent=None):
        """Prepara el cuadro donde se solicita la autorización del cierre."""
        super().__init__(parent)
        self.setWindowTitle("Autorización de Cierre")
        self.setFixedSize(320, 150)
        self.setStyleSheet("""
            QDialog {
                background-color: #f4f6f9;
                color: #0f172a;
                font-family: 'Segoe UI', sans-serif;
            }
        """)

        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self.lbl_info = QLabel("Ingrese su contraseña de administrador:")
        self.lbl_info.setStyleSheet("font-weight: bold; color: #0b2545;")

        self.txt_pass = QLineEdit()
        self.txt_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_pass.setPlaceholderText("Contraseña...")
        self.txt_pass.setStyleSheet("background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 8px; color: #0f172a;")

        btn_layout = QHBoxLayout()
        self.btn_aceptar = QPushButton("Autorizar")
        self.btn_aceptar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_aceptar.setStyleSheet("""
            QPushButton { background-color: #0071dc; color: #ffffff; font-weight: bold; border-radius: 6px; padding: 8px 15px; border: none; }
            QPushButton:hover { background-color: #005bb5; color: #ffffff; }
        """)
        self.btn_aceptar.clicked.connect(self.accept)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancelar.setStyleSheet("""
            QPushButton { background-color: #64748b; color: #ffffff; font-weight: bold; border-radius: 6px; padding: 8px 15px; border: none; }
            QPushButton:hover { background-color: #475569; color: #ffffff; }
        """)
        self.btn_cancelar.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_aceptar)
        btn_layout.addWidget(self.btn_cancelar)

        layout.addRow(self.lbl_info)
        layout.addRow(QLabel("Contraseña:"), self.txt_pass)
        layout.addRow(btn_layout)

    def obtener_password(self):
        """Devuelve la contraseña escrita, sin espacios al inicio o al final."""
        return self.txt_pass.text().strip()


class CierreCajaWidget(QWidget):
    """Módulo de Cierre de Caja basado en búsqueda e ingreso de fecha."""
    def __init__(self):
        """Crea el módulo y solicita la construcción de su interfaz."""
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Construye los controles y conecta cada botón con su acción."""
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
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # El título identifica el propósito de esta pantalla.
        lbl_titulo = QLabel("Cierre de Caja Diario")
        lbl_titulo.setObjectName("titulo_modulo")
        layout.addWidget(lbl_titulo)

        # La tarjeta reúne la fecha, el informe diario y el botón de cierre.
        card_form = QFrame()
        card_form.setStyleSheet("background-color: #ffffff; border-radius: 8px; border: 1px solid #cbd5e1;")
        f_layout = QVBoxLayout(card_form)
        f_layout.setContentsMargins(20, 20, 20, 20)
        f_layout.setSpacing(15)

        # Esta barra permite elegir qué día consultar o cerrar.
        busq_layout = QHBoxLayout()
        lbl_sel = QLabel("Fecha para consultar o cerrar (AAAA-MM-DD):")
        lbl_sel.setStyleSheet("font-weight: bold; color: #1e293b;")

        self.txt_fecha_cierre = QLineEdit()
        # La fecha actual es el valor inicial que se consulta al abrir la pantalla.
        self.txt_fecha_cierre.setText(datetime.now().strftime("%Y-%m-%d"))
        self.txt_fecha_cierre.setPlaceholderText("AAAA-MM-DD")
        self.txt_fecha_cierre.setFixedWidth(150)

        self.btn_buscar_cierre = QPushButton("Consultar fecha")
        self.btn_buscar_cierre.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_buscar_cierre.setStyleSheet("""
            QPushButton { background-color: #0071dc; color: #ffffff; font-weight: bold; border-radius: 6px; padding: 8px 14px; border: none; }
            QPushButton:hover { background-color: #005bb5; color: #ffffff; }
        """)
        # Al consultar, se vuelve a calcular o recuperar el resumen mostrado.
        self.btn_buscar_cierre.clicked.connect(self.actualizar_info_cierre)

        busq_layout.addWidget(lbl_sel)
        busq_layout.addWidget(self.txt_fecha_cierre)
        busq_layout.addWidget(self.btn_buscar_cierre)
        busq_layout.addStretch()
        f_layout.addLayout(busq_layout)

        # Este panel muestra los totales y el estado del cierre seleccionado.
        self.frame_info_cierre = QFrame()
        self.frame_info_cierre.setStyleSheet("background-color: #f8fafc; border-radius: 8px; border: 1px solid #cbd5e1;")
        c_layout = QVBoxLayout(self.frame_info_cierre)
        c_layout.setContentsMargins(20, 15, 20, 15)
        c_layout.setSpacing(8)

        self.lbl_informe = QLabel("Ingrese una fecha y seleccione «Consultar fecha» para ver el resumen.")
        self.lbl_informe.setStyleSheet("font-family: 'Consolas', monospace; font-size: 13px; color: #0f172a; line-height: 1.4;")
        c_layout.addWidget(self.lbl_informe)

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
                color: #ffffff;
            }
        """)
        # El cierre solo se ejecuta después de presionar este botón.
        self.btn_cierre.clicked.connect(self.ejecutar_cierre_caja)

        f_layout.addWidget(self.frame_info_cierre)
        f_layout.addWidget(self.btn_cierre)

        layout.addWidget(card_form)
        layout.addStretch()

        # Se muestra automáticamente el resumen del día actual al abrir.
        self.actualizar_info_cierre()

    def actualizar_info_cierre(self):
        """Valida la fecha y muestra el cierre guardado o un resumen preliminar."""
        fecha_sel = self.txt_fecha_cierre.text().strip()
        # La fecha se convierte para comprobar que sea real y esté bien escrita.
        try:
            # La conversión verifica que la fecha exista y tenga el formato esperado.
            datetime.strptime(fecha_sel, "%Y-%m-%d")
        except ValueError:
            # Sin una fecha válida no se consulta la base de datos.
            QMessageBox.warning(
                self,
                "Fecha no válida",
                "Ingrese una fecha válida con el formato AAAA-MM-DD.",
            )
            return

        # Se comprueba primero si el cierre ya existe para mostrar sus valores guardados.
        cierre_db = obtener_cierre_caja(fecha_sel)

        # Si ya existe un cierre, el informe usa sus valores permanentes.
        if cierre_db:
            informe = (
                f"========== CIERRE DE CAJA ({fecha_sel}) - CERRADO ==========\n\n"
                f"Ventas realizadas: {cierre_db[2]}\n"
                f"Productos vendidos: {cierre_db[3]}\n\n"
                f"Ventas en efectivo:    Q{cierre_db[4]:,.2f}\n"
                f"Ventas con tarjeta:    Q{cierre_db[5]:,.2f}\n"
                f"Ventas por transferencia: Q{cierre_db[6]:,.2f}\n\n"
                f"Descuentos otorgados:  Q{cierre_db[7]:,.2f}\n"
                f"Recargos aplicados:    Q{cierre_db[8]:,.2f}\n\n"
                f"TOTAL VENDIDO:         Q{cierre_db[9]:,.2f}\n\n"
                f"Venta mayor:           Q{cierre_db[10]:,.2f}\n"
                f"Venta menor:           Q{cierre_db[11]:,.2f}\n"
                f"Promedio de venta:     Q{cierre_db[12]:,.2f}\n"
                f"=================================================="
            )
            self.frame_info_cierre.setStyleSheet("background-color: #fef2f2; border-radius: 8px; border: 1px solid #fecaca;")
            self.btn_cierre.setEnabled(False)
            self.btn_cierre.setStyleSheet("""
                QPushButton { background-color: #94a3b8; color: #ffffff; font-weight: bold; border-radius: 6px; padding: 12px; border: none; }
            """)
        else:
            # Solo se cargan las ventas si hace falta preparar un resumen preliminar.
            ventas = cargar_ventas_db()
            ventas_dia = [v for v in ventas if v[8] == fecha_sel]
            resumen = _calcular_resumen_ventas(ventas_dia)

            informe = (
                f"========== CIERRE DE CAJA ({fecha_sel}) - ABIERTO ==========\n\n"
                f"Ventas realizadas: {resumen['ventas_realizadas']}\n"
                f"Productos vendidos: {resumen['productos_vendidos']}\n\n"
                f"Ventas en efectivo:    Q{resumen['efectivo']:,.2f}\n"
                f"Ventas con tarjeta:    Q{resumen['tarjeta']:,.2f}\n"
                f"Ventas por transferencia: Q{resumen['transferencia']:,.2f}\n\n"
                f"Descuentos otorgados:  Q{resumen['descuentos']:,.2f}\n"
                f"Recargos aplicados:    Q{resumen['recargos']:,.2f}\n\n"
                f"TOTAL VENDIDO:         Q{resumen['total_vendido']:,.2f}\n\n"
                f"Venta mayor:           Q{resumen['venta_mayor']:,.2f}\n"
                f"Venta menor:           Q{resumen['venta_menor']:,.2f}\n"
                f"Promedio de venta:     Q{resumen['promedio']:,.2f}\n"
                f"=================================================="
            )
            self.frame_info_cierre.setStyleSheet("background-color: #f0fdf4; border-radius: 8px; border: 1px solid #bbf7d0;")
            self.btn_cierre.setEnabled(True)
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
                    color: #ffffff;
                }
            """)

        self.lbl_informe.setText(informe)

    def ejecutar_cierre_caja(self):
        """Solicita autorización y guarda de forma permanente el cierre diario."""
        fecha_sel = self.txt_fecha_cierre.text().strip()
        # No se inicia el proceso si la fecha no representa un día válido.
        try:
            # La misma validación evita guardar cierres con fechas incorrectas.
            datetime.strptime(fecha_sel, "%Y-%m-%d")
        except ValueError:
            # Se detiene la operación antes de solicitar la contraseña.
            QMessageBox.warning(
                self,
                "Fecha no válida",
                "Ingrese una fecha válida con el formato AAAA-MM-DD.",
            )
            return

        # El usuario debe autorizar la acción antes de guardar el cierre.
        dialogo = DialogoPassword(self)
        # El cierre continúa solo si se aceptó el cuadro de autorización.
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            # Una contraseña incorrecta cancela el cierre y deja los datos intactos.
            if dialogo.obtener_password() != "1111":
                QMessageBox.warning(
                    self,
                    "Autorización no válida",
                    "La contraseña de administrador es incorrecta.",
                )
                return

            # El resumen se calcula con las ventas del día, no con otros días.
            ventas = cargar_ventas_db()
            ventas_dia = [v for v in ventas if v[8] == fecha_sel]
            resumen = _calcular_resumen_ventas(ventas_dia)

            # Los indicadores calculados se guardan en la base de datos como cierre.
            registrar_cierre_caja_detallado(
                fecha_sel,
                resumen["ventas_realizadas"],
                resumen["productos_vendidos"],
                resumen["efectivo"],
                resumen["tarjeta"],
                resumen["transferencia"],
                resumen["descuentos"],
                resumen["recargos"],
                resumen["total_vendido"],
                resumen["venta_mayor"],
                resumen["venta_menor"],
                resumen["promedio"],
            )

            # Se actualiza la pantalla para reflejar el estado cerrado recién guardado.
            self.actualizar_info_cierre()
            QMessageBox.information(
                self,
                "Cierre completado",
                f"La caja del día {fecha_sel} se cerró correctamente.",
            )
