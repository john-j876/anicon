from pages import (
    QLabel, QVBoxLayout, asyncSlot, QWidget, QLineEdit, Qt, line, respanel,
    FlexLayout, AnimeCard, QSizePolicy, QScrollArea, QPoint,
    anime_search, top_anime, anime_page
)

from widgets.firstpage import inputField, corousel_ui

from PySide6.QtCore import QTimer
from PySide6.QtGui import QResizeEvent, QPixmap
from PySide6.QtWidgets import QProgressBar


class Home_page(QWidget):

    def __init__(self, stack):
        super().__init__()
        self.setMinimumSize(700, 500)

        self.stack = stack

        # ---------------- STATE ----------------
        self.page = 1
        self.loading = False
        self.loaded_ids = set()   # prevents duplicate anime cards
        self.search_active = False

        # ---------------- UI ----------------
        self.inputfield = inputField(self).findChild(QLineEdit, 'search_field')
        self.corousel = corousel_ui(self).findChild(QLabel, 'corousel')

        # ---------------- SEARCH BOX ----------------
        self.search_box = QScrollArea()
        self.search_widget = QWidget()
        self.search_lay = QVBoxLayout()

        self.search_lay.setContentsMargins(5,5,5,5)
        self.search_lay.setSpacing(6)

        self.search_widget.setLayout(self.search_lay)

        self.search_box.setWidget(self.search_widget)
        self.search_box.setWidgetResizable(True)
        self.search_box.setStyleSheet('background:transparent')
        self.search_box.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.search_box.hide()

        # ---------------- MAIN SCROLL ----------------
        self.scroll_box = QScrollArea()
        self.scroll_widget = QWidget()

        self.flow = FlexLayout()

        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setContentsMargins(0,0,0,0)
        self.scroll_layout.setSpacing(10)

        self.scroll_layout.addLayout(self.flow)

        self.loading_bar = QProgressBar()
        self.loading_bar.setMaximum(0)
        self.loading_bar.setTextVisible(False)
        self.loading_bar.hide()

        self.scroll_layout.addWidget(self.loading_bar)

        self.scroll_widget.setLayout(self.scroll_layout)

        self.scroll_box.setWidget(self.scroll_widget)
        self.scroll_box.setWidgetResizable(True)
        self.scroll_box.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # ---------------- SEARCH SIZE ----------------
        self.search_box.setFixedSize(self.inputfield.width(),250)
        self.inputfield.setFixedWidth(350)

        # ---------------- LAYOUT ----------------
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self.inputfield, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.corousel, alignment=Qt.AlignCenter)
        self.layout.addSpacing(10)
        self.layout.addWidget(line(self,color='gray'))
        self.layout.addWidget(self.scroll_box,1)

        self.layout.setContentsMargins(0,9,0,0)

        # ---------------- SEARCH ----------------
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.run_search)

        self.inputfield.textChanged.connect(self.debounce_search)

        # ---------------- CAROUSEL ----------------
        self.corousel_res = []
        self.corousel_index = 0

        QTimer.singleShot(0, self.updateCorousel)

        # ---------------- SCROLL ----------------
        self.scroll_box.verticalScrollBar().valueChanged.connect(self.check_scroll)

        QTimer.singleShot(0, self.load_page)

    # --------------------------------------------------
    # RESIZE
    # --------------------------------------------------
    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)

        self.search_box.setParent(self)

        pos = self.inputfield.mapTo(self, QPoint(0,self.inputfield.height()+4))
        self.search_box.setFixedWidth(self.inputfield.width())
        self.search_box.move(pos)

        self.corousel.setFixedWidth(self.width()/1.3)

    # --------------------------------------------------
    # SEARCH
    # --------------------------------------------------
    def debounce_search(self, txt):
        self.search_timer.start(500)

    def showHide(self):
        if len(self.inputfield.text()) > 2:
            self.search_box.show()
            self.search_active = True
        else:
            self.search_box.hide()
            self.search_active = False

    @asyncSlot()
    async def run_search(self):

        txt = self.inputfield.text().strip()

        if len(txt) < 3:
            self.search_box.hide()
            self.search_active = False
            return

        results = await anime_search(txt)

        while self.search_lay.count():
            item = self.search_lay.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        for data in results:

            self.search_lay.addWidget(
                respanel(
                    self,
                    data['id'],
                    data['rank'],
                    data['score'],
                    data['title'],
                    data['image'],
                    data['story'],
                    data['episodes'],
                    data['duration'],
                    self.pass_data
                )
            )

        self.showHide()

    # --------------------------------------------------
    # CAROUSEL
    # --------------------------------------------------
    @asyncSlot()
    async def updateCorousel(self):

        self.corousel_res = await top_anime()
        self.corousel_index = 0

        self.corousel_timer = QTimer(self)
        self.corousel_timer.timeout.connect(self.next_slide)
        self.corousel_timer.start(4000)

    def next_slide(self):

        if not self.corousel_res:
            return

        data = self.corousel_res[self.corousel_index]

        self.corousel.setPixmap(
            QPixmap(data['image']).scaled(
                self.corousel.width(),
                self.corousel.height(),
                Qt.IgnoreAspectRatio,
                Qt.SmoothTransformation
            )
        )

        self.corousel.setAlignment(Qt.AlignCenter)

        self.corousel_index += 1

        if self.corousel_index >= len(self.corousel_res):
            self.corousel_index = 0

    # --------------------------------------------------
    # MAIN FEED
    # --------------------------------------------------
    @asyncSlot()
    async def load_page(self):

        if self.loading:
            return

        self.loading = True
        self.loading_bar.show()

        res = await anime_page(self.page)

        for data in res:

            if data["id"] in self.loaded_ids:
                continue

            self.loaded_ids.add(data["id"])

            card = AnimeCard(
                data['id'],
                data['rank'],
                data['score'],
                data['title'],
                data['image'],
                data['story'],
                data['episodes'],
                data['duration'],
                self.pass_data
            )

            self.flow.addWidget(card)

        self.page += 1

        self.loading_bar.hide()
        self.loading = False

    # --------------------------------------------------
    # SCROLL TRIGGER
    # --------------------------------------------------
    def check_scroll(self):

        if self.search_active:
            return

        bar = self.scroll_box.verticalScrollBar()

        if bar.value() > bar.maximum() - 200 and not self.loading:
            self.load_page()

    # --------------------------------------------------
    # DATA
    # --------------------------------------------------
    def pass_data(self, anime_id, image, story, duration, episodes, score, rank):

        info_page = self.stack.widget(1)

        info_page.set_data(anime_id, image, story, duration, episodes, score, rank)

        def direct():
            self.stack.setCurrentWidget(info_page)

        QTimer.singleShot(1000, direct)

        self.inputfield.setText('')