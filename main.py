import sys
import os
import shutil
from PyQt5.QtWidgets import *
import logging

from modules import *


class Main(QMainWindow):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        self.setupUi(self)

    def setupUi(self, MainWindow):
        self.setWindowTitle("CopyPaster")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        self.save_data = UserData.readSaveData()
        self.stackedWidget = QStackedWidget()
        self.main_widget = QWidget()
        self.main_layout = QGridLayout()
        self.header = QLabel("Скопировать файлы из папки 1 в папку 2.")
        self.from_header = QLabel("Копировать из: ")
        self.to_header = QLabel("Копировать в: ")
        self.from_line = QLineEdit()
        self.from_line.setPlaceholderText("Копировать из...")
        self.from_line.setText(self.save_data["from_folder"])
        self.from_choose_btn = QPushButton("Изменить")
        self.from_box_text = QLabel("Выбрать папку для перемещения")
        self.from_choose_list = None
        try:
            self.dirlist = []
            for filename in os.listdir(self.save_data["from_folder"]):
                full_path = os.path.join(self.save_data["from_folder"], filename)
                if os.path.isdir(full_path):
                    self.dirlist.append((filename, os.path.getmtime(full_path)))
            self.dirlist.sort(key=lambda tpl: tpl[1], reverse=True)
            self.from_choose_list = QComboBox()
            self.from_choose_list.addItems([tpl[0] for tpl in self.dirlist])
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", "Невозможно прочитать директорию 1.", QMessageBox.Ok)
        self.to_line = QLineEdit()
        self.to_line.setPlaceholderText("Копировать в...")
        self.to_line.setText(self.save_data["to_folder"])
        self.to_choose_btn = QPushButton("Изменить")
        self.copy_btn = QPushButton("Скопировать")
        self.main_layout.addWidget(self.header, 0, 0, alignment=Qt.AlignCenter)
        self.main_layout.addWidget(self.from_header, 1, 0)
        self.main_layout.addWidget(self.from_line, 1, 1)
        self.main_layout.addWidget(self.from_choose_btn, 1, 2)
        if self.from_choose_list:
            self.main_layout.addWidget(self.from_choose_list, 2, 1, 1, 2)
        self.main_layout.addWidget(self.from_box_text, 2, 0, 1, 1)
        self.main_layout.addWidget(self.to_header, 3, 0)
        self.main_layout.addWidget(self.to_line, 3, 1)
        self.main_layout.addWidget(self.to_choose_btn, 3, 2)
        self.main_layout.addWidget(self.copy_btn, 4, 0, 1, 3)

        self.from_choose_btn.clicked.connect(self.__fromButtonClicked)
        self.to_choose_btn.clicked.connect(self.__toButtonClicked)
        self.copy_btn.clicked.connect(self.__copyProcess)


        self.logTextBox = QTextEditLogger(self)
        self.logTextBox.setFormatter(
            logging.Formatter(
                '%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s'))
        logging.getLogger().addHandler(self.logTextBox)
        logging.getLogger().setLevel(logging.INFO)

        self.main_layout.addWidget(self.logTextBox.widget, 5, 0, 1, 3)

        self.main_widget.setLayout(self.main_layout)
        self.stackedWidget.addWidget(self.main_widget)
        self.stackedWidget.setCurrentIndex(0)
        self.setCentralWidget(self.stackedWidget)


    def __fromButtonClicked(self):
        self.from_destination = QFileDialog.getExistingDirectory()
        if self.from_destination:
            self.from_line.setText(self.from_destination)
            UserData.changeSaveData(from_path=self.from_destination)
        try:
            self.dirlist = []
            for filename in os.listdir(self.from_destination):
                full_path = os.path.join(self.from_destination, filename)
                if os.path.isdir(full_path):
                    self.dirlist.append((filename, os.path.getmtime(full_path)))
            self.dirlist.sort(key=lambda tpl: tpl[1], reverse=True)
            self.from_choose_list = QComboBox()
            self.from_choose_list.addItems([tpl[0] for tpl in self.dirlist])
            self.main_layout.addWidget(self.from_choose_list, 2, 1, 1, 2)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", "Невозможно прочитать директорию 1.", QMessageBox.Ok)

    def __toButtonClicked(self):
        self.to_destination = QFileDialog.getExistingDirectory()
        if self.to_destination:
            self.to_line.setText(self.to_destination)
            UserData.changeSaveData(to_path=self.to_destination)

    def __copyProcess(self):
        self.from_destination = self.save_data["from_folder"]
        self.to_destination = self.to_line.text()
        self.from_destination = os.path.join(self.from_destination, self.from_choose_list.currentText())
        try:
            for f in os.listdir(self.to_destination):
                os.remove(os.path.join(self.to_destination, f))
                logging.info(f"Deleted file {self.to_destination}/{f}")
            for f in os.listdir(self.from_destination):
                shutil.copy(os.path.join(self.from_destination, f), os.path.join(self.to_destination, f))
                logging.info(f"Copied file {f}")
            UserData.changeSaveData(from_path=self.save_data["from_folder"], to_path=self.save_data["to_folder"])
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e), QMessageBox.Ok)
            logging.error(f"Error: {str(e)}")


def main():
    if not UserData.checkIfSaveExists():
        UserData.generateEmptySave()
    app = QApplication(sys.argv)
    win = Main()
    win.show()
    app.exec_()

if __name__ == "__main__":
    main()