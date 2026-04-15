from PySide6.QtWidgets import QHBoxLayout,QVBoxLayout,QWidget,QPushButton,QLabel,QGraphicsDropShadowEffect,QComboBox,QDialog,QButtonGroup,QLineEdit,QScrollArea,QSizePolicy,QProgressBar
from PySide6.QtCore import QSize,Signal,Qt,QTimer,QPoint,Qt
from PySide6.QtGui import QPixmap,QIcon
from qasync import asyncSlot
from func.search_req import anime_episode_info,anime_info,anime_search,top_anime,anime_page
from pages.flex import FlexLayout
from widgets.firstpage import AnimeCard,line,respanel