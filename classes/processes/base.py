class BaseProcessor():
    db = None
    config = None
    table = None
    debug = False
    
    def __init__(self, *args, **kwargs):
        self.debug = kwargs.get('debug', False)

    def writeSample(self):
        arr_values = []
        for i in range(1000):
            values = [ f"'{str(i) * 4}'"  for field in self.config.fields_to_compare]
            values = ", ".join(values)
            arr_values.append(f"({values})")
        res = self.db.execute(f"insert into {self.config.read_table} ({', '.join(self.config.fields_to_compare)}) values {', '.join(arr_values)}")
        #print(res)
        #print(f"insert into {self.config.read_table} ({', '.join(self.config.fields_to_compare)}) values {', '.join(arr_values)}")

    def reset(self):
        if not self.table:
            return False
        return self.db.execute(f"update {self.table} set processing=0, completed=0, status=0 where id>0")

    def process(self, id):
        if not self.table:
            return False
        return self.db.execute(f"update {self.table} set processing=1 where id={id}")

    def complete(self, id, status=True, **kwargs):
        if not self.table:
            return False
        
        extra_data = []
        for key, value in kwargs.items():
            if isinstance(value, bool):
                extra_data.append(f"{key}={value}")
            else:
                extra_data.append(f"{key}='{value}'")

        extra_qry = ''
        if extra_data:
            extra_qry = f' , { ",".join(extra_data) }'

        return self.db.execute(f"update {self.table} set processing=0, completed=1, status={1 if status else 0}{extra_qry}, completed_timestamp=NOW() where id={id}")

    def getPending(self, limit = 10, count_only = False):
        if not self.table:
            return False
        
        if count_only:
            res = self.db.get(f"select count(*) as COUNT from {self.table} where processing=0 and completed=0")
            return res['COUNT']
        return self.db.get(f"select * from {self.table} where processing=0 and completed=0 order by id asc limit {limit}")
    
    def getFailed(self, limit = 10):
        if not self.table:
            return False
        return self.db.get(f"select * from {self.table} where processing=0 and completed=1 and status=0 order by id asc limit {limit}")

    def delete(self, uid):
        self.db.execute(f"delete from {self.table} where uid={uid}")
        self.db.execute(f"delete from pc_cdr where linkedid={uid} or uniqueid={uid}")
        return True