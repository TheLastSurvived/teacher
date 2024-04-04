from app import app, db, models
from hashlib import md5
import re

regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

def isValidEmail(email):
    if re.fullmatch(regex, email):
      return True
    else:
      return False


print("Создаем супер-пользователя для доступа к админ панели!!!!")
name = input("Введите имя: ")
surname = input("Введите фамилию: ")
email = input("Введите почту: ")
password = input("Введите пароль: ")


with app.app_context():
    if isValidEmail(email):
        admin = models.User(name=name, surname=surname, email=email, password=md5(password.encode()).hexdigest(), root=1)
        db.session.add(admin)
        db.session.commit()
        print("---------------------------------")
        print('Супер-пользователь создан!')
    else:
        print("---------------------------------")
        print("Электронная почта введена не правильно!")

input()