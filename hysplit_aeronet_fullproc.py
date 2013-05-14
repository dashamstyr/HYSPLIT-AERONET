import hysplit_tools as tools
import hysplit_traceback as traceback
import file_process_tools as proc
import numpy as np
import pandas as pan
import os,sys

aerostats = ['Beijing','Bonanza_Creek','Bratts_Lake','Chapais','Dalanzadgad','Egbert',\
             'Fort_McMurray','GSFC','Kelowna_UAS','Mauna_Loa','SACOL','Saturn_Island',\
             'Sioux_Falls','Trinidad_Head','UMBC','Univ_of_Lethbridge','XiangHe',\
             'Yellowknife_Aurora']

hystats = ['BEI','BON','BRA','CHA','DAL','EGB','FMM','GSF','KEL','MAU','SAC','SAT',\
           'SIO','TRI','UMB','UOL','XHE','YKN']

stat_dict = dict(zip(hystats,aerostats))

#STEP #1: Filter original Hysplit files to include only days that have aeronet data

aerofilt_topdir = 'F:\Hysplit\AEROFILT'
aeronet_filedir = 'F:\Aeronet\Aeronet Inversions'
hysplit_dir = 'F:\Hysplit'

startdir = os.getcwd()

for stat in stat_dict.iterkeys():

    print '%s station in process ...' %stat_dict[stat]

    os.chdir(aeronet_filedir)

    inv_files = os.listdir(os.getcwd())

    for i in inv_files:
        if stat_dict[stat] in i:
            aeronet_path = aeronet_filedir+'\\'+i

    os.chdir(aerofilt_topdir)

    hysplit_path = hysplit_dir+'\\'+stat

    aerofilt_dir = tools.aeronet_dayfilter(aeronet_path,aerofilt_topdir,hysplit_path)

    #STEP #2: Convert aeronet file and filtered hysplit files to pandas dataframes

    tools.hysplit_pandas_generator(aerofilt_dir)

    tools.aeronet_pandas_generator(aeronet_path,aerofilt_dir)

    #STEP #3: Generate Hysplit traceback file
     
    traceback.traceback(aerofilt_dir)

os.chdir(startdir)

