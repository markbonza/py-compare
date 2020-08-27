
import json, sys
from os import path
from csv import writer

from .base import BaseProcessor

from helpers import generateRandomDict
from settings import BASE_PATH, LOCAL_PATH

class Writer(BaseProcessor):
    processed = 0
    def __init__(self, db, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = db
        self.config = config
        self.table = config.read_table

        self.output_file = path.join(LOCAL_PATH, config.output_file)
        if not config.output_file:
            self.output_file = path.join(LOCAL_PATH, "output.csv")

    def getReady(self, limit = 10):
        if not self.table:
            return False
        return self.db.get(f"select * from {self.table} where processing=0 and completed=1 and ready=1 order by id asc limit {limit}")
    
    def done(self, id):
        if not self.table:
            return False
        return self.db.execute(f"update {self.table} set ready=0, done=1 where id={id}")

    def undone(self, id):
        if not self.table:
            return False
        return self.db.execute(f"update {self.table} set ready=1, done=0 where id={id}")

    # def random(self):
    #     return generateRandomDict(self.config.fields_to_compare)

    def _writeHeader(self, fields):
        with open(self.output_file, 'a+', newline='') as write_obj:
            csv_writer = writer(write_obj)
            header = []
            for field in fields:
                for f in self.config.fields_to_compare:
                    header.append(f"{field.upper()} - {f.upper()}")
                    
                header.append("")
            csv_writer.writerow(header)

    def execute(self, rows):
        fields = ['local_value', 'api_value', 'differences']
        if not path.exists(self.output_file):
            self._writeHeader(fields)

        try:
            with open(self.output_file, 'a+', newline='') as write_obj:
                for row in rows:
                    csv_writer = writer(write_obj)
                    csv_row = []
                    for field in fields:
                        try:
                            csv_row_obj = json.loads(row[field])
                            if field == 'differences':
                                for f in self.config.fields_to_compare:
                                    csv_row.append(csv_row_obj[f] if f in csv_row_obj else "")
                            else:    
                                for k, v in csv_row_obj.items():
                                    csv_row.append(v)
                        except:
                            #no diff
                            for f in self.config.fields_to_compare:
                                csv_row.append("")

                        csv_row.append("")
                    csv_writer.writerow(csv_row)

                    self.processed += 1
                    progress = f"Written : {self.processed} lines\r"
                    print(progress, end='', flush=True)
        except Exception as e:
            #print(e)
            return False

        return True