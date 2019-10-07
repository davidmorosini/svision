import sys
import threading
import logging
import socketserver

from core.shandler import Shandler

class Webserver(threading.Thread):
    def __init__(self, configs):
        threading.Thread.__init__(self)
        self.configs = configs
        
        self.threads = {
            'bot':[]
        }


    def run(self):
        server_class = socketserver.TCPServer
        HOST, PORT = self.configs['WEBSERVER']['HOST'], self.configs['WEBSERVER']['PORT']
        
        try:
            webservice = server_class((HOST, PORT), Shandler)
            logging.info('svision webserver starts in {}:{}'.format(HOST, PORT))
            print('svision webserver online on {}:{}'.format(HOST, PORT))
            webservice.serve_forever()
        except OSError as oerr:
            logging.error(oerr)
        except KeyboardInterrupt as kerr:
            webservice.server_close()
            logging.info('server closed by user: {}'.format(kerr))
        except Exception as err: 
            webservice.server_close()
            logging.critical(err)
