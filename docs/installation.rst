## Установка

1) Загрузите исходный код с git:
    ```
    git clone git://github.com/oleg-post/SPLM.git
    ```
2) Перейдите в директорию проекта:
    ```
    cd SPLM
    ```
3) Подготовьте виртуальное окружение VirtualEnv и VirtualEnvWrapper. Дополнительно смотрите: http://www.doughellmann.com/docs/virtualenvwrapper/ и https://python-scripts.com/virtualenv. Создайте virtual environment:
    ```
    mkvirtualenv environment
    ```
4) Установите необходимые дополнительные пакеты (python dependencies):
    ```
    pip install -r requirements.txt
    ```
5) Запустите сервер приложения:
    ```
    python run.py
    ```
<a name="3"></a>