import time
from math import floor
from yolo import YOLO, detect_video
from PIL import Image, ImageDraw
import numpy as np
import cv2

import logging

def yolo_detect(yolo, model, img, margin=0, classes=['epi', 'no-epi']):
    
    draw = ImageDraw.Draw(img)
    boxes, shape, class_out, class_name = yolo.get_boxes_detected(img)
    
    im_cv2 = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
    person = 0
    person_class = 0
    #epi | no-epi
    colors = ['green', 'red']
    qtds = [0, 0]
    for j, b in enumerate(boxes):
        #arredondando para baixo
        if(class_out[j] == person_class):
            person += 1
            aux = [floor(n) for n in b]
            #cv2.rectangle(im_cv2,(aux[1],aux[0]),(aux[3],aux[2]),(0,255,0),3)
            
            xi_ = ((aux[0] - margin) if (aux[0] - margin) >= 0 else 0)
            yi_ = ((aux[2] - margin) if (aux[2] - margin) >= 0 else 0)
            xf_ = ((aux[1] + margin) if (aux[1] + margin) < im_cv2.shape[0] else im_cv2.shape[0])
            yf_ = ((aux[3] + margin) if (aux[3] + margin) < im_cv2.shape[1] else im_cv2.shape[1])

            #im_aux = im_cv2[aux[0]:aux[2], aux[1]:aux[3]]
            im_aux = im_cv2[xi_:yi_, xf_:yf_]

            #cv2.imwrite(str(j) + '.jpg', im_aux)

            im_aux_ = cv2.resize(im_aux, (224, 224), interpolation = cv2.INTER_AREA)

            im_aux_ = np.reshape(im_aux_, [1, 224, 224, 3])
            res = model.predict(im_aux_)[0]
            index = np.argmax(res)
            
            fill_ = colors[index]
            qtds[index] += 1
            
            draw.line(((aux[1], aux[0]), (aux[3], aux[0]), (aux[3], aux[2]), (aux[1], aux[2]), (aux[1], aux[0])), fill=fill_, width=4)
                
                #EPI     NO-EPI
    return img, qtds[0], qtds[1]

   
        
