import threading, time

from .db import DB
from .processes import Reader, Api, Comparer, Writer

class Processors():
    config = None
    types = [Reader, Api, Comparer, Writer]
    processes = {}
    error = None
    debug = False

    def __init__(self, config, debug=False):
        self.debug = debug
        self.config = config

    def getError(self):
        return self.error

    def start(self):
        if not self.config:
            self.error = "Please set Config"
            return False

        for _type in self.types:
            self.processes[_type] = Processor(process_class=_type, config=self.config, debug=self.debug)

        for k, process in self.processes.items():
            process.start()

        return True

    def stop(self):
        if self.processes:
            for k, process in self.processes.items():
                process.stop()

class Processor():
    name = ""
    stopping = False
    current_type = None
    config = None
    db = None
    debug = False
    limit = 10

    processed = 0
    success = 0
    failed = 0

    def __init__(self, process_class, config, debug=False):
        self.debug = debug
        self.db = DB(host=config.db.host, user=config.db.user, password=config.db.password, name=config.db.name)

        self.process_class = process_class
        self.name = process_class.__name__

        try:
            self.config = getattr(config.processors, self.name.lower(), None)
        except:
            pass

        self.thread = threading.Thread(target=self.process)
        self.thread.setDaemon(True)

    def start(self):
        print(f'STARTING.....{self.name}')
        
        self.thread.start()

    def process(self):
        my_process = self.process_class(db=self.db, config=self.config, debug=self.debug)
        if self.debug and isinstance(my_process, Reader):
            my_process.writeSample()
            
        while not self.stopping:
            if self.db.isConnected():
                if isinstance(my_process, Writer):
                    #writer process
                    rows = my_process.getReady(self.limit)
                    if rows:
                        # # mark as processing
                        for row in rows:
                            my_process.done(row['id'])

                        status = my_process.execute(rows)

                        if not status:
                            my_process.undone(row['id'])
                else:
                    rows = my_process.getPending(self.limit)
                    if rows:
                        # # mark as processing
                        for row in rows:
                            my_process.process(row['id'])

                        for row in rows:
                            if isinstance(my_process, Comparer):
                                result, status = my_process.execute(row)
                                my_process.complete(row['id'], status=status, ready=status, differences=result)
                            else:
                                status = my_process.execute(row)
                                
                                # mark as completed
                                my_process.complete(row['id'], status=status)
                    
                        time.sleep(0.1)
                    else:
                        #print(f"No {self.name} queue to process, sleeping for 1s...")
                        time.sleep(1)
            else:
                #print("{self.name} - DB not connected...")
                time.sleep(10)
                #print("{self.name} - Trying to reconnect...")
                self.db.connect()
            time.sleep(0.1)

    def stop(self):
        print(f'STOPPING.....{self.name}')
        self.stopping = True

        while self.thread.is_alive():
            print(f'waiting for {self.name} thread to finish.....')
            time.sleep(1)

        if self.db:
            self.db.close()