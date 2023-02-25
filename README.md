# hw05_final

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)

Проект yatube это социальная сеть с возможностью публикации постов с картинками, редактировании их. На сайте можно зарегистрироваться, если забудете пароль, его можно будет восстановить и поменять. Можно подписываться и отписываться от любимых авторов. Можно оставлять комментарии под постами.

Технологии:

Python 3.7
Django 2.2.19

Как запустить проект: Клонировать репозиторий и перейти в него в командной строке:

git clone <> 

Cоздать и активировать виртуальное окружение:

python3 -m venv env source env/bin/activate 

Установить зависимости из файла requirements.txt:

python3 -m pip install --upgrade pip pip install -r requirements.txt 

Выполнить миграции:

python3 manage.py migrate 

Запустить проект:

python3 manage.py runserver
