from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QWidget,
    QPushButton, QComboBox, QMessageBox, QSpinBox, QDoubleSpinBox, QFormLayout
)

from utils.converters import empty_to_none
from utils.validators import validate_delete_filters
from view.utils.ui_helpers import apply_base_style, show_error, show_info, fill_combo


class DeleteDialog(QDialog):

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.setWindowTitle("Удаление студентов")
        self.resize(500, 280)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(12)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.group_input = QComboBox()
        fill_combo(self.group_input, self.controller.get_groups())
        form_layout.addRow("Группа:", self.group_input)

        self.subject_input = QComboBox()
        fill_combo(self.subject_input, self.controller.get_subjects())
        form_layout.addRow("Предмет:", self.subject_input)

        self.min_avg_input = self._create_optional_double_spinbox()
        self.max_avg_input = self._create_optional_double_spinbox()
        form_layout.addRow("Средний балл:", self._create_range_row(self.min_avg_input, self.max_avg_input))

        self.min_score_input = self._create_optional_spinbox()
        self.max_score_input = self._create_optional_spinbox()
        form_layout.addRow("Балл по предмету:", self._create_range_row(self.min_score_input, self.max_score_input))
        self.layout.addLayout(form_layout)

        button_row = QHBoxLayout()
        button_row.addStretch()

        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.perform_delete)
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        button_row.addWidget(self.delete_button)
        button_row.addWidget(self.cancel_button)
        self.layout.addLayout(button_row)

        self.setLayout(self.layout)
        apply_base_style(self)

    # ---------- ЛОГИКА ----------

    def perform_delete(self):
        try:
            filters = self._collect_filters()
            validate_delete_filters(filters)
        except ValueError as error:
            show_error(self, str(error))
            return

        confirmation = QMessageBox.question(
            self,
            "Подтверждение",
            "Удалить записи по указанным условиям?"
        )
        if confirmation != QMessageBox.Yes:
            return

        count = self.controller.delete_students(filters)

        if count:
            show_info(self, "Результат", f"Удалено записей: {count}")
        else:
            show_info(self, "Результат", "Подходящих записей не найдено")

        self.accept()

    def _collect_filters(self):
        return {
            "group": empty_to_none(self.group_input.currentText()),
            "subject": empty_to_none(self.subject_input.currentText()),
            "min_avg": self._spinbox_value(self.min_avg_input),
            "max_avg": self._spinbox_value(self.max_avg_input),
            "min_score": self._spinbox_value(self.min_score_input),
            "max_score": self._spinbox_value(self.max_score_input),
        }

    def _create_optional_spinbox(self):
        spinbox = QSpinBox()
        spinbox.setRange(-1, 10)
        spinbox.setValue(-1)
        spinbox.setSpecialValueText("Не задано")
        return spinbox

    def _create_optional_double_spinbox(self):
        spinbox = QDoubleSpinBox()
        spinbox.setRange(-1.0, 10.0)
        spinbox.setDecimals(2)
        spinbox.setSingleStep(0.5)
        spinbox.setValue(-1.0)
        spinbox.setSpecialValueText("Не задано")
        return spinbox

    def _spinbox_value(self, spinbox):
        return None if spinbox.value() == spinbox.minimum() else spinbox.value()

    def _create_range_row(self, min_widget, max_widget):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel("От"))
        layout.addWidget(min_widget)
        layout.addWidget(QLabel("До"))
        layout.addWidget(max_widget)
        return container
