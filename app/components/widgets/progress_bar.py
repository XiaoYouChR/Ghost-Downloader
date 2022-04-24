from PySide2.QtWidgets import QWidget


# from PySide2.QtCore import QPropertyAnimation, QEasingCurve

class MyProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MyProgressBar")
        self.setStyleSheet("* {\n"
                           "    border: 1px solid rgb(100, 160, 220);\n"
                           "    border-radius: 10px;"
                           "}")

        self.progresser = QWidget(self)
        self.progresser.setObjectName("progresser")
        self.progresser.setStyleSheet("  background:rgb(100, 160, 220);")
        self.progresser.move(0, 0)
        self.resize(0, self.height())

        self.value = 0
        print(type(self.value))

        self.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.progresser.resize(self.value * self.width() / 100, self.height())

    def setValue(self, value):
        self.value = value
        self.progresser.resize(self.value * self.width() / 100, self.height())
        # resizeAction(self.progresser, self.value * self.width() / 100, self.height())
