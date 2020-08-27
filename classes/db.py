import mysql.connector
from mysql.connector import Error, ProgrammingError
from helpers import log_write

class DB():
    exist = True
    connection = None
    # cursor = None
    def __init__(self, host, user, password, name):
        self.host = host
        self.user = user
        self.password = password
        self.name = name

        self.connect()

    def isConnected(self):
        if self.connection and self.exist:
            return self.connection.is_connected()
        
        return False

    def isExist(self):
        return self.exist

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.name
            )
            
            self.connection.autocommit = True
            # self.cursor = self.connection.cursor(dictionary=True)
        except ProgrammingError as p:
            self.exist = False
            log_write(f"ProgrammingError in MySQL: {p}", level="ERROR")
        except Error as error:
            log_write(f"Failed to connect in MySQL: {error}", level="ERROR")
        except Exception as e:
            log_write(f"Exception : {e}", level="ERROR")
        finally:
            pass
            #self.close()

    def close(self):
        if self.isConnected():
            if self.connection:
                self.connection.close()

            log_write("MySQL connection is closed")

    def cursor(self):        
        return self.connection.cursor(dictionary=True)

    def closeCursor(self, cursor):
        if cursor:
            cursor.close()

    def execute(self, query, values=None, auto_commit = True, cursor = None):
        success = True
        if self.isConnected():
            if not cursor:
                cursor = self.cursor()
            try:
                cursor.execute(query, values)
            except Error as error:
                log_write(f"Failed to execute query - {query}, Error : {error}", level="ERROR")
                success = False
            except Exception as e:
                log_write(f"Failed to execute query - {query}, {e}", level="ERROR")
                success = False
            finally:
                if auto_commit:
                    #self.connection.commit()
                    self.closeCursor(cursor)
                # self.close()
                return success

        return False

    def get(self, query):
        cursor = self.cursor()
        self.execute(query, cursor = cursor, auto_commit=False)
        results = cursor.fetchall()
        self.closeCursor(cursor)
        return results
    