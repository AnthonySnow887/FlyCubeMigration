
#
# Created by FlyCubeMigration generator.
# User: anton
# Date: 16.12.2022
# Time: 16:37
#

from src.Migration.BaseMigration import BaseMigration


class ChangeColumn(BaseMigration):
    #
    # NOTE: Uncomment if needed configure migration.
    #
    # def configuration(self):
    #     # Set here your code for configuration migration
    #     return

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

        