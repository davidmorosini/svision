#import rpyc

import sys
import os
import time
sys.path.append('./yolov3/')
sys.path.append('./yolov3/model_data/')
sys.path.append('./svision/')

from PIL import Image

from yolo import YOLO
from image_detect import yolo_detect

from tensorflow.keras.models import model_from_json

#rpyc.core.protocol.DEFAULT_CONFIG['allow_pickle'] = True


class DetectService:#(rpyc.Service):   
    def on_connect(self, conn):
        self.yolo = YOLO()
        
        json_file = open('svision_model/vgg_rmsprop_10ep.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.loaded_model = model_from_json(loaded_model_json)
        # load weights into new model
        self.loaded_model.load_weights("svision_model/vgg_rmsprop_10ep.h5")
        # code that runs when a connection is created
        # (to init the service, if needed)'''
        pass

    def on_disconnect(self, conn):
        self.yolo.close_session()
        # code that runs after the connection has already closed
        # (to finalize the service, if needed)
        pass

    def exposed_detect(self, rpyc_img): # this is an exposed method
        image = rpyc.classic.obtain(rpyc_img)
        inicio = time.time()
        img, person = yolo_detect(self.yolo, self.loaded_model, image)
        fim = time.time()
        return img#, person, (fim - inicio)
               
    
    def exposed_get_status(self):
        return 'ok'

    def teste():
        yolo = YOLO()
        
        json_file = open('svision_model/vgg_rmsprop_10ep.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)
        # load weights into new model
        loaded_model.load_weights("svision_model/vgg_rmsprop_10ep.h5")

        
    
if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(DetectService, port=50001)
    print('remote call online on port: 50001')
    t.start()
