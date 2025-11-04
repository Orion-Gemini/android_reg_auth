# tablet.py
import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QMessageBox,
    QAbstractItemView
)
from PyQt6.QtCore import Qt
import pymysql
from pymysql import cursors


# --- 1. КЛАСС ИНТЕРФЕЙСА (С масштабированием и кнопками действий) ---
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 700)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)

        # Главный вертикальный менеджер
        self.main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # Верхний блок (Заголовок/ФИО)
        self.header_widget = QtWidgets.QWidget(parent=self.centralwidget)
        self.header_layout = QtWidgets.QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(0, 0, 0, 0)

        self.label = QtWidgets.QLabel(parent=self.header_widget)
        self.label.setMinimumHeight(40)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.FIO_persom = QtWidgets.QLabel(parent=self.header_widget)
        self.FIO_persom.setMinimumHeight(40)
        self.FIO_persom.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)

        self.header_layout.addWidget(self.label, 1)
        self.header_layout.addWidget(self.FIO_persom, 0)
        self.main_layout.addWidget(self.header_widget)

        # Таблица (растягивается)
        self.tableView = QtWidgets.QTableView(parent=self.centralwidget)
        self.main_layout.addWidget(self.tableView)

        # --- НИЖНИЙ БЛОК (КНОПКИ ДЕЙСТВИЙ) ---
        self.button_widget = QtWidgets.QWidget(parent=self.centralwidget)
        self.button_layout = QtWidgets.QHBoxLayout(self.button_widget)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setSpacing(10)

        # 1. Кнопка "Обновить"
        self.pushButton = QtWidgets.QPushButton(parent=self.button_widget)
        self.pushButton.setFixedWidth(150)
        self.button_layout.addWidget(self.pushButton)

        # 2. Кнопка "Редактировать"
        self.pushButton_edit = QtWidgets.QPushButton(parent=self.button_widget)
        self.pushButton_edit.setFixedWidth(150)
        self.button_layout.addWidget(self.pushButton_edit)

        # 3. Кнопка "Удалить"
        self.pushButton_delete = QtWidgets.QPushButton(parent=self.button_widget)
        self.pushButton_delete.setFixedWidth(150)
        self.button_layout.addWidget(self.pushButton_delete)

        # Распорка для прижатия кнопок влево
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                       QtWidgets.QSizePolicy.Policy.Minimum)
        self.button_layout.addItem(spacer)

        self.main_layout.addWidget(self.button_widget)

        # Меню и статус бар
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1000, 26))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Система управления гостиницей"))
        self.pushButton.setText(_translate("MainWindow", "Обновить"))
        self.pushButton_edit.setText(_translate("MainWindow", "Редактировать"))
        self.pushButton_delete.setText(_translate("MainWindow", "Удалить"))
        self.label.setText(_translate("MainWindow",
                                      "<html><head/><body><p><span style=\" font-size:20pt; font-weight:600; color:#00aa7f;\">Система управления гостиницей</span></p></body></html>"))
        self.FIO_persom.setText(_translate("MainWindow", "Тут фио"))


