from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem


class StudentsTable(QTableWidget):

    def __init__(self):
        super().__init__()
        self._set_headers(0)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setWordWrap(False)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(False)

    def set_students(self, students):
        max_exam_count = max((len(student.exams) for student in students), default=0)
        self._set_headers(max_exam_count)
        self.setRowCount(len(students))

        for row, s in enumerate(students):
            self.setItem(row, 0, QTableWidgetItem(s.name))
            self.setItem(row, 1, QTableWidgetItem(s.group))
            self.setItem(row, 2, QTableWidgetItem(f"{s.average_score():.2f}"))

            for exam_index in range(max_exam_count):
                subject_column = 3 + exam_index * 2
                score_column = subject_column + 1

                if exam_index < len(s.exams):
                    exam = s.exams[exam_index]
                    self.setItem(row, subject_column, QTableWidgetItem(exam.subject))
                    self.setItem(row, score_column, QTableWidgetItem(str(exam.score)))
                else:
                    self.setItem(row, subject_column, QTableWidgetItem(""))
                    self.setItem(row, score_column, QTableWidgetItem(""))

    def _set_headers(self, exam_count: int):
        headers = ["ФИО", "Группа", "Средний балл"]
        for index in range(exam_count):
            headers.extend([f"Предмет {index + 1}", f"Балл {index + 1}"])

        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        for column in range(3, len(headers)):
            mode = QHeaderView.Stretch if column % 2 == 1 else QHeaderView.ResizeToContents
            header.setSectionResizeMode(column, mode)

    def setItem(self, row, column, item):
        if item is not None:
            item.setTextAlignment(Qt.AlignCenter if column != 0 else Qt.AlignVCenter | Qt.AlignLeft)
        super().setItem(row, column, item)
