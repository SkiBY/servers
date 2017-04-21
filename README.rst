Приложение **p_code** - тестовое задание *Система инвентаризации серверов*

Написано на python 2.7 и использованием фреймворка Flask с базой PostgreeSQL

Включает в себя 


Для установки на Ubuntu:
0. Убедитесь, что у вас установлены и настроены следующие пакеты: python-pip python-dev nginx postgresql postgresql-contrib libpq-dev psycopg2

1. Клонируйте проект:


    git clone https://github.com/SkiBY/servers.git::
    cd servers


2. В virtualenv(что крайне рекомендовано) или на чистой системе проверьте набор python пакетов и установите недостающие:


    pip install -r requirements.txt


3. Создайте базу данных для проекта, дайте к ней доступ нужному пользователю.

Перейдите в папку p_code. Отредактируйте файл config.py

Укажите реквизиты доступа в базу данных:


    PG_USER = логин::
    PG_PASS = пароль::
    PG_BASE_NAME = имя созданной базы данных::


4. Запустите в папке p_code скрипты миграции баз данных и создания нового пользователя

    python manage.py db init::
    python manage.py db migrate::
    python manage.py db upgrade::
    python make_user.py::

5. Добавьте скрипт для запуска uwsgi-проекта в автозагрузку


    sudo nano /etc/init/p_code.conf


*содержимое файла(замените часть в фигурных скобках на актуальные)*


    description "uwsgi for p_code"::

    start on runlevel [2345]::
    stop on runlevel [!2345]::

    setuid {{your user}}::
    setgid www-data::

    #if you use virtualenv::
    env PATH={{path to projects folder}}/p_code/bin::

    chdir {{path to projects folder}}/p_code::
    exec uwsgi --ini p_code.ini::


*содержимое файла*

Стартуйте проект:


    sudo start p_code


6. Настройте nginx

Создайте конфигурационный файл для проекта:


    sudo nano /etc/nginx/sites-available/p_code


*содержимое файла*

    server {::
        listen 80;::
        server_name {{домен сервера или IP-адрес}};::

        location / {::
            include uwsgi_params;::
            uwsgi_pass unix:{{путь к проектам}}p_code/p_code.sock;::
        }::
    }::


*содержимое файла*

Создайте ссылку в папку разрешенных


    sudo ln -s /etc/nginx/sites-available/p_code /etc/nginx/sites-enabled


Перезапустите nginx


7. Проверьте доступность приложения по указанному в конфигурационном файле nginx адресу

8. Вводите логин, пароль - учитывайте серверы )