from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QWidget,
    QPushButton, QComboBox, QSpinBox, QDoubleSpinBox, QFormLayout
)

from model.services.pagination_service import PaginationService
from view.components.pagination_widget import PaginationWidget
from view.components.students_table import StudentsTable

from utils.converters import empty_to_none
from utils.validators import validate_search_filters
from view.utils.ui_helpers import apply_base_style, fill_combo, show_error


class SearchDialog(QDialog):

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.setWindowTitle("Поиск студентов")
        self.resize(1100, 700)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(12)

        # ---------- ПАГИНАЦИЯ ----------
        self.pagination = PaginationService([])

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
        self.search_button = QPushButton("Найти")
        self.search_button.clicked.connect(self.perform_search)
        self.reset_button = QPushButton("Сбросить")
        self.reset_button.clicked.connect(self.reset_filters)
        button_row.addStretch()
        button_row.addWidget(self.search_button)
        button_row.addWidget(self.reset_button)
        self.layout.addLayout(button_row)

        # ---------- ТАБЛИЦА ----------
        self.table = StudentsTable()
        self.layout.addWidget(self.table)

        # ---------- ПАГИНАЦИЯ UI ----------
        self.pagination_widget = PaginationWidget()
        self.layout.addWidget(self.pagination_widget)

        self.setLayout(self.layout)

        self._connect_pagination()
        self._update_table()
        apply_base_style(self)

    # ---------- ЛОГИКА ----------

    def perform_search(self):
        try:
            filters = self._collect_filters()
            validate_search_filters(filters)
            results = self.controller.search_students(filters)
        except ValueError as error:
            show_error(self, str(error))
            return

        self.pagination.set_data(results)
        self._update_table()

    def _collect_filters(self):
        return {
            "group": empty_to_none(self.group_input.currentText()),
            "subject": empty_to_none(self.subject_input.currentText()),
            "min_avg": self._spinbox_value(self.min_avg_input),
            "max_avg": self._spinbox_value(self.max_avg_input),
            "min_score": self._spinbox_value(self.min_score_input),
            "max_score": self._spinbox_value(self.max_score_input),
        }

    # ---------- TABLE ----------

    def _update_table(self):
        data = self.pagination.get_page_data()
        self.table.set_students(data)

        self.pagination_widget.page_label.setText(
            f"Стр. {self.pagination.current_page}/{self.pagination.total_pages()} | "
            f"на странице {len(data)} | "
            f"всего {self.pagination.total_items()}"
        )

    # ---------- PAGINATION ----------

    def _connect_pagination(self):
        pw = self.pagination_widget

        pw.next_btn.clicked.connect(self.next_page)
        pw.prev_btn.clicked.connect(self.prev_page)
        pw.first_btn.clicked.connect(self.first_page)
        pw.last_btn.clicked.connect(self.last_page)
        pw.page_size_box.currentTextChanged.connect(self.change_page_size)

    def next_page(self):
        self.pagination.next()
        self._update_table()

    def prev_page(self):
        self.pagination.prev()
        self._update_table()

    def first_page(self):
        self.pagination.first()
        self._update_table()

    def last_page(self):
        self.pagination.last()
        self._update_table()

    def change_page_size(self, value):
        self.pagination.set_page_size(int(value))
        self._update_table()

    def reset_filters(self):
        self.group_input.setCurrentIndex(0)
        self.subject_input.setCurrentIndex(0)
        self.min_avg_input.setValue(self.min_avg_input.minimum())
        self.max_avg_input.setValue(self.max_avg_input.minimum())
        self.min_score_input.setValue(self.min_score_input.minimum())
        self.max_score_input.setValue(self.max_score_input.minimum())
        self.pagination.set_data([])
        self._update_table()

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
