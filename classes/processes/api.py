
import json

from .base import BaseProcessor

import random
from helpers import generateRandomLetters

class Api(BaseProcessor):
    def __init__(self, db, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = db
        self.config = config
        self.table = config.read_table

    def random(self, original):
        original = json.loads(original)
        to_change = random.choice([True, False])
        if(to_change):
            random_key = random.choice(list(original))
            original[random_key] = f"{original[random_key]}{generateRandomLetters()}"

        return original
        #return generateRandomDict(self.config.fields_to_compare)

    def execute(self, row):
        value = json.dumps(self.random(row['value']))
        return self.db.execute(f"insert into {self.config.queue_table} (ref_id, local_value, api_value) values({row['ref_id']}, '{row['value']}', '{value}')")