
#
# Created by FlyCubeMigration generator.
# User: anton
# Date: 16.12.2022
# Time: 17:07
#

from src.Migration.BaseMigration import BaseMigration


class DropIndex(BaseMigration):
    #
    # NOTE: Uncomment if needed configure migration.
    #
    # def configuration(self):
    #     # Set here your code for configuration migration
    #     return

    def up(self):
        self.drop_index('test_schema.test_table_2', {'name': 'my_test_index_renamed'})
        self.drop_index('test_schema.test_table_2', {'columns': ['my_id_2']})

    def down(self):
        self.add_index('test_schema.test_table_2', ['my_id'], {'name': 'my_test_index_renamed', 'unique': True})
        self.add_index('test_schema.test_table_2', ['my_id_2'])

        