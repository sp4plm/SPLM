# Назначение портала

Портал предназначен для навигации и анализа данных, представленных в семантическом виде, см стандарты Semantic Web на официальном сайте [w3c.org](https://www.w3.org/standards/semanticweb/). Портал так же предназначен для интеграции информации из разных источников.

![w3c](https://www.w3.org/Icons/SW/sw-horz-w3c.png)

# Особенность портала

Ключевой особенностью портала является то, что все данные на портале отображаются в зависимости от их классов зарегистрированных в нем онтологий. Т. е. каждый класс онтологии имеет свою форму представления данных, которая может быть уникальной и заданной в явном виде. Или создаваться «на лету» в результате наследования от своего старшего класса онтологии. 

# Содержание

- [Установка:](#1)
  - [Требования к кофигурации:](#1.1)
- [Запуск:](#2)
  - [Recommended minimum browser](#2.1)
  - [Новый эелемент](#2.2)
- [Основные модули портала](#3) 
- [Возможные области применения портала](#4)

<a name="1"></a>
## Установка

Download via git:

  'git clone git://github.com/hansonkd/FlaskBootstrapSecurity.git'

Change into the cloned directory
  
  'cd FlaskBootstrapSecurity'

Get VirtualEnv and VirtualEnvWrapper set up. See here for further details: http://www.doughellmann.com/docs/virtualenvwrapper/

Create a virtualenvironment

 'mkvirtualenv environment'
 
Install the required python dependancies:

 'pip install -r requirements.txt'

Run a development server:

 'python run.py'


<a name="1.1"></a>
### Требования к кофигурации

If you plan to use Nightscout, we recommend using ...

<a name="2"></a>
## Запуск

<a name="2.1"></a>
### Recommended minimum browser versions for using Nightscout:

Older versions of the browsers might work, but are untested.

Older versions of the browsers might work, but are untested.

<a name="2.2"></a>
### Новый эелемент

бла бла бла

<a name="3"></a>
## Основные модули портала
Основные модули портала являют ядром и поставляются на условиях лицензии [файл лицензии]. К основным мрдулм портала относятся:
- Администрирование портала
- Управление пользователями
- Управление оформлением 
- Управление онтологиями
- Загрузка данных
- Управление запросами в базе данных
- Управление модулями

<a name="4"></a>
## Возможные области применения портала
- Управление информацией об оборудовании (информационна модель изделия)
- Управление информацией календарно-сетевого планирования
- Интеграция данных
- Витрина данных
- Аналитика данных, включая но не ограничиваясь:
  - предиктивная аналитика, 
  - классификация, 
  - кластеризация, 
  - регресионный анализ, 
  - построение дерева решений и т.д.

