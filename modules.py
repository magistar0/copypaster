import logging
import os
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class QTextEditLogger(logging.Handler, QObject):
    appendPlainText = pyqtSignal(str)
    def __init__(self, parent):
        super().__init__()
        QObject.__init__(self)
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)
        self.appendPlainText.connect(self.widget.appendPlainText)

    def emit(self, record):
        msg = self.format(record)
        self.appendPlainText.emit(msg)


class UserData(object):
    save_dir = os.getenv("LOCALAPPDATA") + "/CopyPaster"
    save_filename = "/user.sav"
    default_to_path = os.getenv("APPDATA").replace("\\", "/") + "/.minecraft/mods"

    def checkIfSaveExists() -> bool:
        return os.path.exists(UserData.save_dir + UserData.save_filename)

    def generateEmptySave() -> None:
        if not os.path.exists(UserData.save_dir):
            os.makedirs(UserData.save_dir)
        save_data = {"from_folder": None, "to_folder": UserData.default_to_path}
        with open(UserData.save_dir + UserData.save_filename, "w", encoding="utf-8") as sf:
            sf.write(json.dumps(save_data, ensure_ascii=False))

    def readSaveData() -> dict:
        with open(UserData.save_dir + UserData.save_filename, "r", encoding="utf-8") as sf:
            return json.loads(sf.read())
        
    def changeSaveData(from_path="", to_path=default_to_path) -> None:
        save_data = UserData.readSaveData()
        save_data["from_folder"] = from_path.replace("\\", "/")
        save_data["to_folder"] = to_path.replace("\\", "/")
        with open(UserData.save_dir + UserData.save_filename, "w", encoding="utf-8") as sf:
            sf.write(json.dumps(save_data, ensure_ascii=False))