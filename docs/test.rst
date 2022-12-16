Файл для тестирования автоматической подгрузки документации
======================================


Мой модуль query_mgt
``````````````````````````

Модуль предоставляет функциональность для работы с триплстором через SPARQL запросы.

Модуль работает с триплстором через драйвер, который настраивается в административном интерфейсе.

Для вызова модуля query_mgt из других модулей необходимо использовать следуюший код:

а. Для выполнения запроса к триплстору::

    from app.app_api import tsc_query
    tsc_query(query_code, params)

где

.. autofunction:: app.app_api.tsc_query

б. Для создания редактора sparqt-файлов стороннего модуля::

    from app import app_api
    query_mod_api = app_api.get_mod_api('query_mgt')
    query_mod_api.create_sparqt_manager('/sparqt', mod)

где

.. autofunction:: app.query_mgt.views.create_sparqt_manager

Формат запроса, передаваемый модулю query_mgt (функция tsc_query) должен быть в виде::

    tsc_query(_q, params = {})

где ``_q`` - код запроса в формате Python.String : ``<module>.<file>.<template>``,
``params`` - переменные для подстановки в запрос в формате Python.Dict : ``{<VARNAME> : <VALUE>}``

или в виде::

    tsc_query(_q)

где _q - текстовый SPARQL запрос в формате Python.String


После выполнения запроса в триплсторе модуль делает пост-обработку. Модуль query_mgt возвращает
объект типа Python.List, содержащий список объектов типа Python.Dict. В каждом объекте типа
Python.Dict содержаться пары ключ-значение запрашиваемых переменных.

В случае если запрос к базе был некорректный (или во время запроса произошла ошибка), то
возвращается объект типа Python.String c текстом ошибки. В лог ``app\data\logs\Query.log`` добавляется запись типа
error c причиной невыполнения запроса.

Если запрос к базе вернул пустой запрос, то модуль возвращает пустой объект типа ``Python.List = []``










Мой модуль onto_mgt
``````````````````````````

Модуль предоставляет функциональность для работы с онтологиями.

Модуль позволяет загрузить/заменить/скачать/удалить онтологии на портале. Для каждой онтологии сохраняется
ее префикс, определенный через baseURI. Для загруженных файлов онтологий реализована навигация по онтологии.

Модуль предоставляет API для обращения к нему из других модулей. Пример обращения к модулю onto_mgt::

	from app import app_api
        onto_api = app_api.get_mod_api('onto_mgt')

Список поддерживаемых обращений к модулю:

.. autofunction:: app.onto_mgt.mod_api.ModApi.get_prefixes

.. autofunction:: app.onto_mgt.mod_api.ModApi.get_all_prefixes

.. autofunction:: app.onto_mgt.mod_api.ModApi.get_classes

.. autofunction:: app.onto_mgt.mod_api.ModApi.get_ontos

.. autofunction:: app.onto_mgt.mod_api.ModApi.get_parent

.. autofunction:: app.onto_mgt.mod_api.ModApi.get_graph





