import core
import design
import sys
import pickle
import threading
import vk_api
import requests
from datetime import datetime
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets, QtGui
from vk_api.exceptions import BadPassword, Captcha
from bs4 import BeautifulSoup


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
                 " (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"


def vk_user_data_is_currect(vk_login, vk_password):
    session = vk_api.VkApi(vk_login, vk_password)
    try:
        session.auth()
        return True
    except BadPassword:
        return False
    except Captcha:
        return False


def url_is_good(url):
    page = requests.get(url).text
    if "body error-404" in page:
        return False
    return True


def world_number_is_correct(url, n):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, features="lxml")
    worlds_num = len(soup.find_all("tr", {"style": 'cursor: pointer;'}))
    if worlds_num < n:
        return False
    return True


class Applicaion(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setupUi(self)
        self._load_state()
        self.lineEdit_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pushButton_start.clicked.connect(self.start)
        self.checkBox_toggle_password.stateChanged.connect(self.toggle_password)
        self.log = QPlainTextEditLogger(self.plainTextEdit_log)


    def start(self):
        self._start_button_toggle()

        def main():
            self.log("Проверка введенных данных")
            login = self.lineEdit_login.text()
            password = self.lineEdit_password.text()
            url = self.lineEdit_url.text()
            name = self.lineEdit_name.text()
            world_number = int(self.spinBox_world_number.value())
            once = self.radioButton_vote_once.isChecked()
            if self._data_is_good(login, password, url):
                self.log("Данные верны")
                thread = threading.Thread(target=core.main,
                                          args=(login, password, url, name, world_number,
                                                once, self.log))
                thread.setDaemon(True)
                thread.start()
                thread.join()
                self._start_button_toggle()
        t = threading.Thread(target=main)
        t.setDaemon(True)
        t.start()

    def _data_is_good(self, login, password, url):
        if not login or not password or not url:
            self.log("Введены не все данные!")
            return False
        if not vk_user_data_is_currect(login, password):
            self.log("Введен неправильный логин/пароль!")
            return False
        if "mmotop.ru/servers/" not in url or not url_is_good(url):
            self.log("Введена неверная ссылка на сервер!")
            return False
        if not world_number_is_correct(url, self.spinBox_world_number.value()):
            self.log("Указан неверный мир!")
            return False
        return True

    def _start_button_toggle(self):
        def toggle():
            if self.pushButton_start.isEnabled():
                self.pushButton_start.setEnabled(False)
            else:
                self.pushButton_start.setEnabled(True)
        t = threading.Thread(target=toggle)
        t.setDaemon(True)
        t.start()

    def _save_state(self):
        remember = self.checkBox_remember.isChecked()
        if remember:
            login = self.lineEdit_login.text()
            password = self.lineEdit_password.text()
            url = self.lineEdit_url.text()
            name = self.lineEdit_name.text()
            world_number = self.spinBox_world_number.value()

            vote_once = self.radioButton_vote_once.isChecked()
            vote_cycle = self.radioButton_vote_cycle.isChecked()
            data = {
                "login": login,
                "password": password,
                "url": url,
                "name": name,
                "world_number": world_number,
                "remember": remember,
                "vote_once": vote_once,
                "vote_cycle": vote_cycle
            }
        else:
            data = {
                "remember": remember
            }
        with open("cache.bin", "wb") as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    def _load_state(self):
        try:
            with open("cache.bin", "rb") as f:
                data = pickle.load(f)
                remember = data["remember"]
                if remember:
                    self.lineEdit_login.setText(data["login"])
                    self.lineEdit_password.setText(data["password"])
                    self.lineEdit_url.setText(data["url"])
                    self.lineEdit_name.setText(data["name"])
                    self.spinBox_world_number.setValue(data["world_number"])
                    self.checkBox_remember.setChecked(remember)
                    if data["vote_once"] == "True":
                        self.radioButton_vote_once.setEnabled(True)
                    else:
                        self.radioButton_vote_cycle.setEnabled(True)
        except FileNotFoundError:
            pass

    def closeEvent(self, event):
        self._save_state()

    def toggle_password(self):
        if self.checkBox_toggle_password.isChecked():
            self.lineEdit_password.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.lineEdit_password.setEchoMode(QtWidgets.QLineEdit.Password)


class QPlainTextEditLogger:
    def __init__(self, widget):
        self.widget = widget

    def __call__(self, msg):
        now = datetime.now().strftime("%H:%M:%S")
        self.widget.appendPlainText(now + "  " + str(msg))
        QApplication.processEvents()

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Applicaion()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()