import sys
from PyQt5.QtWidgets import QApplication

from controller.app_controller import AppController
from view.main_window.main_window import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)

    controller = AppController()

    window = MainWindow(controller)
    window.show()

    sys.exit(app.exec_())
