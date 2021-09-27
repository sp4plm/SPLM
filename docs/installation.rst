.. highlight:: shell

============
Установка
============
0) Если у вас не установлен пакет "git", то выполните его установку. Для Ubuntu это команда:

.. code-block:: console

    $ sudo apt install git


1) Загрузите исходный код с git, находясь в папке "opt":

.. code-block:: console
    
    $ cd /opt
    $ sudo git clone git://github.com/oleg-post/SPLM

2) Перейдите в директорию проекта:

.. code-block:: console

    cd SPLM

3) Подготовьте виртуальное окружение VirtualEnv и VirtualEnvWrapper. Дополнительно смотрите: https://python-scripts.com/virtualenv. Создайте virtual environment:

.. code-block:: console

    $ sudo apt install python3.8
    $ sudo apt install python3.8-venv
    $ sudo mkdir venv && cd venv
    $ sudo python3.8 -m venv env
    $ source env/bin/activate
    $ cd ..


4) Установите необходимые дополнительные пакеты (python dependencies):

.. code-block:: console

    pip install -r requirements.txt

5) Запустите сервер приложения:

.. code-block:: console

    python run.py
