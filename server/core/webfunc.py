import json
import logging
from core.service_detect import ThreadStartServer, start_webserver

status = {
    "webserver":False,
    "client":False,
    "person":0,
    "epi":0,
    "no_epi":0
}

service = None

def start_service(configs):
    if(status['webserver']):
        try:
            thread = ThreadStartServer(50000, status)
            thread.start()
            #start_webserver(50000, status)
        except Exception as err:
            logging.error(err)
    

def att_status():
    return json.dumps(status)

def toggle_service():
    status["webserver"] = not(status["webserver"])
    start_service(None)
    return att_status()

