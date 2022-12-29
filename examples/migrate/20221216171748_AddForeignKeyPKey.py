
#
# Created by FlyCubeMigration generator.
# User: anton
# Date: 16.12.2022
# Time: 17:17
#

from src.Migration.BaseMigration import BaseMigration


class AddForeignKeyPKey(BaseMigration):
    #
    # NOTE: Uncomment if needed configure migration.
    #
    # def configuration(self):
    #     # Set here your code for configuration migration
    #     return

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

        