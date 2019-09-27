import sys
import os
import csv
import cv2
import argparse
import json
import time
from math import floor
from yolo import YOLO, detect_video
from PIL import Image

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()

def append_csv(path, lines, delimiter=',', quoting=csv.QUOTE_MINIMAL):
    with open(path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=delimiter, quoting=quoting)   
        writer.writerow(lines) 

def detect_img(yolo, cjson):

    try:
        with open(cjson) as js:
            configs = json.load(js)
    except:
        print('Problems to open configs file!, Aborting.')
    
    data_in = [os.path.join(configs['data-in'], diretorio) for diretorio in os.listdir(configs['data-in'])]

    print('Bouding Box by YOLOv3 - start')

    for data_dir in data_in:
        arqs = []
        try:
            arqs = os.listdir(data_dir)
        except NotADirectoryError:
            pass

        print('\nProcessando diretório [{}] = {} arquivos. '.format(data_dir, len(arqs)))

       
        items = list(range(0, len(arqs)))
        l = len(items)


        printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
        
        subdir = data_dir.split('/')[-1]
        csv_arq_name = subdir + '.csv'
        path_box_out = configs['csv_out'] + csv_arq_name
        path_statistics_out = configs['statistics'] + csv_arq_name
        
        #Index CSV
        append_csv(path_statistics_out, ['path','id','person-prediction','total-prediction','process-time'])
        append_csv(path_box_out, ['path', 'Yi','Yf','Xi','Xf'])

        for i, arq in enumerate(arqs):
            img = Image.open(data_dir + '/' + arq)
            im_cv2 = cv2.imread(data_dir + '/' + arq)

            time_start = time.time()

            boxes, shape, class_out, class_name = yolo.get_boxes_detected(img)

            person = 0
            person_class = 0

            for j, b in enumerate(boxes):
                #arredondando para baixo
                if(class_out[j] == person_class):
                    person += 1
                    aux = [floor(n) for n in b]
                    line = [data_dir + '/' + arq, str(aux[0]), str(aux[2]), str(aux[1]), str(aux[3])]
                    append_csv(path_box_out, line)
                    cv2.rectangle(im_cv2,(aux[1],aux[0]),(aux[3],aux[2]),(0,255,0),3)

            cv2.imwrite('../out/imgs/' + arq, im_cv2)

            
            time_end = time.time()
            metrica = [subdir, str(i), str(person), str(len(boxes)), str(round(time_end - time_start, 4))]
            append_csv(path_statistics_out, metrica)

            printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    yolo.close_session()

FLAGS = None

if __name__ == '__main__':
    # class YOLO defines the default value, so suppress any default here
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    '''
    Command line options
    '''
    parser.add_argument(
        '--model', type=str,
        help='path to model weight file, default ' + YOLO.get_defaults("model_path")
    )

    parser.add_argument(
        '--anchors', type=str,
        help='path to anchor definitions, default ' + YOLO.get_defaults("anchors_path")
    )

    parser.add_argument(
        '--classes', type=str,
        help='path to class definitions, default ' + YOLO.get_defaults("classes_path")
    )

    parser.add_argument(
        '--gpu_num', type=int,
        help='Number of GPU to use, default ' + str(YOLO.get_defaults("gpu_num"))
    )

    parser.add_argument(
        '--image', default=False, action="store_true",
        help='Image detection mode, will ignore all positional arguments'
    )
    '''
    Command line positional arguments -- for video detection mode
    '''
    parser.add_argument(
        "--input", nargs='?', type=str,required=False,default='./path2your_video',
        help = "Video input path"
    )

    parser.add_argument(
        "--output", nargs='?', type=str, default="",
        help = "[Optional] Video output path"
    )

    parser.add_argument(
        "--cjson", type=str,
        help="configs.json input"
    )

    FLAGS = parser.parse_args()
    

    if FLAGS.image:
        """
        Image detection mode, disregard any remaining command line arguments
        """
        print("Image detection mode")
        if "input" in FLAGS:
            print(" Ignoring remaining command line arguments: " + FLAGS.input + "," + FLAGS.output)
        detect_img(YOLO(**vars(FLAGS)), FLAGS.cjson)

    elif "input" in FLAGS:
        detect_video(YOLO(**vars(FLAGS)), FLAGS.input, FLAGS.output)
    else:
        print("Must specify at least video_input_path.  See usage with --help.")
