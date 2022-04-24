from PySide2.QtWidgets import QLabel
from PySide2.QtGui import QPixmap


class PictureLabel(QLabel):
    def __init__(self, parent, pixmap: QPixmap):
        super(PictureLabel, self).__init__(parent)
        self.setScaledContents(True)
        self.setPixmap(pixmap)
