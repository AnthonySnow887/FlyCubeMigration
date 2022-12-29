
#
# Created by FlyCubeMigration generator.
# User: anton
# Date: 16.12.2022
# Time: 17:09
#

from src.Migration.BaseMigration import BaseMigration


class SetPrimaryKey(BaseMigration):
    #
    # NOTE: Uncomment if needed configure migration.
    #
    # def configuration(self):
    #     # Set here your code for configuration migration
    #     return

    def up(self):
        self.set_primary_key('test_schema.test_table_2', 'my_id')

    def down(self):
        self.drop_primary_key('test_schema.test_table_2', 'my_id')

        