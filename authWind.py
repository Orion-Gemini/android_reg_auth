# authWind.py
import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
import pymysql

# Импортируем класс TabletWindow из отдельного файла tablet.py
try:
    # Убедитесь, что TabletWindow импортируется корректно
    from tablet import TabletWindow, Ui_MainWindow as Tablet_Ui_MainWindow
except ImportError:
    print("Ошибка: Не найден файл 'tablet.py' или класс TabletWindow. Убедитесь, что tablet.py находится рядом.")
    sys.exit(1)


# --- СГЕНЕРИРОВАННЫЙ КЛАСС ИНТЕРФЕЙСА АВТОРИЗАЦИИ (Ui_MainWindow) ---
class Ui_MainWindow(object):
    # ... (весь ваш сгенерированный код setupUi и retranslateUi с QLineEdit и центрированием) ...
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(290, 410, 231, 41))
        self.pushButton.setObjectName("pushButton")

        self.textLogin = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.textLogin.setGeometry(QtCore.QRect(260, 190, 291, 41))
        self.textLogin.setObjectName("textLogin")

        self.textPassword = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.textPassword.setGeometry(QtCore.QRect(260, 300, 291, 41))
        self.textPassword.setObjectName("textPassword")
        self.textPassword.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(260, 140, 221, 31))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(260, 250, 221, 31))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(260, 40, 281, 51))
        self.label_3.setObjectName("label_3")
        self.label_3.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "Войти"))
        self.label.setText(_translate("MainWindow",
                                      "<html><head/><body><p><span style=\" font-size:12pt;\">Логин</span></p></body></html>"))
        self.label_2.setText(_translate("MainWindow",
                                        "<html><head/><body><p><span style=\" font-size:12pt;\">Пароль</span></p></body></html>"))
        self.label_3.setText(_translate("MainWindow",
                                        "<html><head/><body><p><span style=\" font-size:16pt; font-weight:600; color:#aaaa7f;\">Добро пожаловать</span></p></body></html>"))


# --- КЛАСС ЛОГИКИ АВТОРИЗАЦИИ (ТОЛЬКО ПРОВЕРКА И ПЕРЕХОД) ---
class AuthWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.check_login)
        self.tablet_window = None

    def check_login(self):
        login = self.ui.textLogin.text().strip()
        password = self.ui.textPassword.text().strip()

        if not login or not password:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, введите логин и пароль.")
            return

        # Проверка в БД
        if self.authenticate_user(login, password):
            self.open_tablet_window(login)
        else:
            QMessageBox.critical(self, "Ошибка входа", "Неверный логин или пароль.")

    def authenticate_user(self, login, password):
        """Подключается к БД и проверяет логин/пароль в admin_director."""
        conn = None
        try:
            conn = pymysql.connect(
                host='localhost',
                port=3306,
                user='root',
                password='root',  # <-- ЗАМЕНИТЕ НА ВАШ ПАРОЛЬ
                database='hotel_db'
            )
            cursor = conn.cursor()

            query = "SELECT login FROM admin_director WHERE login = %s AND password = %s"
            cursor.execute(query, (login, password))

            return cursor.fetchone() is not None

        except Exception as e:
            # Обязательно выводим ошибку подключения, чтобы пользователь увидел причину краха
            print(f"Критическая ошибка подключения к БД: {e}")
            QMessageBox.critical(self, "Ошибка БД",
                                 f"Не удалось подключиться к базе данных: {e}. Проверьте MySQL-сервер и настройки.")
            return False
        finally:
            if conn:
                conn.close()

    def open_tablet_window(self, username):
        """Создает и показывает второе окно, передавая ссылку на себя."""
        if self.tablet_window is None:
            # Передаем ссылку на текущее окно (self)
            self.tablet_window = TabletWindow(username, parent_window=self)

        self.tablet_window.show()
        self.hide()


# --- ЗАПУСК ПРИЛОЖЕНИЯ ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    auth_window = AuthWindow()
    auth_window.show()
    sys.exit(app.exec())