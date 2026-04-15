import sys
from pathlib import Path
from widgets.qt import QPushButton,QIcon,QLabel,Qt,QWidget,QPixmap,QUiLoader,QVBoxLayout,QSize,QHBoxLayout




def project_root():
    # PyInstaller support
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)

    # ALWAYS anchor to current file location safely
    return Path(__file__).resolve().parents[1]  # widgets/ -> anicode/

def resource_path(relative_path: str) -> str:
    return str(project_root() / relative_path)

##########################################################################
def scrollUi(self):
    # FIXED path (no duplicated "anicode")
    ui_path = Path(resource_path("widgets/qt/scroll_box.ui"))

    if not ui_path.exists():
        raise FileNotFoundError(f"Missing UI file: {ui_path}")

    loader = QUiLoader()
    widget = loader.load(str(ui_path), self)

    if widget is None:
        raise RuntimeError("UI failed to load")

    return widget

#############################################################################

def corousel_ui(self):
    path = Path(resource_path("widgets/qt/corousel_ui.ui"))

    loader = QUiLoader()

    w = loader.load(str(path),self)

    return w

#############################################################################
def inputField(self):
    # FIXED path (no duplicated "anicode")
    ui_path = Path(resource_path("widgets/qt/search_in.ui"))

    if not ui_path.exists():
        raise FileNotFoundError(f"Missing UI file: {ui_path}")

    loader = QUiLoader()
    widget = loader.load(str(ui_path), self)

    if widget is None:
        raise RuntimeError("UI failed to load")

    return widget

def line(self,color = 'blue'):
    line = QLabel()
    line.setMaximumHeight(3)
    line.setStyleSheet(('background:'+color+''))
    return line


###############################################################################
def respanel(self, anime_id, rank, score, title, image, story, episodes, duration, click_func):

    anime_id = anime_id
    click_func = click_func
    image = image
    story = story
    duration = duration
    episodes = episodes
    score = score
    rank = rank


    container = QWidget()
    container.setStyleSheet('background:black;border-bottom:1px solid grey')
    layout = QHBoxLayout()
    container.setLayout(layout)

    t_text = QPushButton()
    img = QLabel()
    



    pix = QPixmap(image).scaled(50,30,Qt.IgnoreAspectRatio,Qt.SmoothTransformation)
    img.setPixmap(pix)
    layout.addWidget(img)
    img.setFixedSize(50,30)
    img.setStyleSheet('background:teal;margin-left:4px')


    t_text.setText(title)
    layout.addWidget(t_text,1)
    t_text.setStyleSheet('border:none;font-size:10px;text-align:left')
    t_text.clicked.connect(lambda:click_func(
                anime_id,
                image,
                story,
                duration,
                episodes,
                score,
                rank
    ))

    return container

from PySide6.QtCore import QPropertyAnimation


class AnimeCard(QWidget):

    def __init__(self, anime_id, rank, score, title, image, story, episodes, duration, click_func):
        super().__init__()

        self.anime_id = anime_id
        self.click_func = click_func
        self.image = image
        self.story = story
        self.duration = duration
        self.episodes = episodes
        self.score = score
        self.rank = rank

        self.setFixedSize(160, 250)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        # -------------------------
        # POSTER BUTTON
        # -------------------------
        self.poster = QPushButton()
        self.poster.setFixedSize(148, 190)
        self.poster.setCursor(Qt.PointingHandCursor)

        pix = QPixmap(image).scaled(
            self.poster.size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )

        self.poster.setIcon(QIcon(pix))
        self.poster.setIconSize(self.poster.size())

        self.poster.setStyleSheet("""
        QPushButton{
            border:none;
            border-radius:8px;
            background:#222;
        }
        QPushButton:hover{
            background:#333;
        }
        """)

        # -------------------------
        # TITLE
        # -------------------------
        self.title = QLabel(title)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setWordWrap(True)

        self.title.setStyleSheet("""
        QLabel{
            font-size:11px;
            color:white;
        }
        """)
        layout.addWidget(self.poster)
        layout.addWidget(self.title)

        # click
        self.click_func = click_func

        self.poster.clicked.connect(
            lambda: self.click_func(
                self.anime_id,
                self.image,
                self.story,
                self.duration,
                self.episodes,
                self.score,
                self.rank
            )
        )
        # hover animation (Qt way)
        self.anim = QPropertyAnimation(self, b"size")
        self.anim.setDuration(120)

    # -------------------------
    # HOVER EFFECT (REAL QT WAY)
    # -------------------------
    def enterEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(self.size())
        self.anim.setEndValue(QSize(168, 260))
        self.anim.start()

    def leaveEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(self.size())
        self.anim.setEndValue(QSize(160, 250))
        self.anim.start()