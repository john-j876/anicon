from pages import (
    QLabel, QVBoxLayout, asyncSlot, QWidget, Qt, line, respanel, QPixmap, QIcon,
    FlexLayout, AnimeCard, QSizePolicy, QScrollArea, QPoint, QPushButton, QHBoxLayout,
    anime_episode_info, anime_info
)

from widgets.firstpage import inputField, corousel_ui
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QProgressBar
import qtawesome as qta


# -------------------------------
# Utility to clear layouts
# -------------------------------
def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()


# -------------------------------
# Episode panel
# -------------------------------
def selectpanel(self, title=None, img=None, id=None):

    container = QWidget()
    container.setStyleSheet("background:black;border-bottom:1px solid grey")

    layout = QHBoxLayout()
    container.setLayout(layout)

    ep_label = QLabel(f"episode {id}")
    ep_label.setStyleSheet("color:teal;margin-left:4px")

    if not title:
        title = 'seems to be empty 😊'
        ep_label.hide()

    title_btn = QPushButton(title)
    title_btn.setEnabled(False)
    title_btn.setStyleSheet("border:none;font-size:10px;text-align:left")

    download_btn = QPushButton()
    download_btn.setIcon(qta.icon("fa5s.download"))
    download_btn.clicked.connect(lambda: self.ep_data(episode=id))

    layout.addWidget(ep_label)
    layout.addWidget(title_btn, 1)
    layout.addWidget(download_btn)

    return container


# -------------------------------
# Information Page
# -------------------------------
class Information_page(QWidget):

    def __init__(self, stack):

        super().__init__()

        self.stack = stack
        self.img = None

        # -----------------------
        # back button
        # -----------------------
        self.back = QPushButton("<")
        self.back.setFixedSize(45, 20)
        self.back.clicked.connect(self.goBack)

        # -----------------------
        # carousel
        # -----------------------
        self.corousel = QLabel()
        self.corousel.setFixedHeight(200)
        self.corousel.setAlignment(Qt.AlignCenter)

        # -----------------------
        # story area
        # -----------------------
        self.storyscroll = QScrollArea()
        self.storycon = QWidget()
        self.storylay = QVBoxLayout()

        self.storycon.setLayout(self.storylay)
        self.storyscroll.setWidget(self.storycon)
        self.storyscroll.setWidgetResizable(True)
        self.storyscroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.storylay.setContentsMargins(0, 0, 0, 0)
        self.storylay.addStretch()

        # -----------------------
        # episodes list
        # -----------------------
        self.contentscroll = QScrollArea()
        self.contentcon = QWidget()
        self.contentlay = QVBoxLayout()

        self.contentcon.setLayout(self.contentlay)
        self.contentscroll.setWidget(self.contentcon)
        self.contentscroll.setWidgetResizable(True)

        # -----------------------
        # LOADING BAR (BOTTOM)
        # -----------------------
        self.loading_bar = QProgressBar()
        self.loading_bar.setMaximum(0)  # infinite loader
        self.loading_bar.setTextVisible(False)
        self.loading_bar.hide()

        # -----------------------
        # main layout
        # -----------------------
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self.corousel, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.storyscroll)
        self.layout.addWidget(self.contentscroll, 1)
        self.layout.addWidget(self.loading_bar)

        self.layout.setContentsMargins(0, 10, 0, 0)

    # -------------------------------
    # Resize
    # -------------------------------
    def resizeEvent(self, event):
        super().resizeEvent(event)

        if self.img:
            self.setcorousel(self.img)

        self.posBtn()

        self.corousel.setFixedWidth(self.width()/1.2 if self.width() > 701 else 700)

    # -------------------------------
    # back button position
    # -------------------------------
    def posBtn(self):
        self.back.setParent(self)
        self.back.move(0, 10)

    # -------------------------------
    # set data
    # -------------------------------
    def set_data(self, anime_id, image, story, duration, episodes, score, rank):

        clear_layout(self.storylay)
        clear_layout(self.contentlay)

        story_label = QLabel(story)
        story_label.setWordWrap(True)

        self.storylay.addWidget(story_label)

        self.setcorousel(image)

        # load episodes
        self.anime_intel(anime_id)

    # -------------------------------
    # set image
    # -------------------------------
    def setcorousel(self, img):
        if img:
            pix = QPixmap(img).scaled(
                self.corousel.width(),
                200,
                Qt.IgnoreAspectRatio,
                Qt.SmoothTransformation,
            )
            self.corousel.setPixmap(pix)
        else:
            self.corousel.setText('failed')

    # -------------------------------
    # fetch episodes (FIXED LOADING STATE)
    # -------------------------------
    @asyncSlot()
    async def anime_intel(self, id):

        self.loading_bar.show()

        clear_layout(self.contentlay)

        res = await anime_info(id)

        for data in res:
            panel = selectpanel(
                self,
                data["title"],
                data["image"],
                data["id"],
            )
            self.contentlay.addWidget(panel)

        self.contentlay.addStretch()

        self.loading_bar.hide()

    # -------------------------------
    # go back
    # -------------------------------
    def goBack(self):
        self.stack.setCurrentWidget(self.stack.widget(0))