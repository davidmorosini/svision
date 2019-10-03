import json
import rpyc
import sys
import os
import time
import logging

from PIL import Image
from rpyc.utils.server import ThreadedServer
from tensorflow.keras.models import model_from_json

sys.path.append('./yolov3/')
sys.path.append('./yolov3/model_data/')
sys.path.append('./svision/')

from yolo import YOLO
from image_detect import yolo_detect


rpyc.core.protocol.DEFAULT_CONFIG['allow_pickle'] = True


class DetectService(rpyc.Service):  
    def on_connect(self, conn):
        self.status = 200
        try:
            self.yolo = YOLO()
            
            svision_path = data['SYSTEM']['SVISION_MODEL_PATH']

            json_file = open(os.path.join(svision_path, data['SYSTEM']['SVISION_MODEL']), 'r')
            loaded_model_json = json_file.read()
            json_file.close()
            self.loaded_model = model_from_json(loaded_model_json)
            # load weights into new model
            self.loaded_model.load_weights(os.path.join(svision_path, data['SYSTEM']['SVISION_WEIGHTS']))
        except Exception as err:
            logging.critical(err)
        

    def on_disconnect(self, conn):
        try:
            if(self.status == 200):
                self.yolo.close_session()
                logging.info('close yolo session and finalize svision server process.')
        except Exception as err:
            logging.info(err)
        self.status = 400
        

    def exposed_detect(self, rpyc_img): # this is an exposed method
        image = rpyc.classic.obtain(rpyc_img)
        inicio = time.time()
        img, qtd_epi, qtd_noepi = yolo_detect(self.yolo, self.loaded_model, image)
        fim = time.time()
        return (img, qtd_epi, qtd_noepi, (fim - inicio))
               
    
    def exposed_get_status(self):
        return self.status
    
if __name__ == "__main__":
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
        
        port = data['SYSTEM']['PORT']
        t = ThreadedServer(DetectService, port=port)
        print('svision server online on port: {}'.format(port))
        logging.info('svision server online on port: {}'.format(port))
        t.start()
    except Exception as err:
        print('Error on load server configs.\nDETAILS: {}'.format(err))


    
