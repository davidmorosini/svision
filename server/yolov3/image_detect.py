import time
from math import floor
from yolo import YOLO, detect_video
from PIL import Image, ImageDraw
import numpy as np
import cv2


def yolo_detect(yolo, model, img):
  
    draw = ImageDraw.Draw(img)
    boxes, shape, class_out, class_name = yolo.get_boxes_detected(img)
    
    im_cv2 = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
    person = 0
    person_class = 0
    qtd_epi, qtd_noepi = 0, 0

    for j, b in enumerate(boxes):
        #arredondando para baixo
        if(class_out[j] == person_class):
            person += 1
            aux = [floor(n) for n in b]
            #cv2.rectangle(im_cv2,(aux[1],aux[0]),(aux[3],aux[2]),(0,255,0),3)
            
            im_aux = im_cv2[aux[0]:aux[2], aux[1]:aux[3]]
            im_aux_ = cv2.resize(im_aux, (75, 75), interpolation = cv2.INTER_AREA)
            
            res = model.predict([[im_aux_]])
            
            if(res[0][0] > 0.5):
                fill_='red'
                qtd_noepi += 1
            else:
                fill_='green'
                qtd_epi += 1
            draw.line(((aux[1], aux[0]), (aux[3], aux[0]), (aux[3], aux[2]), (aux[1], aux[2]), (aux[1], aux[0])), fill=fill_, width=4)
    
    return img, qtd_epi, qtd_noepi 

   
        
