import sys
import asyncio

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QMessageBox,
    QStackedLayout, QMainWindow, QSplashScreen
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer, QSharedMemory

from qt_material import apply_stylesheet
from pages.home import Home_page
from pages.information_page import Information_page
from widgets.app_header import app_header
from widgets.firstpage import resource_path

from qasync import QEventLoop
import qtawesome as qta


class Launcher(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowIcon(qta.icon('fa5s.play', color='red'))
        self.setWindowTitle("anime browser")

        # -------------------------
        # HEADER
        # -------------------------
        self.app_header = app_header()

        # -------------------------
        # CENTRAL CONTAINER
        # -------------------------
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)

        self.container.setStyleSheet("background:rgb(54, 52, 52)")

        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # -------------------------
        # STACK (pages)
        # -------------------------
        self.stack = QStackedLayout()

        self.home_page = Home_page(self.stack)
        self.info_page = Information_page(self.stack)

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.info_page)

        self.layout.addWidget(self.app_header)
        self.layout.addLayout(self.stack)

        self.setCentralWidget(self.container)


if __name__ == "__main__":

    # -------------------------
    # APPLICATION
    # -------------------------
    app = QApplication(sys.argv)

    # -------------------------
    # SINGLE INSTANCE LOCK
    # -------------------------
    APP_KEY = "anime_browser_single_instance"

    # attach lock to QApplication so it stays alive
    app.instance_lock = QSharedMemory(APP_KEY)

    if not app.instance_lock.create(1):
        QMessageBox.warning(
            None,
            "Already Running",
            "Another instance of Anime Browser is already running."
        )
        sys.exit(0)

    # -------------------------
    # ASYNC EVENT LOOP
    # -------------------------
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # -------------------------
    # APPLY STYLE
    # -------------------------
    apply_stylesheet(app, "dark_teal.xml")

    # -------------------------
    # SPLASH SCREEN
    # -------------------------
    splash_pix = QPixmap(resource_path("assets/splash.png"))
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)

    splash.show()
    QApplication.processEvents()

    # -------------------------
    # MAIN WINDOW
    # -------------------------
    window = Launcher()

    def start_main():
        window.show()
        splash.finish(window)

    QTimer.singleShot(2000, start_main)

    # -------------------------
    # START EVENT LOOP
    # -------------------------
    with loop:
        loop.run_forever()