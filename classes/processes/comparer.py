import json

from .base import BaseProcessor

class Comparer(BaseProcessor):
    def __init__(self, db, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = db
        self.config = config
        self.table = config.read_table

    def execute(self, row):
        result = ''
        try:
            local_value = json.loads(row['local_value'])
            api_value = json.loads(row['api_value'])

            differences = local_value.items() ^ api_value.items()
            if len(differences) > 0:
                keys = []
                for diff in differences:
                    keys.append(diff[0])

                difference = { x : api_value[x] for x in keys }

                result = json.dumps(difference)

            return result, True
        except Exception as e:
            print(e)

        return result, False