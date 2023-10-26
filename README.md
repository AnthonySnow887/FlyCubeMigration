# FlyCubeMigration

[![License](https://img.shields.io/github/license/AnthonySnow887/FlyCubeMigration)](https://github.com/AnthonySnow887/FlyCubeMigration/blob/master/LICENSE)
[![Latest Release](https://img.shields.io/github/v/release/AnthonySnow887/FlyCubeMigration?label=release)](https://github.com/AnthonySnow887/FlyCubeMigration/releases)
![Last Commit](https://img.shields.io/github/last-commit/AnthonySnow887/FlyCubeMigration/develop)

FlyCubeMigration is a tool developed in Python that follows the ideology and principles of database migration 
found in Ruby on Rails. FlyCubeMigration completely repeats the functionality of the migration core 
implemented in the MVC Web Framework FlyCubePHP.

Installation of each migration is performed in transactional mode and in case of errors, 
rolls back the state of the database to the stage before installation.

Supported databases
-------------------

- SQLite 3;
- PostgreSQL 9.6 or later.
- MySQL/MariaDB (tested on MariaDB 10.2.36)

Operating systems tested
------------------------

- Alma Linux 9.1
- Alt Linux 8.1 and later
- Astra Linux 1.6 / 1.7 / 2.12
- CentOS 8.5
- Debian 12 and later
- OpenSUSE 15.1 and later
- RedOS 7
- Rosa Linux 12.4
- Ubuntu 20.04 and later

Basic system requirements
-------------------------

- python >= 3.6

Additional required Python modules
----------------------------------

- python3-psycopg2
- python3-mysql-connector-python
- python3-PyYAML
- python3-requests

Releases
--------

Releases of FlyCubeMigration are available on [Github](https://github.com/AnthonySnow887/FlyCubeMigration/releases).

License
-------

FlyCubeMigration is licensed under the GPL-3.0 License. See the LICENSE file for details.

Usage
-----

```bash
FlyCubeMigration> ./fly-cube-migration --help

Usage: ./fly-cube-migration [options]

Options include:

  --help                 Show help [-h, -?]
  --version              Print the version [-v]
  --latest-version       Select latest version from GitHub [-lv]
  --env=[VALUE]          Set current environment (production/development; default: development) 
  --output=[VALUE]       Show sql output (optional) (default: false) 
  --config-dir=[VALUE]   Set FlyCubeMigration config file directory (optional) (default: 'config/') 
  --save-config-dir      Save in settings FlyCubeMigration config file directory 
  --clear-config-dir     Clear from settings FlyCubeMigration config file directory 
  --settings             Show current FlyCubeMigration config settings 


  --new-migration        Create new migration 

  --db-create            Create all databases for current environment 
  --db-create-all        Create all databases for all environments (development and production) 

  --db-drop              Drop all databases for current environment 
  --db-drop-all          Drop all databases for all environments (development and production) 

  --db-migrate           Start all database(s) migrations 

  --db-migrate-redo      Start re-install last database migration 

  --db-migrate-status    Select migrations status 

  --db-rollback          Start uninstall last database migration 
  --db-rollback-all      Start uninstall all database(s) migrations 

  --db-version           Select database(s) migration version 

  --name=[VALUE]         Set new object name 
  --to-version=[VALUE]   Set needed migration version (optional; if 0 - uninstall all migrations) 
  --step=[VALUE]         Set needed number of steps for uninstall (re-install) migrations (optional; default: 1) 

Examples:

 1. Set FlyCubeMigration config directory ('--config-dir' is grouped with all the commands listed below):
     ./fly-cube-migration --config-dir=../test/config/ [Other Commands]

 2. Set current environment ('--env' is grouped with all the commands listed below):
     ./fly-cube-migration --env=production [Other Commands]

 3. Show sql output ('--output' is grouped with all the commands listed below):
     ./fly-cube-migration --output=true [Other Commands]

 4. Create new migration:
     ./fly-cube-migration --new-migration --name=ExampleMigration

 5. Select database migration version:
     ./fly-cube-migration --db-version

 6. Select database migrations status:
     ./fly-cube-migration --db-migrate-status

 7. Install all migrations:
     ./fly-cube-migration --db-migrate

 8. Install needed migrations:
     ./fly-cube-migration --db-migrate --to-version=20210309092620

 9. Uninstall last migration:
     ./fly-cube-migration --db-rollback

10. Uninstall last N-steps migrations:
     ./fly-cube-migration --db-rollback --step=3

11. Uninstall all migrations (ver. 1):
     ./fly-cube-migration --db-rollback-all

12. Uninstall all migrations (ver. 2):
     ./fly-cube-migration --db-migrate --to-version=0

13. Re-Install last migration:
     ./fly-cube-migration --db-migrate-redo

14. Re-Install last N-steps migrations:
     ./fly-cube-migration --db-migrate-redo --step=3
```

FlyCubeMigration configure file
-------------------------------

The configuration file must be located in directory ```config/``` and his name must match ```fly-cube-migration.yml```.
Full path to the file: ```config/fly-cube-migration.yml```

If you want to use a different configuration file, then run the application with the command: 
```bash
--config-dir=[PATH TO THE CONGIG FILE DIRECTORY]
```

Example:
```bash
$> ./fly-cube-migration --config-dir=../test/config/ [Other Commands]
```

If you always want to use this configuration file, you can save it in the system settings of the application:
```bash
--save-config-dir
```

Example:
```bash
$> ./fly-cube-migration --config-dir=../test/config/ --save-config-dir
```

>
> NOTE: After saving the settings, you can not specify the directory of the configuration file when executing other commands.
> 

if you need to clear the saved settings, then run the command:
```bash
--clear-config-dir
```

Example:
```bash
$> ./fly-cube-migration --clear-config-dir
```

To get a list of current application configurations use:
```bash
--settings
```

Example:
```bash
$> ./fly-cube-migration --settings

=== FlyCubeMigration =========================

Config file: /home/user/Projects/FlyCubeMigration/config/fly-cube-migration.yml
Values:
 - FLY_CUBE_MIGRATION_DB_CONFIG_DIR: config/
 - FLY_CUBE_MIGRATION_DB_MIGRATIONS_DIR: db/migrate/

=== FlyCubeMigration =========================
```

Default config file example:
```yaml
#
# Directory for database config file 'database.yml'
#
FLY_CUBE_MIGRATION_DB_CONFIG_DIR: "config/"

#
# Directory for database migration files
#
FLY_CUBE_MIGRATION_DB_MIGRATIONS_DIR: "db/migrate/"
```
 
Database configure file
-----------------------

By default, the database configuration file is located in the directory ```config/``` and his name must match ```database.yml```.
Full path to the file: ```config/database.yml```

This file can contain an unlimited number of settings for connecting to different DBMS, 
but the fields "production", "development", "production_secondary" and "development_secondary" can only be set once. 
These fields indicate to the system kernel which section of the settings should be used for connection 
and which adapter should be created in one or another mode of the application.

Secondary settings:
  - "production_secondary" - contains a "key-value" array of additional database access sections for "production mode";
  - "development_secondary" - contains a "key-value" array of additional database access sections for "development mode".

>
> NOTE: The secondary database key can be used to indicate which database the migration belongs to.
> 

If you want to use another directory, then set the full path to it in the FlyCubeMigration configuration file:
```yaml
#
# Directory for database config file 'database.yml'
#
FLY_CUBE_MIGRATION_DB_CONFIG_DIR: "/home/user/test/config/"
```

Default config file example:
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

Migration description
---------------------

Migrations are a convenient way to manage the structure of your database. Like Ruby on Rails, 
the FlyCubeMigration migration system provides a wide range of methods for working with the database schema. 
This approach allows you not to use SQL to describe or change the database schema, 
which in turn makes it possible not to depend on a specific DBMS and its properties.

Each new migration makes changes to the database structure by adding, changing or deleting tables, 
their columns or properties, and can be considered as a "new" version of the database.

To avoid problems and conflicts when installing migrations, each new file gets a unique prefix, 
which is also its version. The prefix is the current date-time in ```YYYYMMDDHHmmSS``` format, where:
  - YYYY - year;
  - MM   - month with leading zero (01-12);
  - DD   - day with leading zero (01-31);
  - HH   - hours with leading zero in 24 hour format (00-23);
  - mm   - minutes with leading zero (00-59);
  - SS   - seconds with leading zero (00-59).

This approach allows you to install migrations only in the order in which they were created. 
All versions of installed migrations are stored in the database, which allows you to get full information about 
the current version of the database or the status of each migration from the list of available ones at any time.

Installation or removal (rollback) of migrations is performed sequentially in the transaction mode, 
if it is supported by the DBMS. In case of a successful operation, the current version of the migrations is saved to the database.

All migration classes are derived from base class BaseMigration.

The migration class must override two abstract methods:
  - up   - method to make migration changes to database 
  - down - method to remove migration changes from database

Optional abstract method:
  - configuration - migration configuration method (called before running install/rollback migration)

> 
> If you need to specify the name of the database to which the current migration file belongs, 
> then use the ```set_database(...)``` function.
> 
> NOTE: In this case, you must specify the database name key specified in the list of secondary databases.
> 
> Database config file example:
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
> Migration file example:
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

The default directory for storing and searching for migrations is ```db/migrate/```.

If you want to use another directory, then set the full path to it in the FlyCubeMigration configuration file:
```yaml
#
# Directory for database migration files
#
FLY_CUBE_MIGRATION_DB_MIGRATIONS_DIR: "/home/user/test/db/migrate/"
```

Migration class example:
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

Migration examples
------------------

The following are examples of using different migration methods.

Create/Drop Extension
---------------------

The ```create_extension``` and ```drop_extension``` methods allow you to enable (or disable) the required database extension.

Supported arguments for the ```create_extension``` method:
  - [bool] if_not_exists - add 'IF NOT EXISTS' flag

Supported arguments for the ```drop_extension``` method:
  - [bool] if_exists - add 'IF EXISTS' flag

>
> NOTE: If the database does not support this functionality, the operation is ignored.
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

Create/Drop Schema
------------------

The ```create_schema``` and ```drop_schema``` methods allow you to create (or drop) a new data schema.

Supported arguments for the ```create_schema``` method:
  - [bool] if_not_exists - add 'IF NOT EXISTS' flag

Supported arguments for the ```drop_schema``` method:
  - [bool] if_exists - add 'IF EXISTS' flag

>
> NOTE: If the database does not support this functionality, the operation is ignored.
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

Create table
------------

The ```create_table``` method allows you to create a new table in the database.

Supported Keys:
  - [bool]     if_not_exists  - add 'IF NOT EXISTS' flag (table only)
  - [bool]     id             - use ID column or not (will be set as primary key)
  - [string]   type           - column data type (required)
  - [integer]  limit          - column data size
  - [bool]     null           - can it be NULL
  - [string]   default        - default value
  - [bool]     primary_key    - use as primary key
  - [bool]     unique         - is unique column
  - [string]   unique_group   - is a unique columns group (value: group name)

>
> NOTE: Differences between ```unique``` and ```unique_group``` argument keys:
> - unique       - indicates that the values in the data column must be unique;
> - unique_group - indicates that the column is included in the array of unique columns, 
>                  the name of which is specified in the arguments (SQL: ```UNIQUE(column_1, column_2, column_3)```).
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

SQL query example above for PostgreSQL:
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

Rename table
------------

The ```rename_table``` method allows you to rename a table.

```python
from src.Migration.BaseMigration import BaseMigration


class RenameTable(BaseMigration):
    
    def up(self):
        self.rename_table('test_schema.test_table', 'test_schema.test_table_renamed')

    def down(self):
        self.rename_table('test_schema.test_table_renamed', 'test_schema.test_table')
```

Drop table
----------

The ```drop_table``` method allows you to drop a previously created table.

```python
from src.Migration.BaseMigration import BaseMigration


class DropTable(BaseMigration):
    
    def up(self):
        self.drop_table('test_schema.test_table')

    def down(self):
        return 
```

Add column
----------

The ```add_column``` method allows you to add a new column to a previously created table.

Supported Props:
  - [bool]     if_not_exists  - add 'IF NOT EXISTS' flag
  - [string]   type           - column data type (required)
  - [integer]  limit          - column data size
  - [bool]     null           - can it be NULL
  - [string]   default        - default value

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

Rename column
-------------

The ```rename_column``` method allows you to rename a column in a table.

>
> NOTE: All objects associated with this column, secondary keys, and other database elements 
>       are automatically updated with the new name.
>

```python
from src.Migration.BaseMigration import BaseMigration


class RenameColumn(BaseMigration):
    
    def up(self):
        self.rename_column('test_schema.test_table_renamed', 'my_new_column', 'my_new_column_renamed')

    def down(self):
        self.rename_column('test_schema.test_table_renamed', 'my_new_column_renamed', 'my_new_column')
```

Change column
-------------

The ```change_column``` method allows you to change the type of the column and its optional parameters, if they are set.

Supported Props:
  - [integer]  limit          - column data size
  - [bool]     null           - can it be NULL
  - [string]   default        - default value

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

Change column default
---------------------

The ```change_column_default``` method allows you to change/delete the ```DEFAULT``` property of a table column.

>
> NOTE: If value of the DEFAULT section is None, the DEFAULT section is deleted.
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

Change column null
------------------

The ```change_column_null``` method allows you to add/remove the ```NOT NULL``` property of a table column.

>
> NOTE: If 'not_null' value is False - section NOT NULL is removed.
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

Drop column
-----------

The ```drop_column``` method allows you to drop a column from a table.

```python
from src.Migration.BaseMigration import BaseMigration


class DropColumn(BaseMigration):
    
    def up(self):
        self.drop_column('test_schema.test_table_renamed', 'my_new_column')

    def down(self):
        return 
```

Add index
---------

The ```add_index``` method allows you to add an index to a table.

Supported Props:
  - [string] name    - index name (optional)
  - [bool]   unique  - is it unique

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

Rename index
------------

The ```rename_index``` method allows you to rename an index for a table.

>
> NOTE: All objects associated with this index, secondary keys, and other database elements 
>       are automatically updated with the new name.
> 

```python
from src.Migration.BaseMigration import BaseMigration


class RenameIndex(BaseMigration):
    
    def up(self):
        self.rename_index('test_schema.test_table_2', 'my_test_index', 'my_test_index_renamed')

    def down(self):
        self.rename_index('test_schema.test_table_2', 'my_test_index_renamed', 'my_test_index')
```

Drop index
----------

The ```drop_index``` method allows you to drop a table index.

Supported Props:
  - [array] columns  - column names
  - [string] name    - index name
  - [bool] if_exists - add 'IF EXISTS' flag (may not be supported) (default: False)
  - [bool] cascade   - add 'CASCADE' flag (may not be supported) (default: False)

>
> NOTE: At least one parameter must be specified!
> 
> NOTE: Priority is given to name!
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

Set/Drop primary key
--------------------

The ```set_primary_key``` and ```drop_primary_key``` methods allow you to set (or drop) a new primary key for a table.

>
> NOTE: When setting up a primary key, the column for the new primary key must already be present in the table.
> 

```python
from src.Migration.BaseMigration import BaseMigration


class SetPrimaryKey(BaseMigration):
    
    def up(self):
        self.set_primary_key('test_schema.test_table_2', 'my_id')

    def down(self):
        self.drop_primary_key('test_schema.test_table_2', 'my_id')
```

Add/Drop foreign key
--------------------

The ```add_foreign_key``` and ```drop_foreign_key``` methods allow you to add (or remove) a foreign (secondary) key for a table.

Supported arguments for the ```add_foreign_key``` method:
  - [bool] on_update - add 'ON UPDATE' flag (may not be supported)
  - [bool] on_delete - add 'ON DELETE' flag (may not be supported)
  - [string] action  - add behavior flag 'NO ACTION / CASCADE / RESTRICT / SET DEFAULT / SET NULL' (may not be supported)
  - [string] name    - foreign key name

>
> NOTE: When setting a secondary key, the table and its columns to which the key will refer must already exist in the database, 
>       and the column types must match. For MySQL/MariaDB, data types must have a dimension (example: varchar(128), bigint, etc.).
> 

>
> NOTE: Additional secondary key flags "ON UPDATE", "ON DELETE", "CASCADE" and "RESTRICT" and others may not be supported by the DBMS. 
>       In this case, they will be ignored.
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

Add/Drop foreign key p_key
--------------------------

The ```add_foreign_key_p_key``` and ```drop_foreign_key_p_key``` methods allow you to add (or remove) a foreign key for a table,
that refers to the primary key of another table.

Supported arguments for the ```add_foreign_key_p_key``` method:
  - [bool] on_update - add 'ON UPDATE' flag (may not be supported)
  - [bool] on_delete - add 'ON DELETE' flag (may not be supported)
  - [string] action  - add behavior flag 'NO ACTION / CASCADE / RESTRICT / SET DEFAULT / SET NULL' (may not be supported)
  - [string] name    - foreign key name

>
> NOTE: The 'add_foreign_key_p_key' method creates a foreign key that will refer to the primary key of the ref_table_name table.
>

>
> NOTE: When setting a secondary key, the table that the key will refer to must already exist in the database, and the column types must match.
> 

>
> NOTE: Additional secondary key flags "ON UPDATE", "ON DELETE", "CASCADE" and "RESTRICT" and others may not be supported by the DBMS. 
>       In this case, they will be ignored.
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

Execution of any SQL query
--------------------------

The ```execute``` method allows you to execute any SQL query.

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

Work examples
-------------

The following are examples of executing various application commands.

Command: --db-migrate-status
----------------------------

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

Command: --db-migrate
---------------------

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

=== FlyCubeMigration =====================
```

Command: --db-rollback
----------------------

```bash
$> ./fly-cube-migration --db-rollback

=== FlyCubeMigration: Rollback database ===

Env type: Development
[MigrationsCore] Start rollback from 20221216171748:
[Down][DB: primary] Migrate from (20221216171748 - 'AddForeignKeyPKey')
[MigrationsCore] Finish rollback
[MigrationsCore] Current migration version: 20221216171105

=== FlyCubeMigration =====================
```

Command: --db-rollback-all
--------------------------

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

=== FlyCubeMigration =====================
```
