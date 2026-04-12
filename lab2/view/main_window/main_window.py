from PyQt5.QtWidgets import (
    QMainWindow, QAction, QVBoxLayout, QWidget, QToolBar, QFileDialog
)

from view.components.students_table import StudentsTable
from view.components.pagination_widget import PaginationWidget

from view.dialogs.search_dialog import SearchDialog
from view.dialogs.delete_dialog import DeleteDialog
from view.dialogs.add_dialog import AddDialog
from view.utils.ui_helpers import apply_base_style, show_error, show_info

from model.services.pagination_service import PaginationService


class MainWindow(QMainWindow):

    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        self.pagination = PaginationService([])

        self.setWindowTitle("Студенты")
        self.setGeometry(100, 100, 1100, 650)

        self._init_ui()
        self._connect_signals()
        self._load_data()
        apply_base_style(self)

    # ---------- UI ----------

    def _init_ui(self):
        self._create_menu()
        self._create_toolbar()

        self.table = StudentsTable()
        self.pagination_widget = PaginationWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.pagination_widget)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

    # ---------- MENU ----------

    def _create_menu(self):
        menu = self.menuBar().addMenu("Действия")

        self.add_action = QAction("Добавить", self)
        self.search_action = QAction("Поиск", self)
        self.delete_action = QAction("Удаление", self)
        self.save_action = QAction("Сохранить", self)
        self.load_action = QAction("Загрузить", self)

        menu.addActions([
            self.add_action,
            self.search_action,
            self.delete_action,
            self.save_action,
            self.load_action
        ])

    # ---------- TOOLBAR ----------

    def _create_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        toolbar.addActions([
            self.add_action,
            self.search_action,
            self.delete_action,
            self.save_action,
            self.load_action
        ])

    # ---------- SIGNALS ----------

    def _connect_signals(self):
        self.add_action.triggered.connect(self.open_add)
        self.search_action.triggered.connect(self.open_search)
        self.delete_action.triggered.connect(self.open_delete)

        self.save_action.triggered.connect(self.save_file)
        self.load_action.triggered.connect(self.load_file)

        # pagination
        pw = self.pagination_widget
        pw.next_btn.clicked.connect(self.next_page)
        pw.prev_btn.clicked.connect(self.prev_page)
        pw.first_btn.clicked.connect(self.first_page)
        pw.last_btn.clicked.connect(self.last_page)
        pw.page_size_box.currentTextChanged.connect(self.change_page_size)

    # ---------- DATA ----------

    def _load_data(self):
        data = self.controller.get_all_students()
        self.pagination.set_data(data)
        self._update_view()

    def _update_view(self):
        page_data = self.pagination.get_page_data()
        self.table.set_students(page_data)

        self.pagination_widget.page_label.setText(self._page_text(len(page_data)))
        self.statusBar().showMessage(
            f"Всего записей: {self.pagination.total_items()} | "
            f"Текущая страница: {self.pagination.current_page}/{self.pagination.total_pages()}"
        )

    # ---------- PAGINATION ----------

    def next_page(self):
        self.pagination.next()
        self._update_view()

    def prev_page(self):
        self.pagination.prev()
        self._update_view()

    def first_page(self):
        self.pagination.first()
        self._update_view()

    def last_page(self):
        self.pagination.last()
        self._update_view()

    def change_page_size(self, value):
        self.pagination.set_page_size(int(value))
        self._update_view()

    def _page_text(self, items_on_page: int):
        return (
            f"Стр. {self.pagination.current_page}/{self.pagination.total_pages()} | "
            f"на странице {items_on_page} | "
            f"всего {self.pagination.total_items()}"
        )

    # ---------- ACTIONS ----------

    def open_add(self):
        if AddDialog(self.controller).exec_():
            self._load_data()

    def open_search(self):
        SearchDialog(self.controller).exec_()

    def open_delete(self):
        if DeleteDialog(self.controller).exec_():
            self._load_data()

    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить", "", "XML files (*.xml)")
        if filename:
            try:
                self.controller.save_to_file(filename)
                show_info(self, "Сохранение", "Данные успешно сохранены")
            except Exception as error:
                show_error(self, f"Не удалось сохранить файл: {error}")

    def load_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Открыть", "", "XML files (*.xml)")
        if filename:
            try:
                self.controller.load_from_file(filename)
                self._load_data()
                show_info(self, "Загрузка", "Данные успешно загружены")
            except Exception as error:
                show_error(self, f"Не удалось загрузить файл: {error}")
