# Установка Python и pip

Обязательное требование — **версия Python 3.8 или выше**.

# Windows

1. Скачайте Windows installer (64-bit или 32-bit) с официального сайта: [https://www.python.org/downloads/](https://www.python.org/downloads/).
2. Запустите установщик и следуйте инструкциям на экране. Отметьте галочку "Добавить Python в переменную PATH". pip будет установлен вместе с интерпретатором Python.

# Linux

## Ubuntu / Debian

```
sudo apt-get install python3 python3-pip
```

## RHEL / AlmaLinux / CentOS Stream

```
sudo dnf install python3 python3-pip
```

## CentOS 7

> Рекомендуем обновиться до актуальной версии CentOS Stream или перейти на альтернативные дистрибутивы AlmaLinux или Rocky Linux.

## Arch Linux

```
sudo pacman -Sy python python-pip
```

# Mac OS X

Установите пакетный менеджер [homebrew](https://brew.sh/#install):

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Установите python через homebrew:

```
brew install python
```

pip будет установлен вместе с пакетом python. Для установки twc-cli используйте команду:

```
pip3 install twc-cli
```

# Универсальный способ установки pip

Этот способ подходит для всех ОС. Оригинальная инструкция: [https://pip.pypa.io/en/stable/installation/](https://pip.pypa.io/en/stable/installation/).

Требуется, чтобы Python уже был установлен на компьютер. Выберите один из следующих вариантов.

## ensurepip

```
python -m ensurepip --upgrade
```

## get-pip.py

Cкачайте скрипт get-pip.py: [https://bootstrap.pypa.io/get-pip.py](https://bootstrap.pypa.io/get-pip.py).

Запустите скрипт:

```
python get-pip.py
```
