import os
import sys
import time
import json
import socketserver
import logging

from http.server import SimpleHTTPRequestHandler
from core.server import Webserver

# This is the main method that will fire off the server. 
if __name__ == '__main__':
    global data
    flag_run = True
    
    conf_path = 'configs.json'
    if(len(sys.argv) > 1):
        conf_path = sys.argv[1]
    
    try:
        with open(conf_path, 'r') as arq:
            data = json.loads(arq.read())

        log_path = data['LOG']['path']

        if(not(os.path.isdir(log_path))):
            os.mkdir(log_path)

        slog = os.path.join(log_path, data['LOG']['name'])

        logging.basicConfig(filename = slog, filemode = data['LOG']['filemode'], \
                            level = logging.INFO,\
                            format = data['LOG']['format'], \
                            datefmt = data['LOG']['dtformat'])
        
        #port = data['SYSTEM']['PORT']
        #t = ThreadedServer(DetectService, port=port)
        #print('svision server online on port: {}'.format(port))
        #logging.info('svision server online on port: {}'.format(port))
        #t.start()
    except Exception as err:
        flag_run = False
        print('Error on load server configs.\nDETAILS: {}'.format(err))


    if(flag_run):
        try:
            thread = Webserver(data)
            thread.start()
            logging.info('Start svision webservice')
        except Exception as err:
            logging.error(err)
        

    
