
#
# Created by FlyCubeMigration generator.
# User: anton
# Date: 16.12.2022
# Time: 16:33
#

from src.Migration.BaseMigration import BaseMigration


class AddColumn(BaseMigration):
    #
    # NOTE: Uncomment if needed configure migration.
    #
    # def configuration(self):
    #     # Set here your code for configuration migration
    #     return

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

        