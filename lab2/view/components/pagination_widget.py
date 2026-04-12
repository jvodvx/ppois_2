from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox


class PaginationWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 4, 0, 0)
        self.layout.setSpacing(8)

        self.first_btn = QPushButton("<<")
        self.prev_btn = QPushButton("<")
        self.next_btn = QPushButton(">")
        self.last_btn = QPushButton(">>")
        for button in (self.first_btn, self.prev_btn, self.next_btn, self.last_btn):
            button.setFixedWidth(36)

        self.page_label = QLabel()
        self.page_label.setMinimumWidth(240)

        self.page_size_label = QLabel("Записей на странице:")
        self.page_size_box = QComboBox()
        self.page_size_box.addItems(["5", "10", "20"])
        self.page_size_box.setCurrentText("10")
        self.page_size_box.setFixedWidth(80)

        self.layout.addWidget(self.first_btn)
        self.layout.addWidget(self.prev_btn)
        self.layout.addWidget(self.next_btn)
        self.layout.addWidget(self.last_btn)
        self.layout.addWidget(self.page_label)
        self.layout.addStretch()
        self.layout.addWidget(self.page_size_label)
        self.layout.addWidget(self.page_size_box)

        self.setLayout(self.layout)
