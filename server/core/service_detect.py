import json
import rpyc
import sys
import os
import time
import logging
import threading

from PIL import Image
from rpyc.utils.server import ThreadedServer

from tensorflow.keras.models import model_from_json
from tensorflow.keras.applications import VGG16
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import SGD

sys.path.append('./core/yolov3/')
sys.path.append('./core/yolov3/model_data/')
sys.path.append('./core/svision/')

from yolo import YOLO
from image_detect import yolo_detect
 


rpyc.core.protocol.DEFAULT_CONFIG['allow_pickle'] = True



status_ = {}


class DetectService(rpyc.Service): 
    global status_
    def on_connect(self, conn):
        self.status = 200
        try:
            self.yolo = YOLO()
            #svision_path = data['SYSTEM']['SVISION_MODEL_PATH']
            svision_path = 'core/svision_model'
            #self.margin = data['SYSTEM']['MARGIN_DETECT']
            self.margin = 10
            #json_file = open(os.path.join(svision_path, data['SYSTEM']['SVISION_MODEL']), 'r')
            #json_file = open(os.path.join(svision_path, 'svision_model.json'), 'r')
            #loaded_model_json = json_file.read()
            #json_file.close()
            self.loaded_model = self.create_model()
            
            # load weights into new model
            #self.loaded_model.load_weights(os.path.join(svision_path, data['SYSTEM']['SVISION_WEIGHTS']))
            self.loaded_model.load_weights(os.path.join(svision_path, 'svision_weights.hdf5'))

            opt = SGD(lr=0.001, momentum=0.9)
            self.loaded_model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])

            status_['client'] = True
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
 
    def create_model(self, num_classes=2, input_shape=(224, 224, 3)):
        vgg_16_base = VGG16(weights=None, include_top=False, input_shape=input_shape)
    
        for l in vgg_16_base.layers:
            l.trainable = False
            
        model_vgg16 = Sequential()
        model_vgg16.add(vgg_16_base)

        model_vgg16.add(Flatten())
        model_vgg16.add(Dense(1024, activation='relu'))
        model_vgg16.add(Dropout(0.5))
        model_vgg16.add(Dense(num_classes, activation='softmax'))

        return model_vgg16
        

    def exposed_detect(self, rpyc_img): # this is an exposed method
        image = rpyc.classic.obtain(rpyc_img)
        inicio = time.time()
        img, qtd_epi, qtd_noepi = yolo_detect(self.yolo, self.loaded_model, image)
        fim = time.time()
        logging.info('AQUII')
        logging.info(status_)
        status_['person'] += qtd_epi + qtd_noepi
        status_['epi'] += qtd_epi
        status_['no_epi'] += qtd_noepi
        return (img, qtd_epi, qtd_noepi, (fim - inicio))
               
    
    def exposed_get_status(self):
        return self.status


class ThreadStartServer(threading.Thread):
    def __init__(self, port, status):
        threading.Thread.__init__(self)
        self.port = port
        self.status = status

    def run(self):
        global status_
        status_ = self.status
        t = ThreadedServer(DetectService, port=self.port)
        logging.info('svision service online on port: {}'.format(self.port))
        t.start()
        return t

def start_webserver(port, status):
    global status_
    status_ = status
    t = ThreadedServer(DetectService, port=port)
    logging.info('svision service online on port: {}'.format(port))
    t.start()
    return t
    
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


    
