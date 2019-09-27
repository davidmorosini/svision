import os
import rpyc
import json

import pyscreenshot
import numpy as np
from PIL import Image
import time
import datetime

from multiprocessing import Process, freeze_support

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
        print('Service conected at {}:{}'.format(IP, PORT))
        print('Initializing remote modules..')
    except ConnectionRefusedError as ref:
        print('Error to connect at {}:{}'.format(IP, PORT))
        print('Description: {}'.format(ref))
    except:
        print('Unknow Error to connect at {}:{}'.format(IP, PORT))
    finally:
        if(con == None):
            print('\nStart {} tentatives to connect at {}:{}'.format(TRY_NUM, IP, PORT))
            for i in range(0, TRY_NUM):
                print('Try [{}/{}]'.format(i+1, TRY_NUM))
                try:
                    con = rpyc.connect(IP, PORT, config = rpyc.core.protocol.DEFAULT_CONFIG)
                    print('SUCESS: Connection established.')
                    print('Initializing remote modules..')
                    break
                except:
                    if((i + 1) < TRY_NUM):
                        print('FAILED: next try in {} sec'.format(SLEEP))
                        time.sleep(SLEEP)
                    else:
                        print('FAILED: Aborting process execution.')
    return con

def main():

    flag_config = False
    try:
        with open('configs.json') as js:
            data = json.load(js)
            IP = data['IP']
            PORT = data['PORT']
            SLEEP_TIME = data['SLEEP_TIME']
            SLEEP_TRY_CON = data['SLEEP_TRY_CON']
            out_path = data['OUT_PATH']
            try_numb_con = data['TRY_NUM_CON']
            recup_num = data['TRY_NUM_RECUP'] 
            def_name = data['DEFAULT_NAME_OUT'] 
            def_type = data['DEFAULT_TYPE_OUT'] 
            flag_config = True
    except Exception as e:
        print('Error to open configs.json file, aborting process.')
        print(e)
    
    if(flag_config):
        if(not(os.path.isdir(out_path))):
            os.mkdir(out_path)
        

        con = get_connection(IP, PORT, try_numb_con, SLEEP_TRY_CON)
        flag_run = False
        if(con != None):
            flag_run = True
        
        
        while(flag_run):
            if(con != None):
                max_recup = recup_num
                
            try:
                while(con != None):
                    save_name_ = os.path.join(out_path, '{}_{}.{}'.format(def_name, string_time(), def_type))
                    call_detect(con.root, save_name=save_name_)
                    time.sleep(SLEEP_TIME)
            except:
                max_recup = max_recup - 1
                con = get_connection(IP, PORT, try_numb_con, SLEEP_TRY_CON)
            
            
            else:
                max_recup = max_recup - 1
                con = get_connection(IP, PORT, try_numb_con, SLEEP_TRY_CON)
            
            if(max_recup == 0):
                flag_run = False
            

if __name__ == '__main__':
    freeze_support()
    p = Process(target=main)
    p.start()
                
        
    
    
    
    
    
    

