from PyQt5.QtWidgets import QMessageBox


def show_info(parent, title, text):
    QMessageBox.information(parent, title, text)


def show_error(parent, text):
    QMessageBox.warning(parent, "Ошибка", text)


def fill_combo(combo, items):
    combo.clear()
    combo.addItem("")
    combo.addItems(items)


def apply_base_style(widget):
    widget.setStyleSheet("""
        QWidget {
            font-size: 13px;
        }
        QMainWindow, QDialog {
            background: #f6f7fb;
        }
        QTableWidget {
            background: white;
            border: 1px solid #d7dbe7;
            gridline-color: #e7eaf3;
            selection-background-color: #dbe8ff;
            selection-color: #1f2a44;
        }
        QHeaderView::section {
            background: #eef2fb;
            border: none;
            border-right: 1px solid #d7dbe7;
            border-bottom: 1px solid #d7dbe7;
            padding: 6px;
            font-weight: 600;
        }
        QPushButton {
            background: #ffffff;
            border: 1px solid #cdd5e3;
            border-radius: 6px;
            padding: 6px 12px;
        }
        QPushButton:hover {
            background: #f0f4ff;
        }
        QPushButton:pressed {
            background: #e4ecff;
        }
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            background: white;
            border: 1px solid #cdd5e3;
            border-radius: 6px;
            padding: 5px 8px;
            min-height: 28px;
        }
        QLabel {
            color: #2d3648;
        }
    """)
