import json

from .base import BaseProcessor

class Reader(BaseProcessor):
    def __init__(self, db, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = db
        self.config = config
        self.table = config.read_table

    def execute(self, row):
        data = { field : row[field] for field in self.config.fields_to_compare }
        value = json.dumps(data)
        return self.db.execute(f"insert into {self.config.queue_table} (ref_id, value) values({row['id']}, '{value}')")