
#
# Created by FlyCubeMigration generator.
# User: anton
# Date: 16.12.2022
# Time: 16:59
#

from src.Migration.BaseMigration import BaseMigration


class AddIndex(BaseMigration):
    #
    # NOTE: Uncomment if needed configure migration.
    #
    # def configuration(self):
    #     # Set here your code for configuration migration
    #     return

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

        