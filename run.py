#!./env/bin/python

import sys, os, time, threading, argparse

#helpers
from helpers import get_config

#classes
from classes import Processors
from settings import BASE_PATH, CONFIG_FILE

#initiate parser
parser = argparse.ArgumentParser()
parser.add_argument("--debug", "-d", help="set debugger", action='store_true')

args = parser.parse_args()

DEBUG = True if args.debug else False

processes = None

def exit_gracefully():
    if processes:
        processes.stop()
    exit(0)


if __name__ == '__main__':

    config = None
    try:
        print(CONFIG_FILE)
        config = get_config(CONFIG_FILE)
    except:
        print("Could not get config file")
        exit(1)

    if not config:
        print("Config not valid")
        exit(1)

    try: 
        processes = Processors(config=config, debug=DEBUG)
        started = processes.start()
        if not started:
            print(processes.getError())
            exit(1)

        while True:
            time.sleep(1)
            #print(".")
            
    except KeyboardInterrupt:
        # error_log("exiting..using keyboard")
        exit_gracefully()
    except SystemExit as se:
        # error_log(f"system existing..{se}")
        exit_gracefully()
    # except Exception as e:
    #     print(f"{e}")
    #     pass
        # error_log(f"Error happen..{e}")