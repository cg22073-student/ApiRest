import sys
import requests

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QCheckBox,
    QMessageBox,
    QFormLayout,
    QGroupBox,
    QSpinBox
)

BASE_URL = "http://localhost:9080/InventarioWebAppPRN335-1.0-SNAPSHOT/Resources/v1"
REQUEST_TIMEOUT = 3


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cliente REST - TipoUnidadMedida (PySide6)")
        self.resize(900, 600)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout()
        central.setLayout(main_layout)

        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout, 2)

        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout, 3)

        form_group = QGroupBox("Datos de TipoUnidadMedida")
        form_layout = QFormLayout()
        form_group.setLayout(form_layout)

        self.id_spin = QSpinBox()
        self.id_spin.setMinimum(0)
        self.id_spin.setMaximum(100)
        form_layout.addRow(QLabel("ID:"), self.id_spin)

        self.nombre_edit = QLineEdit()
        form_layout.addRow(QLabel("Nombre:"), self.nombre_edit)

        self.unidad_base_edit = QLineEdit()
        form_layout.addRow(QLabel("Unidad base:"), self.unidad_base_edit)

        self.comentarios_edit = QLineEdit()
        form_layout.addRow(QLabel("Comentarios:"), self.comentarios_edit)

        self.activo_check = QCheckBox("Activo")
        self.activo_check.setChecked(True)
        form_layout.addRow(QLabel(""), self.activo_check)

        left_layout.addWidget(form_group)
        buttons_layout = QVBoxLayout()

        self.btn_listar = QPushButton("Listar todos")
        self.btn_buscar = QPushButton("Buscar por ID")
        self.btn_crear = QPushButton("Crear nuevo")
        self.btn_actualizar = QPushButton("Actualizar")
        self.btn_eliminar = QPushButton("Eliminar")

        buttons_layout.addWidget(self.btn_listar)
        buttons_layout.addWidget(self.btn_buscar)
        buttons_layout.addWidget(self.btn_crear)
        buttons_layout.addWidget(self.btn_actualizar)
        buttons_layout.addWidget(self.btn_eliminar)
        buttons_layout.addStretch()

        left_layout.addLayout(buttons_layout)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        right_layout.addWidget(QLabel("Salida / Respuestas del servidor:"))
        right_layout.addWidget(self.output)

        self.btn_listar.clicked.connect(self.listar_todos)
        self.btn_buscar.clicked.connect(self.buscar_por_id)
        self.btn_crear.clicked.connect(self.crear)
        self.btn_actualizar.clicked.connect(self.actualizar)
        self.btn_eliminar.clicked.connect(self.eliminar)

        self.id_spin.editingFinished.connect(self.buscar_por_id_auto)

    def mostrar_error(self, mensaje, detalle=None):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error")
        msg.setText(mensaje)
        if detalle:
            msg.setInformativeText(detalle)
        msg.exec()

    def mostrar_info(self, mensaje):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Información")
        msg.setText(mensaje)
        msg.exec()

    def append_output(self, text):
        self.output.append(text)

    def listar_todos(self):
        url = f"{BASE_URL}/tipounidadmedidas/all"
        try:
            resp = requests.get(url, timeout=REQUEST_TIMEOUT)
            self.output.clear()
            if resp.status_code == 200:
                data = resp.json()
                if not data:
                    self.append_output("No hay registros de TipoUnidadMedida.")
                    return
                self.append_output("----------------------------------------")
                for item in data:
                    self.append_output(f"ID: {item.get('id')}")
                    self.append_output(f"Nombre     : {item.get('nombre')}")
                    self.append_output(f"Activo     : {item.get('activo')}")
                    self.append_output(f"Unidad base: {item.get('unidadBase')}")
                    self.append_output(f"Comentarios: {item.get('comentarios')}")
                    self.append_output("----------------------------------------")
            else:
                self.mostrar_error(
                    "Error al listar.",
                    f"Código HTTP: {resp.status_code}\n{resp.text}"
                )
        except requests.exceptions.ConnectTimeout:
            self.mostrar_error(
                "Tiempo de espera agotado.",
                "El servidor REST no respondió a tiempo (timeout)."
            )
        except requests.exceptions.ConnectionError:
            self.mostrar_error(
                "No se pudo conectar.",
                "El servidor REST está apagado o no es accesible."
            )
        except Exception as e:
            self.mostrar_error(
                "Error inesperado al conectar con el servidor.",
                str(e)
            )

    def _buscar_por_id(self, mostrar_mensajes: bool):
        id_val = self.id_spin.value()
        if id_val <= 0:
            if mostrar_mensajes:
                self.mostrar_info("Debes indicar un ID válido.")
            return

        url = f"{BASE_URL}/tipounidadmedidas/{id_val}"
        try:
            resp = requests.get(url, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                item = resp.json()
                self.output.clear()
                self.append_output("=== DETALLE TIPO_UNIDAD_MEDIDA ===")
                self.append_output(f"ID         : {item.get('id')}")
                self.append_output(f"Nombre     : {item.get('nombre')}")
                self.append_output(f"Activo     : {item.get('activo')}")
                self.append_output(f"Unidad base: {item.get('unidadBase')}")
                self.append_output(f"Comentarios: {item.get('comentarios')}")

                self.nombre_edit.setText(item.get("nombre") or "")
                self.unidad_base_edit.setText(item.get("unidadBase") or "")
                self.comentarios_edit.setText(item.get("comentarios") or "")
                self.activo_check.setChecked(bool(item.get("activo")))
            elif resp.status_code == 404:
                self.output.clear()
                self.append_output(f"No se encontró TipoUnidadMedida con id {id_val}.")
                # limpiar formulario
                self.nombre_edit.clear()
                self.unidad_base_edit.clear()
                self.comentarios_edit.clear()
                self.activo_check.setChecked(False)
                if mostrar_mensajes:
                    self.mostrar_info(
                        f"No se encontró TipoUnidadMedida con id {id_val}."
                    )
            else:
                if mostrar_mensajes:
                    self.mostrar_error(
                        "Error al buscar.",
                        f"Código HTTP: {resp.status_code}\n{resp.text}"
                    )
        except requests.exceptions.ConnectTimeout:
            if mostrar_mensajes:
                self.mostrar_error(
                    "Tiempo de espera agotado.",
                    "El servidor REST no respondió a tiempo (timeout)."
                )
        except requests.exceptions.ConnectionError:
            if mostrar_mensajes:
                self.mostrar_error(
                    "No se pudo conectar.",
                    "El servidor REST está apagado o no es accesible."
                )
        except Exception as e:
            if mostrar_mensajes:
                self.mostrar_error(
                    "Error inesperado al conectar con el servidor.",
                    str(e)
                )

    def buscar_por_id(self):
        self._buscar_por_id(mostrar_mensajes=True)

    def buscar_por_id_auto(self):
        self._buscar_por_id(mostrar_mensajes=False)

    def crear(self):
        nombre = self.nombre_edit.text().strip()
        unidad_base = self.unidad_base_edit.text().strip()
        comentarios = self.comentarios_edit.text().strip()
        activo = self.activo_check.isChecked()

        if not nombre:
            self.mostrar_info("El campo 'Nombre' es obligatorio para crear.")
            return

        payload = {
            "nombre": nombre,
            "activo": activo,
            "unidadBase": unidad_base or None,
            "comentarios": comentarios or None
        }

        url = f"{BASE_URL}/tipounidadmedidas"
        try:
            resp = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
            self.output.clear()
            if resp.status_code == 201:
                creado = resp.json()
                self.append_output("✔ Registro creado correctamente.")
                self.append_output(f"Nuevo ID: {creado.get('id')}")
                self.mostrar_info(f"Registro creado. ID: {creado.get('id')}")
            elif resp.status_code == 422:
                self.mostrar_error("Error de validación (422).", resp.text)
            else:
                self.mostrar_error(
                    "Error al crear.",
                    f"Código HTTP: {resp.status_code}\n{resp.text}"
                )
        except requests.exceptions.ConnectTimeout:
            self.mostrar_error(
                "Tiempo de espera agotado.",
                "El servidor REST no respondió a tiempo (timeout)."
            )
        except requests.exceptions.ConnectionError:
            self.mostrar_error(
                "No se pudo conectar.",
                "El servidor REST está apagado o no es accesible."
            )
        except Exception as e:
            self.mostrar_error(
                "Error inesperado al conectar con el servidor.",
                str(e)
            )

    def actualizar(self):
        id_val = self.id_spin.value()
        if id_val <= 0:
            self.mostrar_info("Debes indicar un ID válido para actualizar.")
            return

        nombre = self.nombre_edit.text().strip()
        unidad_base = self.unidad_base_edit.text().strip()
        comentarios = self.comentarios_edit.text().strip()
        activo = self.activo_check.isChecked()

        if not nombre:
            self.mostrar_info("El campo 'Nombre' es obligatorio para actualizar.")
            return

        payload = {
            "id": id_val,
            "nombre": nombre,
            "unidadBase": unidad_base or None,
            "comentarios": comentarios or None,
            "activo": activo
        }

        url = f"{BASE_URL}/tipounidadmedidas/{id_val}"
        try:
            resp = requests.put(url, json=payload, timeout=REQUEST_TIMEOUT)
            self.output.clear()
            if resp.status_code == 200:
                self.append_output("✔ Registro actualizado correctamente.")
                self.mostrar_info("Registro actualizado correctamente.")
            elif resp.status_code == 404:
                self.mostrar_info(
                    f"No se encontró TipoUnidadMedida con id {id_val}."
                )
            elif resp.status_code == 422:
                self.mostrar_error("Error de validación (422).", resp.text)
            else:
                self.mostrar_error(
                    "Error al actualizar.",
                    f"Código HTTP: {resp.status_code}\n{resp.text}"
                )
        except requests.exceptions.ConnectTimeout:
            self.mostrar_error(
                "Tiempo de espera agotado.",
                "El servidor REST no respondió a tiempo (timeout)."
            )
        except requests.exceptions.ConnectionError:
            self.mostrar_error(
                "No se pudo conectar.",
                "El servidor REST está apagado o no es accesible."
            )
        except Exception as e:
            self.mostrar_error(
                "Error inesperado al conectar con el servidor.",
                str(e)
            )

    def eliminar(self):
        id_val = self.id_spin.value()
        if id_val <= 0:
            self.mostrar_info("Debes indicar un ID válido para eliminar.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Seguro que deseas eliminar el registro con ID {id_val}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm != QMessageBox.Yes:
            return

        url = f"{BASE_URL}/tipounidadmedidas/{id_val}"
        try:
            resp = requests.delete(url, timeout=REQUEST_TIMEOUT)
            self.output.clear()
            if resp.status_code == 204:
                self.append_output("✔ Registro eliminado correctamente.")
                self.mostrar_info("Registro eliminado correctamente.")
                self.nombre_edit.clear()
                self.unidad_base_edit.clear()
                self.comentarios_edit.clear()
                self.activo_check.setChecked(False)
            elif resp.status_code == 404:
                self.mostrar_info(
                    f"No se encontró TipoUnidadMedida con id {id_val}."
                )
            else:
                self.mostrar_error(
                    "Error al eliminar.",
                    f"Código HTTP: {resp.status_code}\n{resp.text}"
                )
        except requests.exceptions.ConnectTimeout:
            self.mostrar_error (
                "Tiempo de espera agotado.",
                "El servidor REST no respondió a tiempo (timeout)."
            )
        except requests.exceptions.ConnectionError:
            self.mostrar_error(
                "No se pudo conectar.",
                "El servidor REST está apagado o no es accesible."
            )
        except Exception as e:
            self.mostrar_error(
                "Error inesperado al conectar con el servidor.",
                str(e)
            )


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
