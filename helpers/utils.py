import json, os, random, string
import mysql.connector
from datetime import date, datetime

import hmac
import hashlib
import re

class BodyDigestSignature(object):
    def __init__(self, secret, header='Sign', algorithm=hashlib.sha512):
        self.secret = secret
        self.header = header
        self.algorithm = algorithm

    def __call__(self, request):
        body = request.body
        if not isinstance(body, bytes):   # Python 3
            body = body.encode('utf-8')  # standard encoding for HTTP
        if not isinstance(self.secret, bytes):   # Python 3
            self.secret = self.secret.encode('utf-8')  # standard encoding for HTTP
        
        signature = hmac.new(
            self.secret, 
            body, 
            digestmod=self.algorithm
        )
        request.headers[self.header] = signature.hexdigest()
        return request



class MySQLCursorCustomDict(mysql.connector.cursor.MySQLCursorDict):

    def _row_to_python(self, rowdata, desc=None):
        """Convert a MySQL text result row to Python types

        Returns a dictionary.
        """
        row = rowdata

        if row:
            return objdict(zip(self.column_names, row))

        return None

def json_serial(obj):
    if isinstance(obj, (datetime, date)): 
        return obj.isoformat() 
    raise TypeError ("Type %s not serializable" % type(obj))

class objdict(dict):
    def __getattr__(self, name):
        if name in self:
            if isinstance(self[name], dict):
                self[name] = objdict(self[name])
                #print(f"Found dict {name}")
                #return objdict(self[name])
            return self[name]
        else:
            print(f"property {name} is {type(self[name])} type")
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        if name in self:
            del self[name]
        if isinstance(value, dict):
            super().__setitem__(name, objdict(value))
            self[name] = objdict(value)
        else:
            
            super().__setitem__(name, value)
            self[name] = value

        

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)

def get_config(file="config.json"):
    # Get our config
    with open(file, encoding='utf-8') as c:
        data = c.read()
        cdata = json.loads(data)
        c.close()
    config = objdict(cdata)
    return config
    

def save_config(config, file="config_test.json", pretty=False):
    with open(file, 'w', encoding='utf-8') as f_out:
        if pretty:
            f_out.write(json.dumps(config, indent='\t'))
        else:
            f_out.write(json.dumps(config))
        f_out.close()

def log_write(line, file='general.log', level="LOG", pretty=False):
    #print(line)
    pass
    # current_Date = datetime.now()
    # formatted_date = current_Date.strftime('%Y-%m-%d %H:%M:%S')
    # data = f"[{formatted_date}] {level}: {line}"
    # with open(os.path.join("logs",file), 'a+', encoding='utf-8') as f_out:
    #     f_out.write(data)
    #     f_out.write("\n")

def log_api(line, file='api.log', level="LOG", pretty=False):
    log_write(line=line, file=file, level=level, pretty=pretty)

def mixmon_log(line, file='mixmon.log', level="LOG", pretty=False):
    log_write(line=line, file=file, level=level, pretty=pretty)

def error_log(line, file='error.log', level="LOG", pretty=False):
    log_write(line=line, file=file, level=level, pretty=pretty)

def generateRandomDict(keys, length=8):
    obj = {}
    for k in keys:
        obj[k] = generateRandomLetters(length)

    return obj

def generateRandomLetters(length = 2):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))