from PySide2.QtWidgets import QWidget, QFrame
from PySide2.QtCore import QPropertyAnimation, QEasingCurve, Signal, QRect

class MyProgressBar(QFrame):

    changeValue = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MyProgressBar")
        self.setStyleSheet("* {\n"
                           "    border: 1px solid rgb(230, 230, 230);\n"
                           "    border-radius: 10px;"
                           "}")

        self.progresser = QWidget(self)
        self.progresser.setObjectName("progresser")
        self.progresser.setStyleSheet("  background:rgb(255, 255, 255);")
        self.progresser.move(0, 0)
        self.progresser.resize(0, self.height())

        self.animation = QPropertyAnimation(self.progresser, b"geometry")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)

        self.value = 100

        self.progresser.resize(self.value * self.width() / 100, self.height())

        self.changeValue.connect(self.__setValue)

        self.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.progresser.resize(self.value * self.width() / 100, self.height())

    def setValue(self,value):
        self.changeValue.emit(value)

    def __setValue(self, value):
        self.animation.stop()
        self.value = value
        self.animation.setEndValue(QRect(0, 0, self.value * self.width() / 100, self.height()))
        self.animation.start()