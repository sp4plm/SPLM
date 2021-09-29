.. highlight:: shell

============
Установка
============
Прежде чем начать установку уведитесь что у вас установлен пакет "git". Если их нет, то выполните его установку.
Эту и все последующие установочные команды будем выполнять от пользователя root на примере работы с Ubuntu 18:

.. code-block:: console

    $ sudo -i
    # apt install git


1) Загрузите исходный код с git, находясь в папке "opt":

.. code-block:: console
    
    # cd /opt/
    # git clone git://github.com/oleg-post/SPLM

и перейдите в директорию проекта:

.. code-block:: console

    # cd SPLM

2) Подготовьте виртуальное окружение VirtualEnv для Python. Желательно иметь Python 3.7 или следующий. Дополнительно смотрите: https://python-scripts.com/virtualenv. Если у вас уже есть необходиммая версия Python, то первую команду из указанных ниже можно пропустить. Создайте virtual environment:

.. code-block:: console

    # apt install python3.8
    # apt install python3.8-venv
    # mkdir venv && cd venv
    # python3.8 -m venv env
    # source env/bin/activate
    # cd ..


4) Установите необходимые дополнительные пакеты (python dependencies):

.. code-block:: console

    # pip install -r requirements.txt

5) Запустите сервер приложения:

.. code-block:: console

    # python3 run.py