# --- 2. КЛАСС ЛОГИКИ ОСНОВНОГО ОКНА ---
class TabletWindow(QMainWindow):

    def __init__(self, username, parent_window=None):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.username = username
        self.parent_window = parent_window

        self.ui.FIO_persom.setText(f"Пользователь: {self.username.upper()}")

        # --- ИСПРАВЛЕННЫЕ НАСТРОЙКИ ВЫДЕЛЕНИЯ ---
        # Выделять целые строки
        self.ui.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        # Выделять только одну строку
        self.ui.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.ui.tableView.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        # Подключение кнопок
        self.ui.pushButton.clicked.connect(self.load_booking_data)
        self.ui.pushButton_edit.clicked.connect(self.edit_selected_booking)
        self.ui.pushButton_delete.clicked.connect(self.delete_selected_booking)

        self.load_booking_data()

    def closeEvent(self, event):
        """Возвращение к окну авторизации при закрытии."""
        if self.parent_window is not None:
            self.parent_window.show()
        event.accept()

    def get_selected_booking_id(self):
        """Возвращает ID брони выбранной строки. Выводит предупреждение, если строка не выбрана."""
        # Получаем список выбранных индексов строк
        selected_indexes = self.ui.tableView.selectionModel().selectedRows()

        if not selected_indexes:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, выберите строку для действия (Редактировать/Удалить).")
            return None

        # ID находится в первой колонке (индекс 0)
        index = selected_indexes[0].siblingAtColumn(0)

        return self.ui.tableView.model().data(index, Qt.ItemDataRole.DisplayRole)

    def edit_selected_booking(self):
        booking_id = self.get_selected_booking_id()
        if booking_id:
            # Логика открытия окна редактирования
            QMessageBox.information(self, "Действие", f"Открытие формы редактирования для брони ID: {booking_id}")

    def delete_selected_booking(self):
        booking_id = self.get_selected_booking_id()
        if not booking_id:
            return

        reply = QMessageBox.question(self, 'Подтверждение',
                                     f"Вы уверены, что хотите удалить бронь ID: {booking_id}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            conn = None
            try:
                # ВАЖНО: ЗАМЕНИТЕ ПАРОЛЬ НА ВАШ АКТУАЛЬНЫЙ
                conn = pymysql.connect(host='localhost', port=3306, user='root',
                                       password='YOUR_DB_PASSWORD', database='hotel_db')
                cursor = conn.cursor()

                # ЛОГИКА УДАЛЕНИЯ ИЗ БД
                query = "DELETE FROM booking WHERE id = %s"
                cursor.execute(query, (booking_id,))
                conn.commit()
                QMessageBox.information(self, "Успех", f"Бронь ID: {booking_id} успешно удалена.")
                self.load_booking_data()  # Обновляем таблицу
            except Exception as e:
                QMessageBox.critical(self, "Ошибка БД", f"Не удалось удалить бронь: {e}")
            finally:
                if conn:
                    conn.close()

    def load_booking_data(self):
        """Загружает данные бронирования с расширенным набором колонок."""
        conn = None
        try:
            conn = pymysql.connect(
                host='localhost',
                port=3306,
                user='root',
                password='root',  # <-- ЗАМЕНИТЕ НА ВАШ ПАРОЛЬ
                database='hotel_db',
                cursorclass=pymysql.cursors.DictCursor
            )

            cursor = conn.cursor()

            # SQL-ЗАПРОС
            query = """
            SELECT 
                b.id, 
                CONCAT(c.surname, ' ', c.name, ' ', c.lastname) AS full_name, 
                c.passport, 
                b.date_in, 
                b.date_out, 
                cat.name AS category_name, 
                r.number AS room_number, 
                s.name AS status_name,
                b.purpose
            FROM 
                booking b
            JOIN clients c ON b.clientId = c.id
            JOIN rooms r ON b.roomId = r.id
            JOIN category cat ON r.categoryId = cat.id
            JOIN status s ON r.statusId = s.id
            ORDER BY b.id DESC;
            """

            cursor.execute(query)
            data = cursor.fetchall()

            model = QtGui.QStandardItemModel()

            if data:
                # Настройка заголовков колонок
                headers = {
                    'id': 'ID', 'full_name': 'ФИО гостя', 'passport': 'Паспорт',
                    'date_in': 'Заезд', 'date_out': 'Выезд', 'category_name': 'Тип номера',
                    'room_number': 'Номер', 'status_name': 'Статус', 'purpose': 'Пожелания'
                }

                keys = list(headers.keys())
                model.setHorizontalHeaderLabels([headers[k] for k in keys])

                # Заполнение модели
                for row in data:
                    items = []
                    for key in keys:
                        value = str(row.get(key, ''))
                        # Форматирование даты (убираем время)
                        if key in ['date_in', 'date_out'] and value and ' ' in value:
                            value = value.split(' ')[0]

                        items.append(QtGui.QStandardItem(value))

                    model.appendRow(items)

            self.ui.tableView.setModel(model)

            self.ui.tableView.resizeColumnsToContents()
            self.ui.tableView.horizontalHeader().setStretchLastSection(True)

        except Exception as e:
            QMessageBox.critical(self.ui.centralwidget, "Ошибка БД",
                                 f"Ошибка подключения или запроса: {e}",
                                 QMessageBox.StandardButton.Close)
        finally:
            if conn:
                conn.close()


# (Точка входа)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dummy_auth = QMainWindow()
    tablet_window = TabletWindow('test_user', parent_window=dummy_auth)
    tablet_window.show()
    sys.exit(app.exec())