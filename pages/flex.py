from PySide6.QtWidgets import QLayout
from PySide6.QtCore import QRect, QSize, Qt


class FlexLayout(QLayout):

    def __init__(self, parent=None, margin=10, spacing=10):
        super().__init__(parent)

        self.item_list = []
        self.setSpacing(spacing)
        self.setContentsMargins(margin, margin, margin, margin)

    def addItem(self, item):
        self.item_list.append(item)

    def count(self):
        return len(self.item_list)

    def itemAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list.pop(index)
        return None

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.do_layout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.do_layout(rect, False)

    def sizeHint(self):
        return QSize(400, 300)

    def do_layout(self, rect, test_only):

        spacing = self.spacing()
        x = rect.x()
        y = rect.y()

        row = []
        row_width = 0
        row_height = 0

        for item in self.item_list:

            size = item.sizeHint()
            next_width = row_width + size.width() + spacing

            if next_width > rect.width() and row:
                self.layout_row(row, rect, row_width, row_height, y, test_only)

                y += row_height + spacing
                row = []
                row_width = 0
                row_height = 0

            row.append(item)
            row_width += size.width() + spacing
            row_height = max(row_height, size.height())

        if row:
            self.layout_row(row, rect, row_width, row_height, y, test_only)

        return y + row_height - rect.y()

    def layout_row(self, row, rect, row_width, row_height, y, test_only):

        spacing = self.spacing()

        total_width = sum(item.sizeHint().width() for item in row) + spacing*(len(row)-1)

        x = rect.x() + (rect.width() - total_width) // 2

        for item in row:

            size = item.sizeHint()

            if not test_only:
                item.setGeometry(QRect(x, y, size.width(), size.height()))

            x += size.width() + spacing