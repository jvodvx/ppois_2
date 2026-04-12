from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton,
    QTableWidget, QSpinBox, QDialogButtonBox
)
from PyQt5.QtWidgets import QHeaderView

from model.entities.student import Student
from model.entities.exam import Exam

from utils.validators import validate_student, validate_exam
from view.utils.ui_helpers import apply_base_style, show_error


class AddDialog(QDialog):

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.setWindowTitle("Добавление студента")
        self.resize(650, 420)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(12)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Например: Иванов Иван")
        form_layout.addRow("ФИО:", self.name_input)

        self.group_input = QLineEdit()
        self.group_input.setPlaceholderText("Например: 101")
        form_layout.addRow("Группа:", self.group_input)
        self.layout.addLayout(form_layout)

        # ---------- ЭКЗАМЕНЫ ----------
        self.layout.addWidget(QLabel("Экзамены"))

        self.exam_table = QTableWidget()
        self.exam_table.setColumnCount(2)
        self.exam_table.setHorizontalHeaderLabels(["Предмет", "Балл"])
        self.exam_table.verticalHeader().setVisible(False)
        self.exam_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.exam_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.layout.addWidget(self.exam_table)

        # кнопки
        btn_layout = QHBoxLayout()

        self.add_exam_btn = QPushButton("Добавить экзамен")
        self.add_exam_btn.clicked.connect(self.add_exam_row)

        self.remove_exam_btn = QPushButton("Удалить экзамен")
        self.remove_exam_btn.clicked.connect(self.remove_exam_row)

        btn_layout.addWidget(self.add_exam_btn)
        btn_layout.addWidget(self.remove_exam_btn)

        self.layout.addLayout(btn_layout)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.save_student)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

        self.setLayout(self.layout)
        self.add_exam_row()
        apply_base_style(self)

    # ---------- TABLE ----------

    def add_exam_row(self):
        row = self.exam_table.rowCount()
        self.exam_table.insertRow(row)

        score_input = QSpinBox()
        score_input.setRange(0, 10)
        self.exam_table.setCellWidget(row, 1, score_input)

    def remove_exam_row(self):
        row = self.exam_table.currentRow()
        if row >= 0:
            self.exam_table.removeRow(row)

    # ---------- SAVE ----------

    def save_student(self):
        try:
            student = self._collect_data()
            self.controller.add_student(student)
            self.accept()

        except ValueError as e:
            show_error(self, str(e))

    def _collect_data(self):
        name = self.name_input.text().strip()
        group = self.group_input.text().strip()

        exams = []

        for row in range(self.exam_table.rowCount()):
            subject_item = self.exam_table.item(row, 0)
            score_widget = self.exam_table.cellWidget(row, 1)

            subject = subject_item.text().strip() if subject_item else ""
            score = score_widget.value() if score_widget else None

            validate_exam(subject, score, row + 1)

            exams.append(Exam(subject, score))

        validate_student(name, group, exams)

        return Student(name, group, exams)
