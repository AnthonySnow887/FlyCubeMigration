# FlyCubeMigration

[![License](https://img.shields.io/github/license/AnthonySnow887/FlyCubeMigration)](https://github.com/AnthonySnow887/FlyCubeMigration/blob/master/LICENSE)
[![Latest Release](https://img.shields.io/github/v/release/AnthonySnow887/FlyCubeMigration?label=release)](https://github.com/AnthonySnow887/FlyCubeMigration/releases)
![Last Commit](https://img.shields.io/github/last-commit/AnthonySnow887/FlyCubeMigration/develop)

FlyCubeMigration — это инструмент, разработанный на Python, который следует идеологии и принципам миграции базы данных, 
заложенным в Ruby on Rails. FlyCubeMigration полностью повторяет функционал ядра миграции, 
реализованного в MVC Web Framework FlyCubePHP.

Установка каждой миграции выполняется в режиме транзакции и в случае ошибок 
откатывает состояние базы данных до стадии установки.

Начиная с версии 1.1.0 добавлена поддержка POST-скриптов, которые будут выполняться каждый раз при установке/переустановке/удалении миграций.
POST-скрипты позволяют автоматизировать рутинные действия, необходимые после выполнения описанных выше действий.
POST-скрипты представляют собой стандартные SQL скрипты, расположенные в одном или нескольких каталогах, и содержащие общие для всех миграций команды.

Установка POST-скриптов выполняется в режиме транзакции для всех измененных баз данных и в случае ошибок 
откатывает состояние базы данных до стадии установки POST-скрипта, вызвавшего ошибку.

Начиная с версии 1.2.0 добавлена поддержка выгрузки файлов миграций в SQL-файлы.
Данный механизм позволяет использовать штатные консольные утилиты базы данных для установки или удаления миграций без необходимости использования всех требуемых python3 библиотек и инструментов.


## Поддерживаемые СУБД

- SQLite 3;
- PostgreSQL 9.6 or later.
- MySQL/MariaDB (tested on MariaDB 10.2.36)

## Операционные системы, на которых проводилось тестирование

- Alma Linux 9.1
- Alt Linux 8.1 and later
- Astra Linux 1.6 / 1.7 / 2.12
- CentOS 8.5
- Debian 12 and later
- OpenSUSE 15.1 and later
- RedOS 7
- Rosa Linux 12.4
- Ubuntu 20.04 and later

## Базовые системные требования

- python >= 3.6

## Дополнительные зависимые Python модули

- python3-psycopg2
- python3-mysql-connector-python
- python3-PyYAML
- python3-requests

## Релизы

Релизы FlyCubeMigration доступны на [Github](https://github.com/AnthonySnow887/FlyCubeMigration/releases).

## Лицензия

FlyCubeMigration распространяется под лицензией GPL-3.0. Подробности смотрите в файле LICENSE.

## Использование

```bash
FlyCubeMigration> ./fly-cube-migration --help

Usage: ./fly-cube-migration [options]

Options include:

  --help                    Show help [-h, -?]
  --version                 Print the version [-v]
  --latest-version          Select latest version from GitHub [-lv]
  --env=[VALUE]             Set current environment (production/development; default: development)
  --output=[VALUE]          Show sql output (optional) (default: false)
  --config-dir=[VALUE]      Set FlyCubeMigration config file directory (optional) (default: 'config/')
  --save-config-dir         Save in settings FlyCubeMigration config file directory
  --clear-config-dir        Clear from settings FlyCubeMigration config file directory
  --settings                Show current FlyCubeMigration config settings


  --post-scripts            Show loaded post-scripts

  --new-project             Create new FlyCubeMigration project

  --new-migration           Create new migration

  --make-migration-number   Create and output new migration version number

  --db-create               Create all databases for current environment
  --db-create-all           Create all databases for all environments (development and production)

  --db-drop                 Drop all databases for current environment
  --db-drop-all             Drop all databases for all environments (development and production)

  --db-migrate              Start all database(s) migrations

  --db-migrate-redo         Start re-install last database migration

  --db-migrate-status       Select migrations status

  --db-rollback             Start uninstall last database migration
  --db-rollback-all         Start uninstall all database(s) migrations

  --db-version              Select database(s) migration version

  --db-settings             Show database(s) config settings

  --db-migrate-export       Export all database(s) migrations (section: up)

  --db-rollback-export      Export all database(s) migrations (section: down)

  --name=[VALUE]            Set new object name
  --to-version=[VALUE]      Set needed migration version (optional; if 0 - uninstall all migrations)
  --step=[VALUE]            Set needed number of steps for uninstall (re-install) migrations (optional; default: 1)
  --dir=[VALUE]             Set directory for export migration files (optional; default: "FLY_CUBE_MIGRATION_DIR/export/")


Examples:

 1. Set FlyCubeMigration config directory ('--config-dir' is grouped with all the commands listed below):
     ./fly-cube-migration --config-dir=../test/config/ [Other Commands]

 2. Set current environment ('--env' is grouped with all the commands listed below):
     ./fly-cube-migration --env=production [Other Commands]

 3. Show sql output ('--output' is grouped with all the commands listed below):
     ./fly-cube-migration --output=true [Other Commands]

 4. Create new FlyCubeMigration project:
     ./fly-cube-migration --new-project --name=ExampleProject

 5. Create new migration:
     ./fly-cube-migration --new-migration --name=ExampleMigration

 6. Select database migration version:
     ./fly-cube-migration --db-version

 7. Select database migrations status:
     ./fly-cube-migration --db-migrate-status

 8. Install all migrations:
     ./fly-cube-migration --db-migrate

 9. Install needed migrations:
     ./fly-cube-migration --db-migrate --to-version=20210309092620

10. Uninstall last migration:
     ./fly-cube-migration --db-rollback

11. Uninstall last N-steps migrations:
     ./fly-cube-migration --db-rollback --step=3

12. Uninstall all migrations (ver. 1):
     ./fly-cube-migration --db-rollback-all

13. Uninstall all migrations (ver. 2):
     ./fly-cube-migration --db-migrate --to-version=0

14. Re-Install last migration:
     ./fly-cube-migration --db-migrate-redo

15. Re-Install last N-steps migrations:
     ./fly-cube-migration --db-migrate-redo --step=3
```

## Быстрый старт

Для начала работы с FlyCubeMigration создайте новый проект командой:
```bash
$> ./fly-cube-migration --new-project --name=MyProject

=== FlyCubeMigration =========================
[Created] /home/user/FlyCubeMigrationProjects/MyProject
[Created] /home/user/FlyCubeMigrationProjects/MyProject/config
[Created] /home/user/FlyCubeMigrationProjects/MyProject/db
[Created] /home/user/FlyCubeMigrationProjects/MyProject/db/migrate
[Created] /home/user/FlyCubeMigrationProjects/MyProject/post_scripts
[Created] /home/user/FlyCubeMigrationProjects/MyProject/config/fly-cube-migration.yml
[Created] /home/user/FlyCubeMigrationProjects/MyProject/config/database.yml
[Created] /home/user/FlyCubeMigrationProjects/MyProject/config/post-scripts.yml
=== FlyCubeMigration =========================
```

## Файл конфигурации FlyCubeMigration

Файл конфигурации должен находиться в каталоге ```config/``` и его имя должно совпадать с ```fly-cube-migration.yml```.
Полный путь к файлу: ```config/fly-cube-migration.yml```

Если вы хотите использовать другой файл конфигурации, то запустите приложение с командой: 
```bash
--config-dir=[PATH TO THE CONGIG FILE DIRECTORY]
```

Пример:
```bash
$> ./fly-cube-migration --config-dir=../test/config/ [Other Commands]
```

Если вы всегда хотите использовать этот файл конфигурации, вы можете сохранить его в системных настройках приложения:
```bash
--save-config-dir
```

Пример:
```bash
$> ./fly-cube-migration --config-dir=../test/config/ --save-config-dir
```

>
> ПРИМЕЧАНИЕ: После сохранения настроек можно не указывать каталог конфигурационного файла при выполнении других команд.
> 

Если вам нужно очистить сохраненные настройки, то выполните команду:
```bash
--clear-config-dir
```

Пример:
```bash
$> ./fly-cube-migration --clear-config-dir
```

Чтобы получить список текущих конфигураций приложения, используйте:
```bash
--settings
```

Пример:
```bash
$> ./fly-cube-migration --settings

=== FlyCubeMigration =========================

Config file: /home/user/Projects/FlyCubeMigration/config/fly-cube-migration.yml
Values:
 - FLY_CUBE_MIGRATION_CONFIG_DIR: config/
 - FLY_CUBE_MIGRATION_DB_MIGRATIONS_DIR: db/migrate/

=== FlyCubeMigration =========================
```

Пример базового файла конфигурации:
```yaml
#
# Directory for config files: 'fly-cube-migration.yml', 'database.yml' and 'post-scripts.yml'
#
FLY_CUBE_MIGRATION_CONFIG_DIR: "config/"

#
# Directory for database migration files
#
FLY_CUBE_MIGRATION_DB_MIGRATIONS_DIR: "db/migrate/"
```
 
## Конфигурационный файл для доступа к СУБД

По умолчанию файл конфигурации базы данных находится в каталоге ```config/``` и его имя должно совпадать с ```database.yml```.
Полный путь к файлу: ```config/database.yml```

Этот файл может содержать неограниченное количество настроек для подключения к разным СУБД, 
но поля "production", "development", "production_secondary" и "development_secondary" можно задать только один раз.

Эти поля указывают ядру системы, какой раздел настроек следует использовать для подключения, 
и какой адаптер необходимо создать в том или ином режиме работы приложения.

Дополнительные настройки:
  - "production_secondary" - содержит массив "ключ-значение" дополнительных разделов доступа к БД для режима "production";
  - "development_secondary" - содержит массив "ключ-значение" дополнительных секций доступа к БД для режима "development".

>
> ПРИМЕЧАНИЕ: Ключ вторичной базы данных можно использовать, чтобы указать, к какой базе данных относится миграция.
> 

Если вы хотите использовать другую директорию, то укажите полный путь к ней в конфигурационном файле FlyCubeMigration:
```yaml
#
# Directory for config files: 'fly-cube-migration.yml', 'database.yml' and 'post-scripts.yml'
#
FLY_CUBE_MIGRATION_CONFIG_DIR: "/home/user/test/config/"
```

Пример базового файла конфигурации:
```yaml
# SQLite configuration example
default_sqlite_dev: &default_sqlite_dev
  adapter: sqlite
  database: db/fly_cube_dev.sqlite3

default_sqlite_prod: &default_sqlite_prod
  adapter: sqlite
  database: db/fly_cube_prod.sqlite3

# PostgreSQL TCP configuration example
default_postgresql_dev: &default_postgresql_dev
  adapter: postgresql
  database: fly_cube_dev
  host: 127.0.0.1
  port: 5432
  username: postgres
  password: ""

default_postgresql_prod: &default_postgresql_prod
  adapter: postgresql
  database: fly_cube_prod
  host: 127.0.0.1
  port: 5432
  username: postgres
  password: ""

# PostgreSQL UNIX configuration example
default_postgresql_unix_dev: &default_postgresql_unix_dev
  adapter: postgresql
  database: fly_cube_dev
  unix_socket_dir: /var/run/postgresql
  username: postgres
  password: ""

default_postgresql_unix_prod: &default_postgresql_unix_prod
  adapter: postgresql
  database: fly_cube_prod
  unix_socket_dir: /var/run/postgresql
  username: postgres
  password: ""

# MySQL TCP configuration example
default_mysql_dev: &default_mysql_dev
  adapter: mysql
  database: fly_cube_dev
  host: 127.0.0.1
  port: 3306
  username: root
  password: ""

default_mysql_prod: &default_mysql_prod
  adapter: mysql
  database: fly_cube_prod
  host: 127.0.0.1
  port: 3306
  username: root
  password: ""

# MySQL UNIX configuration example
default_mysql__unix_dev: &default_mysql_unix_dev
  adapter: mysql
  database: fly_cube_dev
  unix_socket: /run/mysql/mysql.sock
  username: root
  password: ""

default_mysql_unix_prod: &default_mysql_unix_prod
  adapter: mysql
  database: fly_cube_prod
  unix_socket: /run/mysql/mysql.sock
  username: root
  password: ""


# ENV sections
production:
  <<: *default_sqlite_prod

development:
  <<: *default_sqlite_dev

# Secondary ENV sections
production_secondary:
#  test: *default_postgresql_prod
#  test-2: *default_postgresql_unix_prod

development_secondary:
#  test: *default_postgresql_dev
#  test-2: *default_postgresql_unix_dev
```

## Конфигурационный файл POST-скриптов

POST-скрипты представляют собой стандартные SQL скрипты, расположенные в одном или нескольких каталогах, и содержащие общие для всех миграций команды.
POST-скрипты позволяют автоматизировать рутинные действия, необходимые после выполнения установки/переустановки/удаления миграций.
Примером действий POST-скриптов можно назвать:
 - установка грантов на таблицы/представления/функции базы данных
 - установка/смена владельца таблиц
 - и так далее

Установка POST-скриптов выполняется в режиме транзакции для всех измененных баз данных и в случае ошибок 
откатывает состояние базы данных до стадии установки POST-скрипта, вызвавшего ошибку.

>
> ПРИМЕЧАНИЕ: POST-скрипты выполняются только для следующих команд:
>  - --db-migrate
>  - --db-migrate-redo
>  - --db-rollback
>  - --db-rollback-all
>

По умолчанию файл конфигурации POST-скриптов находится в каталоге ```config/``` и его имя должно совпадать с ```post-scripts.yml```.
Полный путь к файлу: ```config/post-scripts.yml```

Этот файл может содержать неограниченное количество настроек для описания расположения скриптов SQL, 
но поля "production", "development" можно задать только один раз.

Эти поля указывают ядру системы, какой раздел настроек следует использовать в том или ином режиме работы приложения.

Если вы хотите использовать другую директорию, то укажите полный путь к ней в конфигурационном файле FlyCubeMigration:
```yaml
#
# Directory for config files: 'fly-cube-migration.yml', 'database.yml' and 'post-scripts.yml'
#
FLY_CUBE_MIGRATION_CONFIG_DIR: "/home/user/test/config/"
```

Пример базового файла конфигурации:
```yaml
#
# NOTE: Only '*.sql' files are loaded. Other files will be ignored.
#

# configuration example
default_dev: &default_dev
  file-use-sort: false
  file:
#    - /home/user/FlyCubeMigrationProjects/Myproject/post_scripts/00.sql
#    - /home/user/FlyCubeMigrationProjects/Myproject/post_scripts/10.sql
  directory-recursive-load: false
  directory:
#    - /home/user/FlyCubeMigrationProjects/Myproject/post_scripts/

default_dev_2: &default_dev_2
  file-use-sort: false
#  file: /home/user/FlyCubeMigrationProjects/Myproject/post_scripts/00.sql
  directory-recursive-load: false
#  directory: /home/user/FlyCubeMigrationProjects/Myproject/post_scripts/


default_prod: &default_prod
  file-use-sort: false
  file:
#    - /home/user/FlyCubeMigrationProjects/Myproject/post_scripts/00.sql
#    - /home/user/FlyCubeMigrationProjects/Myproject/post_scripts/10.sql
  directory-recursive-load: false
  directory:
#    - /home/user/FlyCubeMigrationProjects/Myproject/post_scripts/

default_prod_2: &default_prod_2
  file-use-sort: false
#  file: /home/user/FlyCubeMigrationProjects/Myproject/post_scripts/00.sql
  directory-recursive-load: false
#  directory: /home/user/FlyCubeMigrationProjects/Myproject/post_scripts/


# ENV sections
production:
  <<: *default_prod

development:
  <<: *default_dev
```

Описание полей конфигурационного файла:
 - [bool]       file-use-sort               - использовать прямую сортировку по имени SQL скриптов, указанных в секции ```file```
 - [str|list]   file                        - содержит путь/список путей до SQL скриптов
 - [bool]       directory-recursive-load    - использовать рекурсиыную загрузку каталогов, указанных в секции ```directory```
 - [str|list]   directory                   - содержит путь/список путей до каталогов с SQL скриптами


## Миграции - описание

Миграции — это удобный способ управления структурой вашей базы данных. Как и Ruby on Rails, 
система миграции FlyCubeMigration предоставляет широкий набор методов для работы со схемой базы данных.
Такой подход позволяет не использовать SQL для описания или изменения схемы базы данных, 
что в свою очередь дает возможность не зависеть от конкретной СУБД и ее свойств.

Каждая новая миграция вносит изменения в структуру базы данных, добавляя, изменяя или удаляя таблицы,
их столбцы или свойства, и может рассматриваться как «новая» версия базы данных.

Во избежание проблем и конфликтов при установке миграций каждый новый файл получает уникальный префикс,
что также является его версией. Префикс представляет собой текущую дату и время в формате ```YYYYMMDDHHmmSS```, где:
  - YYYY - год;
  - MM - месяц с ведущим нулем (01-12);
  - DD - день с ведущим нулем (01-31);
  - HH - часы с ведущим нулем в 24-часовом формате (00-23);
  - mm - минуты с ведущим нулем (00-59);
  - SS - секунды с ведущим нулем (00-59).

Такой подход позволяет устанавливать миграции только в том порядке, в котором они были созданы.
Все версии установленных миграций хранятся в базе данных, что позволяет в любой момент получить полную информацию 
о текущей версии базы или состоянии каждой миграции из списка доступных.

Установка или удаление (откат) миграций выполняется последовательно в режиме транзакции, 
если это поддерживается СУБД. В случае успешной операции в базу данных сохраняется текущая версия миграций.

Все классы миграции являются производными от базового класса BaseMigration.

Класс миграции должен переопределить два абстрактных метода:
  - up - метод внесения изменений в базу данных
  - down - метод удаления изменений из базы данных

Необязательный абстрактный метод:
  - configuration - метод конфигурации миграции (вызывается перед запуском установки/отката миграции)

> 
> Если вам нужно указать имя базы данных, которой принадлежит текущий файл миграции, 
> используйте функцию ```set_database(...)```.
> 
> ПРИМЕЧАНИЕ: В этом случае необходимо указать ключ имени базы данных, указанный в списке secondary databases.
> 
> Пример конфигурационного файла для доступа к СУБД:
> ```yaml
> default_postgresql_dev: &default_postgresql_dev
>   adapter: postgresql
>   database: fly_cube_dev
>   host: 127.0.0.1
>   port: 5432
>   username: postgres
>   password: ""
>    
> default_postgresql_prod: &default_postgresql_prod
>   adapter: postgresql
>   database: fly_cube_prod
>   host: 127.0.0.1
>   port: 5432
>   username: postgres
>   password: ""
> 
> # Secondary ENV sections
> production_secondary:
>   test: *default_postgresql_prod
>  
> development_secondary:
>   test: *default_postgresql_dev
> ```
>  
> Пример файла миграции:
> ```python
> from src.Migration.BaseMigration import BaseMigration
> 
> 
> class ExampleMigration(BaseMigration):
>    
>    def configuration(self):
>        self.set_database('test')
> 
>    def up(self):
>        # Set here your code for install migration
>        return
>
>     def down(self):
>        # Set here your code for rollback migration
>        return
> ```
> 

Каталог по умолчанию для хранения и поиска миграций — ```db/migrate/```.

Если вы хотите использовать другую директорию, то укажите полный путь к ней в конфигурационном файле FlyCubeMigration:
```yaml
#
# Directory for database migration files
#
FLY_CUBE_MIGRATION_DB_MIGRATIONS_DIR: "/home/user/test/db/migrate/"
```

Пример класса миграции:
```python
from src.Migration.BaseMigration import BaseMigration


class ExampleMigration(BaseMigration):
    
    def configuration(self):
        # Set here your code for configuration migration
        return

    def up(self):
        # Set here your code for install migration
        return 

    def down(self):
        # Set here your code for rollback migration
        return 
```

## Миграции - примеры

Ниже приведены примеры использования различных методов миграций.

### Create/Drop Extension

Методы ```create_extension``` и ```drop_extension``` позволяют включить (или отключить) необходимое расширение базы данных.

Поддерживаемые аргументы метода ```create_extension```:
  - [bool] if_not_exists - добавить флаг 'IF NOT EXISTS'

Поддерживаемые аргументы метода ```drop_extension```:
  - [bool] if_exists - добавить флаг 'IF EXISTS'

>
> ПРИМЕЧАНИЕ: Если база данных не поддерживает данный функционал, операция игнорируется.
> 

```python
from src.Migration.BaseMigration import BaseMigration


class CreateExtension(BaseMigration):
    
    def up(self):
        # ver. 1: without props:
        self.create_extension('uuid-ossp')
        # ver. 2: with props:
        self.create_extension('uuid-ossp', {'if_not_exists': True})

    def down(self):
        # ver. 1: without props:
        self.drop_extension('uuid-ossp')
        # ver. 2: with props:
        self.drop_extension('uuid-ossp', {'if_exists': True})
```

### Create/Drop Schema

Методы ```create_schema``` и ```drop_schema``` позволяют создать (или удалить) новую схему данных.

Поддерживаемые аргументы метода ```create_schema```:
  - [bool] if_not_exists - добавить флаг 'IF NOT EXISTS'

Поддерживаемые аргументы метода ```drop_schema```:
  - [bool] if_exists - добавить флаг 'IF EXISTS'

>
> ПРИМЕЧАНИЕ: Если база данных не поддерживает данный функционал, операция игнорируется.
> 

```python
from src.Migration.BaseMigration import BaseMigration


class CreateSchema(BaseMigration):
    
    def up(self):
        # ver. 1: without props:
        self.create_schema('test_schema')
        # ver. 2: with props:
        self.create_schema('test_schema', {'if_not_exists': True})

    def down(self):
        # ver. 1: without props:
        self.drop_schema('test_schema')
        # ver. 2: with props:
        self.drop_schema('test_schema', {'if_exists': True})
```

### Create table

Метод ```create_table``` позволяет создать новую таблицу в базе данных.

Поддерживаемые аргументы метода:
  - [bool]     if_not_exists  - добавить флаг 'IF NOT EXISTS' (только для таблицы)
  - [bool]     id             - использовать столбец ID или нет (будет установлен как первичный ключ)
  - [string]   type           - тип данных колонки (обязательный)
  - [integer]  limit          - размер данных колонки
  - [bool]     null           - может ли быть NULL
  - [string]   default        - базовое значение
  - [bool]     primary_key    - использовать как первичный ключ
  - [bool]     unique         - является уникальным
  - [string]   unique_group   - является уникальной группой (значение: имя группы)

>
> ПРИМЕЧАНИЕ: различия ключей аргументов ```unique``` и ```unique_group```:
> - unique       - указывает, что значения в колонке данных должны быть уникальными;
> - unique_group - указывает, что колонка входит в массив уникальных колонок, 
                   имя которого задается в аргументах (SQL: ```UNIQUE(column_1, column_2, column_3)```).
> 

```python
from src.Migration.BaseMigration import BaseMigration


class CreateTable(BaseMigration):
    
    def up(self):        
        self.create_table('test_schema.test_table', {
                'id': False,
                'if_not_exists': True,
                'my_id': {
                    'type': 'integer',
                    'null': False,
                    'primary_key': True
                },
                'my_data': {
                    'type': 'string',
                    'limit': 128,
                    'default': '',
                    'unique_group': 'group-1'
                },
                'my_data_2': {
                    'type': 'string',
                    'limit': 128,
                    'default': '',
                    'unique_group': 'group-1'
                },
                'my_data_3': {
                    'type': 'string',
                    'default': '',
                    'unique': True
                }
            })

    def down(self):
        self.drop_table('test_schema.test_table')
```

Пример SQL-запроса, описанного выше, для PostgreSQL:
```sql
CREATE TABLE test_schema.test_table
(
  my_id integer NOT NULL,
  my_data character varying(128) DEFAULT ''::character varying,
  my_data_2 character varying(128) DEFAULT ''::character varying,
  my_data_3 text DEFAULT ''::text,
  CONSTRAINT test_pkey PRIMARY KEY (my_id),
  CONSTRAINT test_my_data_3_key UNIQUE (my_data_3),
  CONSTRAINT test_my_data_my_data_2_key UNIQUE (my_data, my_data_2)
)
```

### Rename table

Метод ```rename_table``` позволяет переименовать таблицу.

```python
from src.Migration.BaseMigration import BaseMigration


class RenameTable(BaseMigration):
    
    def up(self):
        self.rename_table('test_schema.test_table', 'test_schema.test_table_renamed')

    def down(self):
        self.rename_table('test_schema.test_table_renamed', 'test_schema.test_table')
```

### Drop table

Метод ```drop_table``` позволяет удалить ранее созданную таблицу.

```python
from src.Migration.BaseMigration import BaseMigration


class DropTable(BaseMigration):
    
    def up(self):
        self.drop_table('test_schema.test_table')

    def down(self):
        return 
```

### Add column

Метод ```add_column``` позволяет добавить новый столбец в ранее созданную таблицу.

Поддерживаемые аргументы метода:
  - [bool]     if_not_exists  - добавить флаг 'IF NOT EXISTS'
  - [string]   type           - тип данных колонки (обязательный)
  - [integer]  limit          - размер данных колонки
  - [bool]     null           - может ли быть NULL
  - [string]   default        - базовое значение

```python
from src.Migration.BaseMigration import BaseMigration


class AddColumn(BaseMigration):
    
    def up(self):
        self.add_column('test_schema.test_table_renamed', 'my_new_column', {
            'if_not_exists': True,
            'type': 'text',
            'limit': 128,
            'null': False,
            'default': '---'
        })

    def down(self):
        self.drop_column('test_schema.test_table_renamed', 'my_new_column')
```

### Rename column

Метод ```rename_column``` позволяет переименовать столбец в таблице.

>
> ПРИМЕЧАНИЕ: Все связанные с данной колонкой объекты, вторичные ключи и прочие элементы базы данных  
>             автоматически обновляются с учетом нового имени.
>

```python
from src.Migration.BaseMigration import BaseMigration


class RenameColumn(BaseMigration):
    
    def up(self):
        self.rename_column('test_schema.test_table_renamed', 'my_new_column', 'my_new_column_renamed')

    def down(self):
        self.rename_column('test_schema.test_table_renamed', 'my_new_column_renamed', 'my_new_column')
```

### Change column

Метод ```change_column``` позволяет изменить тип столбца и его дополнительные параметры, если они заданы.

Поддерживаемые аргументы метода:
  - [integer]  limit          - размер данных колонки
  - [bool]     null           - может ли быть NULL
  - [string]   default        - базовое значение

```python
from src.Migration.BaseMigration import BaseMigration


class ChangeColumn(BaseMigration):
    
    def up(self):
        self.change_column('test_schema.test_table_renamed', 'my_new_column_renamed', 'varchar', {
            'limit': 256,
            'null': False,
            'default': '---???---'
        })

    def down(self):
        self.change_column('test_schema.test_table_renamed', 'my_new_column_renamed', 'text', {
            'limit': 128,
            'null': False,
            'default': '---'
        })
```

### Change column default

Метод ```change_column_default``` позволяет изменить/удалить свойство ```DEFAULT``` столбца таблицы.

>
> ПРИМЕЧАНИЕ: Если значение DEFAULT равно None, то свойство стобца DEFAULT удаляется.
> 

```python
from src.Migration.BaseMigration import BaseMigration


class ChangeColumnDefault(BaseMigration):
    
    def up(self):
        # Remove default ver. 1:
        self.change_column_default('test_schema.test_table_renamed', 'my_new_column_renamed')
        # Remove default ver. 2:
        self.change_column_default('test_schema.test_table_renamed', 'my_new_column_renamed', None)
        # Change default:
        self.change_column_default('test_schema.test_table_renamed', 'my_new_column_renamed', '???')

    def down(self):
        self.change_column_default('test_schema.test_table_renamed', 'my_new_column_renamed', '---???---')
```

### Change column null

Метод ```change_column_null``` позволяет добавить/удалить свойство ```NOT NULL``` столбца таблицы.

>
> ПРИМЕЧАНИЕ: Если значение 'not_null' равно False, то свойство столбца NOT NULL удаляется.
> 

```python
from src.Migration.BaseMigration import BaseMigration


class ChangeColumnNull(BaseMigration):
    
    def up(self):
        # Add 'NOT NULL':
        self.change_column_null('test_schema.test_table_renamed', 'my_new_column_renamed', True)
        # Remove 'NOT NULL' ver. 1:
        self.change_column_null('test_schema.test_table_renamed', 'my_new_column_renamed')
        # Remove 'NOT NULL' ver. 2:
        self.change_column_null('test_schema.test_table_renamed', 'my_new_column_renamed', False)

    def down(self):
        self.change_column_null('test_schema.test_table_renamed', 'my_new_column_renamed', True)
```

### Drop column

Метод ```drop_column``` позволяет удалить столбец из таблицы.

```python
from src.Migration.BaseMigration import BaseMigration


class DropColumn(BaseMigration):
    
    def up(self):
        self.drop_column('test_schema.test_table_renamed', 'my_new_column')

    def down(self):
        return 
```

### Add index

Метод ```add_index``` позволяет добавить индекс для таблицы.

Поддерживаемые аргументы метода:
  - [string] name    - имя индекса (необязательное)
  - [bool]   unique  - является ли уникальным

```python
from src.Migration.BaseMigration import BaseMigration


class AddIndex(BaseMigration):
    
    def up(self):
        self.create_table('test_schema.test_table_2', {
            'id': False,
            'if_not_exists': True,
            'my_id': {
                'type': 'integer',
                'null': False
            },
            'my_id_2': {
                'type': 'integer',
                'null': False
            },
            'my_data': {
                'type': 'string',
                'limit': 128,
                'default': ''
            }
        })
        self.add_index('test_schema.test_table_2', ['my_id'], {'name': 'my_test_index', 'unique': True})
        self.add_index('test_schema.test_table_2', ['my_id_2'])

    def down(self):
        self.drop_table('test_schema.test_table_2')
```

### Rename index

Метод ```rename_index``` позволяет переименовать индекс для таблицы.

>
> ПРИМЕЧАНИЕ: Все связанные с данным индексом объекты, вторичные ключи и прочие элементы базы данных  
>             автоматически обновляются с учетом нового имени.
> 

```python
from src.Migration.BaseMigration import BaseMigration


class RenameIndex(BaseMigration):
    
    def up(self):
        self.rename_index('test_schema.test_table_2', 'my_test_index', 'my_test_index_renamed')

    def down(self):
        self.rename_index('test_schema.test_table_2', 'my_test_index_renamed', 'my_test_index')
```

### Drop index

Метод ```drop_index``` позволяет удалить индекс таблицы.

Поддерживаемые аргументы метода:
  - [array] columns  - имя колонки
  - [string] name    - имя индекса
  - [bool] if_exists - добавить флаг 'IF EXISTS' (может не поддерживаться) (default: False)
  - [bool] cascade   - добавить флаг 'CASCADE' (может не поддерживаться) (default: False)

>
> ПРИМЕЧАНИЕ. Необходимо указать хотя бы один параметр!
> 
> ПРИМЕЧАНИЕ: Приоритет отдается имени (```name```)!
> 

```python
from src.Migration.BaseMigration import BaseMigration


class DropIndex(BaseMigration):
    
    def up(self):
        self.drop_index('test_schema.test_table_2', {'name': 'my_test_index_renamed', 'if_exists': True, 'cascade': True})
        self.drop_index('test_schema.test_table_2', {'columns': ['my_id_2']})

    def down(self):
        self.add_index('test_schema.test_table_2', ['my_id'], {'name': 'my_test_index_renamed', 'unique': True})
        self.add_index('test_schema.test_table_2', ['my_id_2'])
```

### Set/Drop primary key

Методы ```set_primary_key``` и ```drop_primary_key``` позволяют установить (или удалить) новый первичный ключ таблицы.

>
> ПРИМЕЧАНИЕ: При установке первичного ключа столбец для него уже должен присутствовать в таблице.
> 

```python
from src.Migration.BaseMigration import BaseMigration


class SetPrimaryKey(BaseMigration):
    
    def up(self):
        self.set_primary_key('test_schema.test_table_2', 'my_id')

    def down(self):
        self.drop_primary_key('test_schema.test_table_2', 'my_id')
```

### Add/Drop foreign key

Методы ```add_foreign_key``` и ```drop_foreign_key``` позволяют добавить (или удалить) внешний (вторичный) ключ для таблицы.

Поддерживаемые аргументы метода ```add_foreign_key```:
  - [bool] on_update - добавить флаг 'ON UPDATE' (может не поддерживаться)
  - [bool] on_delete - добавить флаг 'ON DELETE' (может не поддерживаться)
  - [string] action  - добавить флаг поведения 'NO ACTION / CASCADE / RESTRICT / SET DEFAULT / SET NULL' (может не поддерживаться)
  - [string] name    - имя вторичного ключа

>
> ПРИМЕЧАНИЕ: При установке вторичного ключа, таблица и ее столбцы, на которые будет ссылаться ключ, должны уже существовать в базе данных, 
>             а типы столбцов должны совпадать. Для MySQL/MariaDB типы данных должны иметь размерность (пример: varchar(128), bigint и т. д.).
> 

>
> ПРИМЕЧАНИЕ: Дополнительные флаги вторичного ключа «ON UPDATE», «ON DELETE», «CASCADE» и «RESTRICT» и другие могут не поддерживаться СУБД. 
>             В этом случае они будут проигнорированы.
> 

```python
from src.Migration.BaseMigration import BaseMigration


class AddForeignKey(BaseMigration):
    
    def up(self):
        self.add_foreign_key('test_schema.test_table_2', ['my_id_2'],
                             'test_schema.test_table_renamed', ['my_id'],
                             {'on_delete': True, 'action': 'CASCADE'})

    def down(self):
        self.drop_foreign_key('test_schema.test_table_2', ['my_id_2'])
```

### Add/Drop foreign key p_key

Методы ```add_foreign_key_p_key``` и ```drop_foreign_key_p_key``` позволяют добавить (или удалить) внешний ключ для таблицы, 
который ссылается на первичный ключ другой таблицы.

Поддерживаемые аргументы метода ```add_foreign_key_p_key```:
  - [bool] on_update - добавить флаг 'ON UPDATE' (может не поддерживаться)
  - [bool] on_delete - добавить флаг 'ON DELETE' (может не поддерживаться)
  - [string] action  - добавить флаг поведения 'NO ACTION / CASCADE / RESTRICT / SET DEFAULT / SET NULL' (может не поддерживаться)
  - [string] name    - имя вторичного ключа

>
> ПРИМЕЧАНИЕ: Метод 'add_foreign_key_p_key' создает внешний ключ, который будет ссылаться на первичный ключ таблицы ref_table_name.
>

>
> ПРИМЕЧАНИЕ: При установке вторичного ключа, таблица, на которую будет ссылаться этот ключ, должна уже существовать в базе данных, а типы столбцов должны совпадать.
> 

>
> ПРИМЕЧАНИЕ: Дополнительные флаги вторичного ключа «ON UPDATE», «ON DELETE», «CASCADE» и «RESTRICT» и другие могут не поддерживаться СУБД. 
>             В этом случае они будут проигнорированы.
> 

```python
from src.Migration.BaseMigration import BaseMigration


class AddForeignKeyPKey(BaseMigration):
    
    def up(self):
        self.create_table('test_schema.test_table_3', {
            'id': False,
            'if_not_exists': True,
            'my_id': {
                'type': 'integer',
                'null': False
            },
            'my_data': {
                'type': 'string',
                'limit': 128,
                'default': ''
            }
        })
        self.add_foreign_key_p_key('test_schema.test_table_3', 'my_id',
                                   'test_schema.test_table_renamed',
                                   {'on_delete': True, 'action': 'CASCADE'})

    def down(self):
        self.drop_foreign_key_p_key('test_schema.test_table_3', 'my_id')
        self.drop_table('test_schema.test_table_3')
```

### Execution of any SQL query

Метод ```execute``` позволяет выполнить любой SQL-запрос.

```python
from src.Migration.BaseMigration import BaseMigration


class ExecuteSQL(BaseMigration):
    
    def up(self):
        self.execute("""
            CREATE TABLE my_test_table (
                my_id int NOT NULL,
                my_data varchar (128) DEFAULT '',
                my_new_column_renamed varchar (256) NOT NULL DEFAULT '---???---',
                CONSTRAINT test_table_pkey PRIMARY KEY (my_id)
            );
        """)

    def down(self):
        self.execute("DROP TABLE my_test_table;")
```

## Выгрузка файлов миграций в SQL-файлы

Для выгрузки файлов миграций в SQL-файлы с версии 1.2.0 добавлены следующие методы:
  - ```--db-migrate-export```     - Выгрузить миграции для всех баз данных (секция: up)
  - ```--db-rollback-export```    - Выгрузить миграции для всех баз данных (секция: down)

>
> ПРИМЕЧАНИЕ:
>
> Для указания каталога куда будут выгружены миграции предусмотрен дополнительный параметр:
>  - ```--dir=[VALUE]```     - Задать каталог для выгрузки SQL-миграций (optional; default: "FLY_CUBE_MIGRATION_DIR/export/")
>
> Если данный каталог отсутствует в системе, то он будет создан.
>
> Пример:
> ```bash
> $> ./fly-cube-migration --db-migrate-export --dir=/home/user/export
> ```
>

Данные команды выгружают из файлов-миграций соответствующие секции (up или down) и сохраняют их в новые SQL-файлы, имена которых формируются из имени миграции + добавления расширения файла ```.sql```.

Данный механизм позволяет использовать штатные консольные утилиты базы данных для установки или удаления миграций без необходимости использования всех требуемых python3 библиотек и инструментов.

>
> ПРИМЕЧАНИЕ:
>
> Перед началом выгрузки миграций каталог для SQL-миграций будет полностью очищен!
>

Для установки SQL-файлов миграций в базу данных в каталоге ```tools``` добавлены bash-скрипты:
  - ```migrate.sh```    - скрипт установки миграций в базу данных
  - ```rollback.sh```   - скрипт удаления миграций из базы данных

### Команда: --db-migrate-export

```bash
$> ./fly-cube-migration --db-migrate-export
=== FlyCubeMigration: Export database migrations ===

Env type: Development
[MigrationsCore] Start export migrations:
[Up][DB: primary] Export (20241002175043 - 'AddWebhookTemplate')
[Up][DB: primary] Export (20241209123002 - 'FixLogicalGroupClassif')
[Up][DB: primary] Export (20241210151026 - 'AddChangelogTable')
[Up][DB: primary] Export (20250109145904 - 'AddClusterTables')
[Up][DB: primary] Export (20250129180207 - 'UpdateWebhookConfigsTemplates')
[Up][DB: primary] Export (20250130164413 - 'AddUpdateTriggerOnNotificationMsgTemplates')
[Up][DB: primary] Export (20250304141405 - 'ChangeParametersCheckInterval')
[Up][DB: primary] Export (20250414180005 - 'UpdateDataSaving')
[Up][DB: primary] Export (20250425160742 - 'FixSqlElementsHistoryDataGetFunc')
[Up][DB: primary] Export (20250604173423 - 'ChangeChildServersInfoTables')
[Up][DB: primary] Export (20250609202742 - 'UpdateHistoryCompression')
[Up][DB: primary] Export (20250619171551 - 'FixSelectChangelogFunc')
[Up][DB: primary] Export (20250626125624 - 'AddIgnoreOldOperativeData')
[Up][DB: primary] Export (20250702143428 - 'ReorderHistoryColumns')
[Up][DB: primary] Export (20250702173821 - 'AddClusterSettingsAndCmdTables')
[Up][DB: primary] Export (20250714155400 - 'AddSipMetadata')
[Up][DB: primary] Export (20250714160441 - 'ClearOldMetadata')
[Up][DB: primary] Export (20250714162919 - 'ClearOldClassifProtocols')
[Up][DB: primary] Export (20250716143254 - 'AddIndexesForHistory')
[Up][DB: primary] Export (20250723145023 - 'ReCreateExtForTableCompressor')
[Up][DB: primary] Export (20250731115107 - 'ChangeMetadataTables')
[Up][DB: primary] Export (20250731115211 - 'AddWebhookNameUniqueConstraint')
[Up][DB: primary] Export (20250806151343 - 'ReCreateExtForTableCompressor2')
[Up][DB: primary] Export (20250820171933 - 'RemoveIndexesForHistoryDump')
[MigrationsCore] Finish export migrations
[MigrationsCore] Directory for export: /home/user/Database/schema_migrations/export/

=== FlyCubeMigration =====================
```

### Установка SQL-миграций скриптом migrate.sh

```bash
$> sh tools/migrate.sh -h

Help:
  -d,  --dir          - set sql migrations directory
  -tv, --to-version   - set max sql migration version (default: None)
  -dh, --dbhost       - set database host address
  -db, --dbname       - set database name
  -u,  --username     - set user name for connect to database
  -p,  --password     - set user password for connect to database

Example usage:

  #> sh tools/migrate.sh --dir export/primary/ -db test -u postgres -p 12345678

  or

  #> sh tools/migrate.sh -d export/primary/ -tv 20250714155400 -db test -u postgres -p 12345678
```

```bash
$> sh tools/migrate.sh --dir /home/user/Database/schema_migrations/export/primary/ -db test -u postgres -p 12345678

Current database version: 20250806151343
[Up] 20250820171933_RemoveIndexesForHistoryDump.sql
Migrate finished
New database version: 20250820171933
```

### Команда: --db-rollback-export

```bash
$> ./fly-cube-migration --db-rollback-export
=== FlyCubeMigration: Export database migrations ===

Env type: Development
[MigrationsCore] Start export migrations:
[Down][DB: primary] Export (20250820171933 - 'RemoveIndexesForHistoryDump')
[Down][DB: primary] Export (20250806151343 - 'ReCreateExtForTableCompressor2')
[Down][DB: primary] Export (20250731115211 - 'AddWebhookNameUniqueConstraint')
[Down][DB: primary] Export (20250731115107 - 'ChangeMetadataTables')
[Down][DB: primary] Export (20250723145023 - 'ReCreateExtForTableCompressor')
[Down][DB: primary] Export (20250716143254 - 'AddIndexesForHistory')
[Down][DB: primary] Export (20250714162919 - 'ClearOldClassifProtocols')
[Down][DB: primary] Export (20250714160441 - 'ClearOldMetadata')
[Down][DB: primary] Export (20250714155400 - 'AddSipMetadata')
[Down][DB: primary] Export (20250702173821 - 'AddClusterSettingsAndCmdTables')
[Down][DB: primary] Export (20250702143428 - 'ReorderHistoryColumns')
[Down][DB: primary] Export (20250626125624 - 'AddIgnoreOldOperativeData')
[Down][DB: primary] Export (20250619171551 - 'FixSelectChangelogFunc')
[Down][DB: primary] Export (20250609202742 - 'UpdateHistoryCompression')
[Down][DB: primary] Export (20250604173423 - 'ChangeChildServersInfoTables')
[Down][DB: primary] Export (20250425160742 - 'FixSqlElementsHistoryDataGetFunc')
[Down][DB: primary] Export (20250414180005 - 'UpdateDataSaving')
[Down][DB: primary] Export (20250304141405 - 'ChangeParametersCheckInterval')
[Down][DB: primary] Export (20250130164413 - 'AddUpdateTriggerOnNotificationMsgTemplates')
[Down][DB: primary] Export (20250129180207 - 'UpdateWebhookConfigsTemplates')
[Down][DB: primary] Export (20250109145904 - 'AddClusterTables')
[Down][DB: primary] Export (20241210151026 - 'AddChangelogTable')
[Down][DB: primary] Export (20241209123002 - 'FixLogicalGroupClassif')
[Down][DB: primary] Export (20241002175043 - 'AddWebhookTemplate')
[MigrationsCore] Finish export migrations
[MigrationsCore] Directory for export: /home/user/Database/schema_migrations/export/

=== FlyCubeMigration =====================
```

### Удаление SQL-миграций скриптом rollback.sh

```bash
$> sh tools/rollback.sh -h

Help:
  -d,  --dir          - set sql migrations directory
  -tv, --to-version   - set min sql migration version (default: 0)
  -dh, --dbhost       - set database host address
  -db, --dbname       - set database name
  -u,  --username     - set user name for connect to database
  -p,  --password     - set user password for connect to database

Note:
  If the arg '--to-version' is default, then all migrations will be removed from the database!

Example usage:

  #> sh tools/rollback.sh --dir export/primary/ -db test -u postgres -p 12345678

  or

  #> sh tools/rollback.sh -d export/primary/ -tv 20250714155400 -db test -u postgres -p 12345678
```

```bash
$> sh tools/rollback.sh --dir /home/user/Database/schema_migrations/export/primary/ -tv 20250806151343 -db test -u postgres -p 12345678

Current database version: 20250820171933
[Down] 20250820171933_RemoveIndexesForHistoryDump.sql
Rollback finished
New database version: 20250806151343
```

## Примеры работы приложения

Ниже приведены примеры выполнения различных команд приложения.

### Команда: --db-migrate-status

```bash
$> ./fly-cube-migration --db-migrate-status

=== FlyCubeMigration: Migrate status ===

Env type: Development
[MigrationsCore] Current database version: 20221216170715
[MigrationsCore] Found migration files: 15
[MigrationsCore] Installed in database: 12
[Installed][DB: primary] Migration (20221216161952 - 'CreateExtension')
[Installed][DB: primary] Migration (20221216162136 - 'CreateSchema')
[Installed][DB: primary] Migration (20221216162220 - 'CreateTable')
[Installed][DB: primary] Migration (20221216163154 - 'RenameTable')
[Installed][DB: primary] Migration (20221216163324 - 'AddColumn')
[Installed][DB: primary] Migration (20221216163600 - 'RenameColumn')
[Installed][DB: primary] Migration (20221216163706 - 'ChangeColumn')
[Installed][DB: primary] Migration (20221216165156 - 'ChangeColumnDefault')
[Installed][DB: primary] Migration (20221216165636 - 'ChangeColumnNull')
[Installed][DB: primary] Migration (20221216165937 - 'AddIndex')
[Installed][DB: primary] Migration (20221216170541 - 'RenameIndex')
[Installed][DB: primary] Migration (20221216170715 - 'DropIndex')
[Not Installed][DB: primary] Migration (20221216170940 - 'SetPrimaryKey')
[Not Installed][DB: primary] Migration (20221216171105 - 'AddForeignKey')
[Not Installed][DB: primary] Migration (20221216171748 - 'AddForeignKeyPKey')

=== FlyCubeMigration =====================
```

### Команда: --db-migrate

```bash
$> ./fly-cube-migration --db-migrate

=== FlyCubeMigration: Migrate database ===

Env type: Development
[MigrationsCore] Start migrate from 20221216170715:
[Skip][DB: primary] Migration (20221216161952 - 'CreateExtension')
[Skip][DB: primary] Migration (20221216162136 - 'CreateSchema')
[Skip][DB: primary] Migration (20221216162220 - 'CreateTable')
[Skip][DB: primary] Migration (20221216163154 - 'RenameTable')
[Skip][DB: primary] Migration (20221216163324 - 'AddColumn')
[Skip][DB: primary] Migration (20221216163600 - 'RenameColumn')
[Skip][DB: primary] Migration (20221216163706 - 'ChangeColumn')
[Skip][DB: primary] Migration (20221216165156 - 'ChangeColumnDefault')
[Skip][DB: primary] Migration (20221216165636 - 'ChangeColumnNull')
[Skip][DB: primary] Migration (20221216165937 - 'AddIndex')
[Skip][DB: primary] Migration (20221216170541 - 'RenameIndex')
[Skip][DB: primary] Migration (20221216170715 - 'DropIndex')
[Up][DB: primary] Migrate to (20221216170940 - 'SetPrimaryKey')
[Up][DB: primary] Migrate to (20221216171105 - 'AddForeignKey')
[Up][DB: primary] Migrate to (20221216171748 - 'AddForeignKeyPKey')
[MigrationsCore] Finish migrate
[MigrationsCore] Current migration version: 20221216171748
[MigrationsCore] Execute post-scripts:
[Skip] List of post-scripts is Empty.
[MigrationsCore] Finish execute post-scripts

=== FlyCubeMigration =====================
```

### Команда: --db-rollback

```bash
$> ./fly-cube-migration --db-rollback

=== FlyCubeMigration: Rollback database ===

Env type: Development
[MigrationsCore] Start rollback from 20221216171748:
[Down][DB: primary] Migrate from (20221216171748 - 'AddForeignKeyPKey')
[MigrationsCore] Finish rollback
[MigrationsCore] Current migration version: 20221216171105
[MigrationsCore] Execute post-scripts:
[Skip] List of post-scripts is Empty.
[MigrationsCore] Finish execute post-scripts

=== FlyCubeMigration =====================
```

### Команда: --db-rollback-all

```bash
$> ./fly-cube-migration --db-rollback-all

=== FlyCubeMigration: Rollback database ===

Env type: Development
[MigrationsCore] Start rollback from 20221216171105:
[Skip][DB: primary] Migration (20221216171748 - 'AddForeignKeyPKey')
[Down][DB: primary] Migrate from (20221216171105 - 'AddForeignKey')
[Down][DB: primary] Migrate from (20221216170940 - 'SetPrimaryKey')
[Down][DB: primary] Migrate from (20221216170715 - 'DropIndex')
[Down][DB: primary] Migrate from (20221216170541 - 'RenameIndex')
[Down][DB: primary] Migrate from (20221216165937 - 'AddIndex')
[Down][DB: primary] Migrate from (20221216165636 - 'ChangeColumnNull')
[Down][DB: primary] Migrate from (20221216165156 - 'ChangeColumnDefault')
[Down][DB: primary] Migrate from (20221216163706 - 'ChangeColumn')
[Down][DB: primary] Migrate from (20221216163600 - 'RenameColumn')
[Down][DB: primary] Migrate from (20221216163324 - 'AddColumn')
[Down][DB: primary] Migrate from (20221216163154 - 'RenameTable')
[Down][DB: primary] Migrate from (20221216162220 - 'CreateTable')
[Down][DB: primary] Migrate from (20221216162136 - 'CreateSchema')
[Down][DB: primary] Migrate from (20221216161952 - 'CreateExtension')
[MigrationsCore] Finish rollback
[MigrationsCore] Current migration version: 0
[MigrationsCore] Execute post-scripts:
[Skip] List of post-scripts is Empty.
[MigrationsCore] Finish execute post-scripts

=== FlyCubeMigration =====================
```

### Команда: --db-settings

```bash
$> ./fly-cube-migration --db-settings

=== FlyCubeMigration: Database settings ===

Env type: Development
Database settings:
  adapter: postgresql
  database: test
  host: 127.0.0.1
  port: 5432
  username: postgres
  password: 12345678

=== FlyCubeMigration ======================
```

### Команда: --make-migration-number

```bash
$> ./fly-cube-migration --make-migration-number

=== FlyCubeMigration: Make migration number ===
20231114171323
=== FlyCubeMigration ==========================
```
