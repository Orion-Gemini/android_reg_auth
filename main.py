from fastapi import FastAPI
from pydantic import BaseModel
import mysql.connector

app = FastAPI()


class UserRegister(BaseModel):
    name: str
    surname: str
    lastname: str
    passport: int  # изменено на int
    login: str
    password: int  # изменено на int


class UserLogin(BaseModel):
    login: str
    password: int  # изменено на int


def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        database='hotel_db',
        user='root',
        password='root'
    )
    return connection


@app.post("/register")
async def register(user_data: UserRegister):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM clients WHERE login = %s OR passport = %s",
                   (user_data.login, user_data.passport))
    if cursor.fetchone():
        return {"status": "error", "message": "Логин или паспорт уже существуют"}

    cursor.execute(
        "INSERT INTO clients (name, surname, lastname, passport, login, password) VALUES (%s, %s, %s, %s, %s, %s)",
        (user_data.name, user_data.surname, user_data.lastname, user_data.passport, user_data.login, user_data.password)
    )
    connection.commit()

    cursor.close()
    connection.close()

    return {"status": "success", "message": "Регистрация успешна"}


@app.post("/login")
async def login(user_data: UserLogin):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM clients WHERE login = %s", (user_data.login,))
    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if not user:
        return {"status": "error", "message": "Пользователь не найден"}

    if user['password'] != user_data.password:
        return {"status": "error", "message": "Неверный пароль"}

    return {
        "status": "success",
        "message": "Вход выполнен",
        "user_name": f"{user['surname']} {user['name']}"
    }