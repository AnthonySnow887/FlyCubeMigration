from abc import ABCMeta, abstractmethod, abstractproperty
from src.Helper.Helper import Helper


class BaseMigrator:
    __metaclass__ = ABCMeta
    _db_adapter = None
    _export_file = None

    def __init__(self, db_adapter, export_file: str = None):
        self._db_adapter = db_adapter
        self._export_file = export_file

    #
    # base methods to override if needed:
    #

    def create_database(self, name: str, props: dict = {}):
        """Создать новую базу данных

        :param name: название базы данных
        :type name: str
        :param props: свойства
        :type props: dict

        NOTE: override this method for correct implementation.
        """

        return

    def drop_database(self, name: str):
        """Удалить базу данных

        :param name: название базы данных
        :type name: str

        NOTE: override this method for correct implementation.
        """

        return

    def create_extension(self, name: str, props: dict = {}):
        """Подключить расширение базы данных

        :param name: название
        :type name: str
        :param props: свойства
        :type props: dict

        Supported Props:
          - [bool] if_not_exists - добавить флаг 'IF NOT EXISTS'

        NOTE: override this method for correct implementation.
        """

        return

    def drop_extension(self, name: str, props: dict = {}):
        """Удалить расширение базы данных

        :param name: название
        :type name: str
        :param props: свойства
        :type props: dict

        Supported Props:
          - [bool] if_exists - добавить флаг 'IF EXISTS'

        NOTE: override this method for correct implementation.
        """

        return

    def create_schema(self, name: str, props: dict = {}):
        """Создать новую схему данных

        :param name: название
        :type name: str
        :param props: свойства
        :type props: dict

        Supported Props:
          - [bool] if_not_exists - добавить флаг 'IF NOT EXISTS'

        NOTE: override this method for correct implementation.
        """

        return

    def drop_schema(self, name: str, props: dict = {}):
        """Удалить схему данных

        :param name: название
        :type name: str
        :param props: свойства
        :type props: dict

        Supported Props:
          - [bool] if_exists - добавить флаг 'IF EXISTS'

        NOTE: override this method for correct implementation.
        """

        return

    def table_indexes(self, table_name: str) -> dict:
        """Запросить список индексов для таблицы

        :param table_name: название таблицы
        :type table_name: str
        :rtype: dict

        Return example:
        {
            'index_1': {
                'index_name': 'index_1',
                'unique': True,
                'table': 'test_table',
                'columns': [ 'column_1', 'column_2']
            }
            'index_2': {
                'index_name': 'index_2',
                'unique': False,
                'table': 'test_table',
                'columns': [ 'column_2' ]
            }
            ...
        }

        NOTE: override this method for correct implementation.
        """

        return {}

    def table_columns(self, table_name: str) -> dict:
        """Запросить список колонок таблицы и их типов

        :param table_name: название таблицы
        :type table_name: str
        :rtype: dict

        Return example:
        {
            'column_1': {
                'table': 'test_table',
                'column': 'column_1',
                'type': 'text',
                'is_pk': True,
                'is_not_null': True
                'default': None
            }
            'column_2': {
                'table': 'test_table',
                'column': 'column_2',
                'type': 'integer'
                'is_pk': False
                'is_not_null': False
                'default': 999
            }
            ...
        }

        NOTE: override this method for correct implementation.
        """

        return {}

    def table_primary_keys(self, table_name: str) -> dict:
        """Запросить список первичных ключей таблицы

        :param table_name: название таблицы
        :type table_name: str
        :rtype: dict

        Return example:
        {
            'test_pkey': {
                'name':'test_pkey'
                'table': 'public.test',
                'column': 'my_id',
                'type': 'integer'
            }
        }

        NOTE: override this method for correct implementation.
        """

        return {}

    def table_foreign_keys(self, table_name) -> dict:
        """Запросить список вторичных ключей для таблицы

        :param table_name: название таблицы
        :type table_name: str
        :rtype: dict

        Return example:
        {
            'fk_test_2_test_id': {
                'name':'fk_test_2_test_id',
                'table': 'public.test_2',
                'column': 'test_id',
                'ref_table': 'public.test',
                'ref_column': 'my_id'
                'on_update': 'NO ACTION',
                'on_delete': 'NO ACTION'
            }
            ...
        }

        NOTE: override this method for correct implementation.
        """

        return {}

    def to_database_type(self, name: str, limit: int = None) -> str:
        """Преобразование типа колонки в тип базы данных

        :param name: имя типа
        :type name: str
        :param limit: размер данных
        :type limit: int
        :rtype: str

        NOTE: override this method for correct implementation.
        """

        if name == 'string':
            if limit:
                return f"varchar ({limit})"
            else:
                return "text"
        if limit:
            return f"{name} ({limit})"
        return name

    def make_default_value(self, def_value: str, value_type: str) -> str:
        """Создать SQL подстроку с базовым значением

        :param def_value: базовое значение
        :type def_value: str
        :param value_type: тип данных колонки
        :type value_type: str
        :rtype: str

        NOTE: override this method for correct implementation.
        """

        if value_type.find("text") != -1 or value_type.find("varchar") != -1 or value_type.find("character varying") != -1:
            return f"DEFAULT ('{def_value}')"
        return f"DEFAULT ({def_value})"

    def make_reference_action(self, action: str) -> str:
        """Создать корректный флаг ACTION для reference

        :param action: значение ('NO ACTION / CASCADE / RESTRICT / SET DEFAULT / SET NULL')
        """

        action = action.lower().strip()
        if action == 'no action':
            return 'NO ACTION'
        elif action == 'cascade':
            return 'CASCADE'
        elif action == 'restrict':
            return 'RESTRICT'
        elif action == 'set default':
            return 'SET DEFAULT'
        elif action == 'set null':
            return 'SET NULL'
        return 'NO ACTION'

    #
    # public methods
    #

    def create_table(self, name: str, args: dict):
        """Создать таблицу

        :param name: название
        :type name: str
        :param args: массив колонок и их спецификация
        :type args: dict

        Supported Keys:
            [bool]     if_not_exists  - добавить флаг 'IF NOT EXISTS' (только для таблицы)
            [bool]     id             - использовать колонку ID или нет (будет задана как первичный ключ)
            [string]   type           - тип данных колонки (обязательный)
            [integer]  limit          - размер данных колонки
            [bool]     null           - может ли быть NULL
            [string]   default        - базовое значение
            [bool]     primary_key    - использовать как первичный ключ
            [bool]     unique         - является уникальным
            [string]   unique_group   - является уникальной группой (значение: имя группы)

        NOTE:
            id - serial not NULL (for MySQL: bigint unsigned)

            createTable('test', {
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
                    'default': ''
                }
            });
        """

        if name == "":
            raise Exception("[BaseMigrator][create_table] Table name is Empty!")
        if not self._db_adapter:
            raise Exception("[BaseMigrator][create_table] Database adapter is None!")
        if_not_exists = ""
        if args.get('if_not_exists', False):
            if_not_exists = "IF NOT EXISTS"
            args.pop('if_not_exists', None)
        tmp_name = self._db_adapter.quote_table_name(name)
        sql = f"CREATE TABLE {if_not_exists} {tmp_name} (\n"
        sql += self._prepare_create_table(name, args)
        sql += "\n);"
        self._exec_query_or_export(sql)

    def rename_table(self, name: str, new_name: str):
        """Переименовать таблицу

        :param name: имя
        :param new_name: новое имя
        :return:
        """

        if name == "" or new_name == "":
            raise Exception("[BaseMigrator][rename_table] Table name or new table name is Empty!")
        if not self._db_adapter:
            raise Exception("[BaseMigrator][rename_table] Database adapter is None!")
        tmp_indexes = self.table_indexes(name)
        tmp_name = self._db_adapter.quote_table_name(name)
        tmp_new_name = self._db_adapter.quote_table_name(new_name)
        self._exec_query_or_export(f"ALTER TABLE {tmp_name} RENAME TO {tmp_new_name};")
        for k, v in tmp_indexes.items():
            index_new_name = str(v['index_name']).replace(name, new_name)
            if str(v['index_name']) == index_new_name:
                continue
            self.rename_index(new_name, str(v['index_name']), index_new_name)

    def drop_table(self, name: str, props: dict = {}):
        """Удалить таблицу

        :param name: название
        :param props: свойства

        Supported Props:
            [bool] if_exists - добавить флаг 'IF EXISTS'
            [bool] cascade   - добавить флаг 'CASCADE'
        """

        if name == "":
            raise Exception("[BaseMigrator][drop_table] Table name is Empty!")
        if not self._db_adapter:
            raise Exception("[BaseMigrator][drop_table] Database adapter is None!")
        name = self._db_adapter.quote_table_name(name)
        sql = f"DROP TABLE {name}"
        if props.get('if_exists', False):
            sql += " IF EXISTS"
        if props.get('cascade', False):
            sql += " CASCADE"
        self._exec_query_or_export(f"{sql};")

    def add_column(self, table_name: str, column_name: str, props: dict = {}):
        """Добавить колонку в таблицу

        :param table_name: название таблицы
        :param column_name: название колонки
        :param props: свойства

        Supported Props:
            [bool]     if_not_exists  - добавить флаг 'IF NOT EXISTS'
            [string]   type           - тип данных колонки (обязательный)
            [integer]  limit          - размер данных колонки
            [bool]     null           - может ли быть NULL
            [string]   default        - базовое значение
        """

        if table_name == "" or column_name == "":
            raise Exception("[BaseMigrator][add_column] Table name or column name is Empty!")
        if not self._db_adapter:
            raise Exception("[BaseMigrator][add_column] Database adapter is None!")
        if_not_exists = ""
        if props.get('if_not_exists', False):
            if_not_exists = "IF NOT EXISTS"
            props.pop('if_not_exists', None)
        tmp_res = self._prepare_create_column(column_name, props)
        if not tmp_res.get('sql'):
            raise Exception("[BaseMigrator][add_column] Prepare create column return empty result!")
        tmp_table_name = self._db_adapter.quote_table_name(table_name)
        self._exec_query_or_export(f"ALTER TABLE {tmp_table_name} ADD COLUMN {if_not_exists} {tmp_res.get('sql')};")

    def rename_column(self, table_name: str, column_name: str, column_new_name: str):
        """Переименовать колонку в таблице

        :param table_name: название таблицы
        :param column_name: название колонки
        :param column_new_name: новое название колонки
        """

        if table_name == "" or column_name == "" or column_new_name == "":
            raise Exception("[BaseMigrator][rename_column] Table name or column name or column new name is Empty!")
        if column_name == column_new_name:
            raise Exception("[BaseMigrator][rename_column] Column name is the same as new column name!")
        if not self._db_adapter:
            raise Exception("[BaseMigrator][rename_column] Database adapter is None!")
        tmp_indexes = self.table_indexes(table_name)
        tmp_table_name = self._db_adapter.quote_table_name(table_name)
        tmp_column_name = self._db_adapter.quote_table_name(column_name)
        tmp_column_new_name = self._db_adapter.quote_table_name(column_new_name)
        self._exec_query_or_export(f"ALTER TABLE {tmp_table_name} RENAME COLUMN {tmp_column_name} TO {tmp_column_new_name};")
        for k, v in tmp_indexes.items():
            if not column_name in v['columns']:
                continue
            index_new_name = f"{table_name}_{column_name}_index"
            self.rename_index(table_name, str(v['index_name']), index_new_name)

    def change_column(self, table_name: str, column_name: str, new_type: str, props: dict = {}):
        """Изменить тип колонки и ее дополнительные параметры, если они заданы

        :param table_name: название таблицы
        :param column_name: название колонки
        :param new_type: новый тип данных
        :param props: свойства

        Supported Props:
          - [integer]  limit          - размер данных колонки
          - [bool]     null           - может ли быть NULL
          - [string]   default        - базовое значение
        """

        if table_name == "" or column_name == "" or new_type == "":
            raise Exception("[BaseMigrator][change_column] Table name or column name or new type is Empty!")
        if not self._db_adapter:
            raise Exception("[BaseMigrator][change_column] Database adapter is None!")
        table_name = self._db_adapter.quote_table_name(table_name)
        # drop default
        sql = f"ALTER TABLE {table_name} ALTER COLUMN {self._db_adapter.quote_table_name(column_name)} DROP DEFAULT;"
        self._exec_query_or_export(sql)
        # change type
        tmp_limit = props.get('limit', None)
        if tmp_limit:
            tmp_limit = int(tmp_limit)
        tmp_type = self.to_database_type(new_type, tmp_limit)
        tmp_type_using = str(tmp_type)
        t_pos = tmp_type_using.find("(")
        if t_pos != -1:
            tmp_type_using = str(tmp_type_using[0:t_pos]).strip()
        sql = f"ALTER TABLE {table_name} ALTER COLUMN {self._db_adapter.quote_table_name(column_name)} TYPE {tmp_type} USING ({column_name}::{tmp_type_using});"
        self._exec_query_or_export(sql)
        # change default
        if props.get('default', None):
            tmp_default = self.make_default_value(str(props['default']), tmp_type)
            sql = f"ALTER TABLE {table_name} ALTER COLUMN {self._db_adapter.quote_table_name(column_name)} SET {tmp_default}; "
            self._exec_query_or_export(sql)
        # change not null
        if props.get('null', None):
            if not props.get('null'):
                sql = f"ALTER TABLE {table_name} ALTER COLUMN {self._db_adapter.quote_table_name(column_name)} SET NOT NULL; "
            else:
                sql = f"ALTER TABLE {table_name} ALTER COLUMN {self._db_adapter.quote_table_name(column_name)} DROP NOT NULL; "
            self._exec_query_or_export(sql)

    def change_column_default(self, table_name: str, column_name: str, default=None):
        """Изменить/Удалить секцию DEFAULT у колонки

        :param table_name: название таблицы
        :param column_name: название колонки
        :param default: значение секции DEFAULT (если None - секция DEFAULT удаляется)
        """

        if table_name == "" or column_name == "":
            raise Exception("[BaseMigrator][change_column_default] Table name or column name is Empty!")
        if not self._db_adapter:
            raise Exception("[BaseMigrator][change_column_default] Database adapter is None!")
        if not default:
            # drop default
            table_name = self._db_adapter.quote_table_name(table_name)
            sql = f"ALTER TABLE {table_name} ALTER COLUMN {self._db_adapter.quote_table_name(column_name)} DROP DEFAULT;"
            self._exec_query_or_export(sql)
        else:
            # replace default
            tmp_columns = self.table_columns(table_name)
            if not column_name in tmp_columns:
                raise Exception(f"[BaseMigrator][change_column_default] Not found column \"{column_name}\" in table columns list!")
            tmp_type = tmp_columns[column_name]['type']
            tmp_default = self.make_default_value(default, tmp_type)
            table_name = self._db_adapter.quote_table_name(table_name)
            sql = f"ALTER TABLE {table_name} ALTER COLUMN {self._db_adapter.quote_table_name(column_name)} SET {tmp_default};"
            self._exec_query_or_export(sql)

    def change_column_null(self, table_name: str, column_name: str, not_null: bool = False):
        """Добавить/Удалить секцию NOT NULL у колонки

        :param table_name: название таблицы
        :param column_name: название колонки
        :param not_null: значение секции (если False - секция NOT NULL удаляется)
        """

        if table_name == "" or column_name == "":
            raise Exception("[BaseMigrator][change_column_null] Table name or column name is Empty!")
        if not self._db_adapter:
            raise Exception("[BaseMigrator][change_column_null] Database adapter is None!")
        table_name = self._db_adapter.quote_table_name(table_name)
        if not_null:
            self._exec_query_or_export(f"ALTER TABLE {table_name} ALTER COLUMN {self._db_adapter.quote_table_name(column_name)} SET NOT NULL;")
        else:
            self._exec_query_or_export(f"ALTER TABLE {table_name} ALTER COLUMN {self._db_adapter.quote_table_name(column_name)} DROP NOT NULL;")

    def drop_column(self, table_name: str, column_name: str):
        """Удалить колонку из таблицы

        :param table_name: название таблицы
        :param column_name: название колонки

        NOTE: not supported in SQLite -> override this method for correct implementation.
        """

        if table_name == "" or column_name == "":
            raise Exception("[BaseMigrator][drop_column] Table name or column name is Empty!")
        if not self._db_adapter:
            raise Exception("[BaseMigrator][drop_column] Database adapter is None!")
        table_name = self._db_adapter.quote_table_name(table_name)
        self._exec_query_or_export(f"ALTER TABLE {table_name} DROP COLUMN {self._db_adapter.quote_table_name(column_name)};")

    def add_index(self, table_name: str, columns: list, props: dict = {}):
        """Добавить индекс для таблицы

        :param table_name: название таблицы
        :param columns: названия колонок
        :param props: свойства

        Supported Props:
          - [string] name    - имя индекса (необязательное)
          - [bool]   unique  - является ли уникальным
        """

        if table_name == "" or len(columns) == 0:
            raise Exception("[BaseMigrator][add_index] Table name or columns is Empty!")
        props['table'] = table_name
        props['columns'] = columns
        self._add_index_protected(props)

    def rename_index(self, table_name: str, old_name: str, new_name: str):
        """Переименовать индекс для таблицы

        :param table_name: название таблицы
        :param old_name: старое название
        :param new_name: новое название
        """

        if table_name == "" or old_name == "" or new_name == "":
            raise Exception("[BaseMigrator][rename_index] Table name or old name or new name is Empty!")
        if not self._db_adapter:
            raise Exception("[BaseMigrator][rename_index] Database adapter is None!")
        if old_name == new_name:
            raise Exception("[BaseMigrator][rename_index] Old name is the same as new name!")
        tmp_old_name = self._db_adapter.quote_table_name(old_name)
        tmp_new_name = self._db_adapter.quote_table_name(new_name)
        self._exec_query_or_export(f"ALTER INDEX {tmp_old_name} RENAME TO {tmp_new_name};")

    def drop_index(self, table_name: str, props: dict = {}):
        """Удалить индекс таблицы

        :param table_name: название таблицы
        :param props: свойства

        Supported Props:
          - [array] columns  - имена колонок
          - [string] name    - имя индекса
          - [bool] if_exists - добавить флаг 'IF EXISTS' (может не поддерживаться) (default: False)
          - [bool] cascade   - добавить флаг 'CASCADE' (может не поддерживаться) (default: False)

        NOTE: Должен быть задан хотябы один!
        NOTE: Приоритет отдается name!
        """

        if table_name == "":
            raise Exception("[BaseMigrator][drop_index] Table name is Empty!")
        props['table'] = table_name
        self._drop_index_protected(props)

    def set_primary_key(self, table_name: str, column_name: str):
        """Установить новый первичный ключ таблицы

        :param table_name: название таблицы
        :param column_name: название колонки
        """

        if table_name == "" or column_name == "":
            raise Exception("[BaseMigrator][set_primary_key] Table name or column name is Empty!")
        if not self._db_adapter:
            raise Exception("[BaseMigrator][set_primary_key] Database adapter is None!")
        # drop old primary keys
        tmp_p_keys = self.table_primary_keys(table_name)
        for info in tmp_p_keys.values():
            self.drop_primary_key(table_name, info['column'])
        # set new primary key
        tmp_table_lst = table_name.split(".")
        tmp_name = self._db_adapter.quote_table_name(f"{tmp_table_lst[len(tmp_table_lst) - 1]}_pkey")
        table_name = self._db_adapter.quote_table_name(table_name)
        self._exec_query_or_export(f"ALTER TABLE {table_name} ADD CONSTRAINT {tmp_name} PRIMARY KEY ({column_name});")

    def drop_primary_key(self, table_name: str, column_name: str):
        """Удалить первичный ключ таблицы

        :param table_name: название таблицы
        :param column_name: название колонки
        """

        if table_name == "" or column_name == "":
            raise Exception("[BaseMigrator][drop_primary_key] Table name or column name is Empty!")
        if not self._db_adapter:
            raise Exception("[BaseMigrator][drop_primary_key] Database adapter is None!")
        tmp_p_key_name = ""
        tmp_p_keys = self.table_primary_keys(table_name)
        for info in tmp_p_keys.values():
            if info['column'] == column_name:
                tmp_p_key_name = info['name']
                break
        if tmp_p_key_name == "":
            raise Exception(f"[BaseMigrator][drop_primary_key] Not found primary key name for table \"{table_name}\"!")
        table_name = self._db_adapter.quote_table_name(table_name)
        self._exec_query_or_export(f"ALTER TABLE {table_name} DROP CONSTRAINT {self._db_adapter.quote_table_name(tmp_p_key_name)};")

    def add_foreign_key(self,
                        table_name: str, columns: list,
                        ref_table_name: str, ref_columns: list,
                        props: dict = {}):
        """Добавить вторичный ключ для таблицы

        :param table_name: название таблицы
        :param columns: названия колонок
        :param ref_table_name: название таблицы на котороу ссылаемся
        :param ref_columns: названия колонок на которые ссылаемся
        :param props: свойства

        Supported Props:
          - [bool] on_update - добавить флаг 'ON UPDATE' (может не поддерживаться)
          - [bool] on_delete - добавить флаг 'ON DELETE' (может не поддерживаться)
          - [string] action  - добавить флаг поведения 'NO ACTION / CASCADE / RESTRICT / SET DEFAULT / SET NULL' (может не поддерживаться)
          - [string] name    - задать имя вторичного ключа
        """

        if table_name == "" or len(columns) == 0:
            raise Exception("[BaseMigrator][add_foreign_key] Table name or columns is Empty!")
        if ref_table_name == "" or len(ref_columns) == 0:
            raise Exception("[BaseMigrator][add_foreign_key] Reference table name or reference columns is Empty!")
        if not self._db_adapter:
            raise Exception("[BaseMigrator][add_foreign_key] Database adapter is None!")
        columns = list(set(columns))  # get uniq list
        columns = list(filter(len, columns))  # remove empty
        if len(columns) == 0:
            raise Exception("[BaseMigrator][add_foreign_key] Columns is Empty!")
        ref_columns = list(set(ref_columns))  # get uniq list
        ref_columns = list(filter(len, ref_columns))  # remove empty
        if len(ref_columns) == 0:
            raise Exception("[BaseMigrator][add_foreign_key] Reference columns is Empty!")
        columns_names = str(", ").join(columns)
        columns_names_2 = str("_").join(columns)
        ref_columns_names = str(", ").join(ref_columns)
        tmp_name = f"fk_{table_name}_{columns_names_2}"
        if 'name' in props:
            tmp_name = props['name']  # TODO name to underscore?
        table_name = self._db_adapter.quote_table_name(table_name)
        ref_table_name = self._db_adapter.quote_table_name(ref_table_name)
        sql = f"ALTER TABLE {table_name} ADD CONSTRAINT {self._db_adapter.quote_table_name(tmp_name)} FOREIGN KEY ({columns_names}) REFERENCES {ref_table_name} ({ref_columns_names})"
        add_next = False
        if props.get('on_update', False):
            sql += " ON UPDATE"
            add_next = True
        elif props.get('on_delete', False):
            sql += " ON DELETE"
            add_next = True
        if props.get('action', None) and add_next:
            sql += f" {self.make_reference_action(props['action'])}"
        elif add_next:
            sql += " NO ACTION"
        self._exec_query_or_export(f"{sql};")

    def add_foreign_key_p_key(self,
                              table_name: str, column_name: str,
                              ref_table_name: str,
                              props: dict = {}):
        """Добавить вторичный ключ для таблицы, ссылающийся на первичный ключ другой таблицы

        :param table_name: название таблицы
        :param column_name: название колонки
        :param ref_table_name: название таблицы на котороу ссылаемся
        :param props: свойства

        NOTE: данный метод создает вторичный ключ, который будет ссылаться на первичный ключ таблицы ref_table_name.

        Supported Props:
          - [bool] on_update - добавить флаг 'ON UPDATE' (может не поддерживаться)
          - [bool] on_delete - добавить флаг 'ON DELETE' (может не поддерживаться)
          - [string] action  - добавить флаг поведения 'NO ACTION / CASCADE / RESTRICT / SET DEFAULT / SET NULL' (может не поддерживаться)
          - [string] name    - задать имя вторичного ключа
        """

        ref_p_key_column = ""
        tmp_columns = self.table_columns(ref_table_name)
        for info in tmp_columns.values():
            if info['is_pk']:
                ref_p_key_column = info['column']
                break
        if ref_p_key_column == "":
            raise Exception(f"[BaseMigrator][add_foreign_key_p_key] Not found primary key name for reference table \"{ref_table_name}\"!")
        self.add_foreign_key(table_name, [column_name], ref_table_name, [ref_p_key_column], props)

    def drop_foreign_key(self, table_name: str, columns: list):
        """Удалить вторичный ключ таблицы

        :param table_name: название таблицы
        :param columns: названия колонок
        """

        if table_name == "" or len(columns) == 0:
            raise Exception("[BaseMigrator][drop_foreign_key] Table name or columns is Empty!")
        if not self._db_adapter:
            raise Exception("[BaseMigrator][drop_foreign_key] Database adapter is None!")
        columns = list(set(columns))  # get uniq list
        columns = list(filter(len, columns))  # remove empty
        if len(columns) == 0:
            raise Exception("[BaseMigrator][drop_foreign_key] Columns is Empty!")
        # select f-keys list
        columns_names = str(", ").join(columns)
        tmp_name = ""
        tmp_f_key_dict = self.table_foreign_keys(table_name)
        for fk in tmp_f_key_dict.values():
            if fk['column'] == columns_names:
                tmp_name = fk['name']
                break
        if tmp_name == "":
            raise Exception(f"[BaseMigrator][drop_foreign_key] Not found foreign key for columns \"{columns_names}\"!")
        table_name = self._db_adapter.quote_table_name(table_name)
        self._exec_query_or_export(f"ALTER TABLE {table_name} DROP CONSTRAINT {self._db_adapter.quote_table_name(tmp_name)};")

    def drop_foreign_key_p_key(self, table_name: str, column_name: str):
        """Удалить вторичный ключ таблицы, ссылающийся на первичный ключ другой таблицы

        :param table_name: название таблицы
        :param column_name: название колонки
        :return:
        """

        if table_name == "" or column_name == "":
            raise Exception("[BaseMigrator][drop_foreign_key_p_key] Table name or column name is Empty!")
        if not self._db_adapter:
            raise Exception("[BaseMigrator][drop_foreign_key_p_key] Database adapter is None!")
        self.drop_foreign_key(table_name, [column_name])

    def execute(self, sql: str):
        """Выполнить SQL запрос

        :param sql: SQL запрос
        """

        if sql == "":
            raise Exception("[BaseMigrator][execute] SQL is Empty!")
        if not self._db_adapter:
            raise Exception("[BaseMigrator][execute] Database adapter is None!")
        self._exec_query_or_export(sql)

    #
    # protected methods:
    #

    def _add_index_protected(self, args: dict):
        """Добавить индекс для таблицы

        :param args: аргументы

        Supported Props:
          - [string] table   - имя таблицы
          - [list]   columns - список имен колонок
          - [string] name    - имя индекса (необязательное)
          - [bool]   unique  - является ли уникальным
        """

        if not self._db_adapter:
            raise Exception("[BaseMigrator][_add_index_protected] Database adapter is None!")
        if len(args.keys()) == 0:
            raise Exception("[BaseMigrator][_add_index_protected] Args is Empty!")
        if not 'table' in args:
            raise Exception("[BaseMigrator][_add_index_protected] Not found 'table' in args!")
        if not 'columns' in args:
            raise Exception("[BaseMigrator][_add_index_protected] Not found 'columns' in args!")
        tmp_columns = list(set(args['columns']))  # get uniq list
        tmp_columns = list(filter(len, tmp_columns))  # remove empty
        if tmp_columns and len(tmp_columns) == 0:
            raise Exception("[BaseMigrator][_add_index_protected] Columns is Empty!")
        tmp_columns_names = str(", ").join(tmp_columns)
        tmp_columns_names_2 = str("_").join(tmp_columns)
        table_lst = str(args['table']).split('.')
        tmp_name = f"{table_lst[len(table_lst) - 1]}_{tmp_columns_names_2}_index"
        if 'name' in args:
            tmp_name = args['name']
        is_unique = ''
        if args.get('unique', False):
            is_unique = 'UNIQUE'
        table = self._db_adapter.quote_table_name(args['table'])
        self._exec_query_or_export(f"CREATE {is_unique} INDEX {self._db_adapter.quote_table_name(tmp_name)} ON {table} ({tmp_columns_names});")

    def _drop_index_protected(self, args: dict):
        """Удалить индекс у таблицы

        :param args: аргументы

        Supported Props:
          - [string] table      - имя таблицы
          - [list]   columns    - список имен колонок
          - [string] name       - имя индекса (необязательное)
          - [bool] if_exists - добавить флаг 'IF EXISTS' (может не поддерживаться) (default: False)
          - [bool] cascade   - добавить флаг 'CASCADE' (может не поддерживаться) (default: False)

        NOTE: Должен быть задан хотябы один!
        NOTE: Приоритет отдается name!
        """

        if not self._db_adapter:
            raise Exception("[BaseMigrator][_drop_index_protected] Database adapter is None!")
        if len(args.keys()) == 0:
            raise Exception("[BaseMigrator][_drop_index_protected] Args is Empty!")
        if not 'table' in args:
            raise Exception("[BaseMigrator][_drop_index_protected] Not found 'table' in args!")
        if not 'columns' in args and not 'name' in args:
            raise Exception("[BaseMigrator][_drop_index_protected] Not found 'columns' and 'name' in args!")
        tmp_name = ""
        if 'columns' in args:
            tmp_columns = list(set(args['columns']))  # get uniq list
            tmp_columns = list(filter(len, tmp_columns))  # remove empty
            if tmp_columns and len(tmp_columns) == 0:
                raise Exception("[BaseMigrator][_drop_index_protected] Columns is Empty!")
            tmp_columns_names = str("_").join(tmp_columns)
            table_lst = str(args['table']).split('.')
            tmp_name = f"{table_lst[len(table_lst) - 1]}_{tmp_columns_names}_index"
        if 'name' in args:
            tmp_name = args['name']

        sql = "DROP INDEX"
        if args.get('if_exists', False):
            sql += " IF EXISTS"
        sql += f" {tmp_name}"
        if args.get('cascade', False):
            sql += " CASCADE"
        self._exec_query_or_export(f"{sql};")

    def _prepare_create_table(self, name: str, args: dict) -> str:
        """Подготовить SQL для метода CREATE TABLE

        :param name: название таблицы
        :type name: str
        :param args: аргументы
        :type args: dict
        :rtype: str
        """

        tmp_sql = ""
        tmp_p_key = ""
        tmp_unique = []
        tmp_unique_groups = {}
        if args.get('id', False):
            tmp_p_key = 'id'
            tmp_sql += 'id serial not NULL'
        for k, v in args.items():
            if k == 'id':
                continue
            if tmp_sql != "":
                tmp_sql += ",\n"
            if isinstance(v, dict):
                # column config array
                tmp_res = self._prepare_create_column(k, v)
                tmp_sql += tmp_res.get('sql', '')
                tmp_unique += tmp_res.get('unique', [])
                tmp_unique_groups = self.__merge_two_dicts(tmp_unique_groups, tmp_res.get('unique_groups', {}))
                if tmp_p_key == "":
                    tmp_p_key = tmp_res.get('p_key', '')
            else:
                # use as column type
                tmp_sql += f"{self._db_adapter.quote_table_name(k)} {self.to_database_type(str(v))}"

        if tmp_p_key != "":
            tmp_table_lst = name.split('.')
            tmp_name = f"{tmp_table_lst[len(tmp_table_lst) - 1]}_pkey"
            tmp_sql += f",\nCONSTRAINT {self._db_adapter.quote_table_name(tmp_name)} PRIMARY KEY ({tmp_p_key})"
        if len(tmp_unique) > 0:
            for uniq in tmp_unique:
                if uniq == "":
                    continue
                tmp_sql += f",\nUNIQUE ({uniq})"
        if len(tmp_unique_groups.keys()) > 0:
            for uniq_gr in tmp_unique_groups.values():
                tmp_unique = list(set(uniq_gr))  # get uniq list
                tmp_unique = list(filter(len, tmp_unique))  # remove empty
                if len(tmp_unique) == 0:
                    continue
                separator = ", "
                tmp_sql += f",\nUNIQUE ({separator.join(tmp_unique)})"

        return tmp_sql

    def _prepare_create_column(self, name: str, args: dict) -> dict:
        """Подготовить SQL для создания колонки

        :param name: название колонки
        :type name: str
        :param args: аргументы
        :type args: dict
        :rtype: dict

        Return example:
        {
            'sql': '',
            'p_key': '',
            'unique': [],
            'unique_groups': {
                'a': []
            }
        }
        """

        if not 'type' in args:
            return {}
        p_key = ""
        unique = []
        unique_groups = {}
        tmp_column_conf = self._db_adapter.quote_table_name(name)
        tmp_limit = args.get('limit', None)
        if tmp_limit:
            tmp_limit = int(tmp_limit)
        tmp_type = self.to_database_type(args['type'], tmp_limit)
        tmp_column_conf += f" {tmp_type}"
        if not args.get('null', True):
            tmp_column_conf += " NOT NULL"
        if 'default' in args:
            tmp_column_conf += f" {self.make_default_value(str(args['default']), tmp_type)}"
        if args.get('primary_key', False):
            p_key = name
        if args.get('unique', False):
            unique.append(name)
        elif args.get('unique_group', None):
            tmp_list = []
            if str(args['unique_group']) in unique_groups:
                tmp_list = unique_groups[str(args['unique_group'])]
            tmp_list.append(name)
            unique_groups[str(args['unique_group'])] = tmp_list

        return {
            'sql': tmp_column_conf,
            'p_key': p_key,
            'unique': unique,
            'unique_groups': unique_groups
        }

    def __merge_two_dicts(self, x: dict, y: dict):
        """Объединить два словаря

        :param x: словать 1
        :param y: словарь 2
        """

        z = x.copy()  # start with keys and values of x
        z.update(y)  # modifies z with keys and values of y
        return z

    def __is_export(self) -> bool:
        """Используется ли экспортирование миграции
        """

        if not self._export_file:
            return False
        return True

    def __export(self, sql: str):
        """Сохранить SQL миграции в файл

        :param sql: SQL данные
        """

        if not self.__is_export():
            return
        with open(self._export_file, 'a') as f:
            f.write(Helper.text_left_strip(sql, True))
            f.write("\n")

    def _exec_query_or_export(self, sql: str):
        """Выполнить в БД или сохранить SQL миграцию в файл

        :param sql: SQL данные
        """

        if self.__is_export():
            self.__export(sql)
        else:
            self._db_adapter.query(sql)
