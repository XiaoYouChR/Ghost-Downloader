from PySide2.QtWidgets import QFileDialog

from View.settings_window.settings_window import config


def decidePathWin(parent, texiEdit, default=False):
    defaultPath = config.__getitem__("download-folder")
    filePath = QFileDialog.getExistingDirectory(parent, "选择文件夹", dir=defaultPath)
    if not filePath == "":
        if not default:
            texiEdit.setText(filePath)
        elif default:
            texiEdit.setText(filePath)
            config.__setitem__("download-folder", filePath)