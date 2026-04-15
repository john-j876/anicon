from PySide6.QtWidgets import QLabel




class app_header(QLabel):
      def __init__(self):
            super().__init__()

            self.setText('anicon')
            self.setFixedHeight(25)
            self.setStyleSheet('qproperty-alignment:AlignCenter;border-bottom:1px solid blue;background:black;color:white;font-size:13;padding:5pt')