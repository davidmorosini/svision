import os
import rpyc
import json
import logging

import pyscreenshot
import numpy as np
from PIL import Image
import time
import datetime

from multiprocessing import Process, freeze_support

#Configuração necessária para envio de objetos
rpyc.core.protocol.DEFAULT_CONFIG['allow_pickle'] = True

def cls():
    os.system('cls' if os.name=='nt' else 'clear')
    
def string_time():
    now = datetime.datetime.now()
    year = '{:02d}'.format(now.year)
    month = '{:02d}'.format(now.month)
    day = '{:02d}'.format(now.day)
    hour = '{:02d}'.format(now.hour)
    minute = '{:02d}'.format(now.minute)
    second = '{:02d}'.format(now.second)
    str_date = '{}{}{}_{}{}{}'.format(year, month, day, hour, minute, second)
    return str_date

def call_detect(con, save_name='svision_out.png'):
    im = pyscreenshot.grab()    
    rpyc_bundle = con.exposed_detect(im)
    bundle = rpyc.classic.obtain(rpyc_bundle) 
    img, qtd_epi, qtd_noepi, time = bundle[0], bundle[1], bundle[2], bundle[3]
    
    img_save_ = 'Não'
    if(qtd_epi + qtd_noepi > 0):
        img.save(save_name)
        img_save_ = save_name   
    cls()
    time = round(time, 4)
    print('\nStatus:\n* Pessoas Detectadas: {}\n\t- Com EPI: {}\n\t- Sem EPI: {}\n*Tempo de detecção: {} s\n*Imagem salva: {}'.format(qtd_epi + qtd_noepi, qtd_epi, qtd_noepi, time, img_save_))
    
def get_connection(IP, PORT, TRY_NUM, SLEEP):
    con = None
    
    try:
        con = rpyc.connect(IP, PORT, config = rpyc.core.protocol.DEFAULT_CONFIG)
        print('svision conected at {}:{}'.format(IP, PORT))
        print('Initializing remote modules. Wait a few seconds..')
        logging.info('Service conected at {}:{}'.format(IP, PORT))
    except ConnectionRefusedError as ref:
        print('Connection refused.')
        logging.error(ref)
    except Exception as e:
        logging.error(e)
    finally:
        if(con == None):
            print('* Start {} tentatives to connect at {}:{}'.format(TRY_NUM, IP, PORT))
            logging.info('Start {} tentatives to connect at {}:{}'.format(TRY_NUM, IP, PORT))
            for i in range(0, TRY_NUM):
                print('\t-> Tentative [{}/{}]'.format(i+1, TRY_NUM))
                try:
                    con = rpyc.connect(IP, PORT, config = rpyc.core.protocol.DEFAULT_CONFIG)
                    print('* SUCESS: Connection established.')
                    logging.info('SUCESS - Connection established')
                    break
                except Exception as e:
                    if((i + 1) < TRY_NUM):
                        print('\tFAILED: next tentative in {} sec'.format(SLEEP))
                        logging.error(e)
                        logging.info('next tentative in {} sec'.format(SLEEP))
                        time.sleep(SLEEP)
                    else:
                        print('* FAILED: Aborting svision system.')
                        logging.info('FAILED - Aborting svision system.')
    return con

def main():

    flag_config = False
    try:
        with open('configs.json') as js:
            data = json.load(js)

        IP = data['RSERVICE']['HOST']
        PORT = data['RSERVICE']['PORT']

        SLEEP_TIME = data['SYSTEM']['SLEEP_TIME']
        SLEEP_TRY_CON = data['SYSTEM']['SLEEP_TRY_CON']
        out_path = data['SYSTEM']['OUT_PATH']
        try_numb_con = data['SYSTEM']['TRY_NUM_CON']
        recup_num = data['SYSTEM']['TRY_NUM_RECUP'] 
        def_name = data['SYSTEM']['DEFAULT_NAME_OUT'] 
        def_type = data['SYSTEM']['DEFAULT_TYPE_OUT'] 
        cam_name = data['SYSTEM']['CAM_NAME']
        
        log_path = data['LOG']['path']

        if(not(os.path.isdir(log_path))):
            os.mkdir(log_path)

        slog = os.path.join(log_path, data['LOG']['name'])

        logging.basicConfig(filename = slog, filemode = data['LOG']['filemode'], \
                            level = logging.INFO,\
                            format = data['LOG']['format'], \
                            datefmt = data['LOG']['dtformat'])
        flag_config = True

    except Exception as e:
        print('Error to open configs.json file, aborting svision local process.\nDetails: {}'.format(e))
    
    if(flag_config):
        logging.info('svision online.')
        cam_out = os.path.join(out_path, cam_name)
        #Criando diretório de saída baseado no nome da camera atual
        if(not(os.path.isdir(out_path))):
            os.mkdir(out_path)
        if(not(os.path.isdir(cam_out))):
            os.mkdir(cam_out)
        
        print('starting svision system\n')
        con = get_connection(IP, PORT, try_numb_con, SLEEP_TRY_CON)
        flag_run = False
        if(con != None):
            flag_run = True
            
        while(flag_run):
            if(con != None):
                max_recup = recup_num
                
            try:
                while(con != None):
                    save_name_ = os.path.join(cam_out, '{}_{}.{}'.format(def_name, string_time(), def_type))
                    call_detect(con.root, save_name=save_name_)
                    time.sleep(SLEEP_TIME)
            except Exception as exec_err:
                logging.error(exec_err)
                max_recup = max_recup - 1
                con = get_connection(IP, PORT, try_numb_con, SLEEP_TRY_CON)
            
            
            else:
                max_recup = max_recup - 1
                con = get_connection(IP, PORT, try_numb_con, SLEEP_TRY_CON)
            
            if(max_recup == 0):
                flag_run = False
        
        logging.info('svision offline.')
            

if __name__ == '__main__':
    #necessário para execução de chamada remota
    freeze_support()
    p = Process(target=main)
    p.start()
                
        
    
    
    
    
    
    

