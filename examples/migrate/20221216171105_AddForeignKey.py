
#
# Created by FlyCubeMigration generator.
# User: anton
# Date: 16.12.2022
# Time: 17:11
#

from src.Migration.BaseMigration import BaseMigration


class AddForeignKey(BaseMigration):
    #
    # NOTE: Uncomment if needed configure migration.
    #
    # def configuration(self):
    #     # Set here your code for configuration migration
    #     return

    def up(self):
        self.add_foreign_key('test_schema.test_table_2', ['my_id_2'],
                             'test_schema.test_table_renamed', ['my_id'],
                             {'on_delete': True, 'action': 'CASCADE'})

    def down(self):
        self.drop_foreign_key('test_schema.test_table_2', ['my_id_2'])

        