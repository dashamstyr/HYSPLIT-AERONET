
def control_single(location,start_time,run_hours,height,meteo_files,output_dir):
    #a tool for generating a control file for use with HYSPLIT to make trajectories
    import os,sys
    
    os.chdir('c:/hysplit4/working/')
    if os.path.isfile('CONTROL'):
        os.remove('CONTROL')
    year = str(start_time[0]).zfill(2)
    month = str(start_time[1]).zfill(2)
    day = str(start_time[2]).zfill(2)
    hour = str(start_time[3]).zfill(2)

    time_in = year+' '+month+' '+day+' '+hour
    latlonht = str(location[1])+' '+str(location[2])+' '+str(height)         
    output_path = output_dir+'/'+location[0]+'/'

    if not os.path.isdir(output_path):
        os.makedirs(output_path)
                       
    
    output_file = location[0]+year+month+day+hour+'_'+str(height)+'.txt'
    cont_file = open('CONTROL','w')
    cont_file.writelines(time_in+'\n'+'1\n'+latlonht+'\n'+str(run_hours)+'\n'+\
                         '0\n10000\n'+str(len(meteo_files))+'\n')

    for n in meteo_files:
        [meteo_path,meteo_filename] = os.path.split(n)
        cont_file.writelines(meteo_path+'/\n'+meteo_filename+'\n')

    cont_file.writelines(output_path+'\n'+output_file)
    cont_file.close()

##def infile_generator(folder,basename):
##    import os,sys
##
##    os.chdir(folder)
##    if os.path.isfile('INFILE'):
##        os.remove('INFILE')
##
##    c = os.listdir(os.getcwd())
##
##    for f in c:
        


def set_dir(titlestring):
    #simply sets the current working directory to one selected by the useer
    from Tkinter import Tk
    import tkFileDialog
     
     
    master = Tk()
    master.withdraw() #hiding tkinter window
     
    file_path = tkFileDialog.askdirectory(title=titlestring)
     
    if file_path != "":
       return str(file_path)
     
    else:
       print "you didn't open anything!"
     
def get_files(titlestring,filetype = ('.txt','*.txt')):
    #grabs all files in a folder that contain the titlestring input
    from Tkinter import Tk
    import tkFileDialog
     
     
    master = Tk()
    master.withdraw() #hiding tkinter window

    file_path = []
     
    file_path = tkFileDialog.askopenfilename(title=titlestring, filetypes=[filetype,("All files",".*")],multiple='True')
     
    if file_path != "":
       return str(file_path)
     
    else:
       print "you didn't open anything!"
       
def aeronet_import(filename):
    # import aeronet data file into a list of dictionaries
    # filename must include full path to file
    
    import csv

    filetoread = open(filename,'r')
    header = []
    headerlines = 3
    for n in range(0,headerlines):
        header.append(next(filetoread))

    tempdict = csv.DictReader(filetoread)

    aerodict = []
    for row in tempdict:
        aerodict.append(row)

    filetoread.close()

    return header,aerodict

def hysplit_import(filename):
    # import hysplit data file into a list
    # filename must include full path to file
    
    import csv
    import numpy as np

    filetoread = open(filename,'rb')
    h = next(filetoread)
    header = []
    headmarker = '1 PRESSURE'
    while headmarker not in h:
        header.append([h])
        h = next(filetoread)
        
    temp = csv.reader(filetoread,delimiter = ' ',skipinitialspace = 'True')

    hysplitdata = np.array([])
    for row in temp:
        hysplitdata = np.append(hysplitdata,row)
    hysplitdata = np.reshape(hysplitdata,(-1,13))
    hysplitdata = hysplitdata.astype('float16')

    filetoread.close()  
    
    return header,hysplitdata

def aeronet_extract(aerofile,filterkeys):
    #import data dictionary and filter for desired keys
    #output goes into matlab file (filename.mat) in selected output folder
    #with each key pointing to a list of values date time and data type (1.5 or 2.0) are included
    #filterkeys is a list of variables to extract from the Aeronet file
    
    import os,sys
    import datetime as dt 
    
    [header,aerodict] = aeronet_import(aerofile)
    
    datelist = []
    datatypelist = []
    output_dict = dict()
    for line in aerodict:
        tempdate = line['Date(dd-mm-yyyy)'].split(':')
        temptime = line['Time(hh:mm:ss)'].split(':')
        year = int(tempdate[2])
        month = int(tempdate[1])
        day = int(tempdate[0])
        hour = int(temptime[0])

        tempdatatype = line['DATA_TYPE']

        date = dt.datetime(year,month,day,hour)
        datelist.append(date)
        datatypelist.append(tempdatatype)

    output_dict['Date'] = datelist
    output_dict['Data Type'] = datatypelist

    for key in filterkeys:
        temp = []
        for line in aerodict:
            temp.append(float(line[key]))
            

        output_dict[key] = temp

    return output_dict
                    
def aeronet_dayfilter(aeronet_path,aerofilt_dir,hysplit_path):
    #takes in a full path to an aeronet file, then extracts the days for whcih
    #data were collected and filters a folder full of hysplit files to
    #include only days for which aeronet data exist and dumps filtered list into
    #a new directory in "aerofilt_dir" directory with the same folder
    #name as the one containing original hysplit files
    
    import os,sys
    import shutil

    print 'Performing Aeronet Dayfilter ...'

    startdir = os.getcwd()
    
    [aeronet_dir,aeronet_file] = os.path.split(aeronet_path)

    os.chdir(aeronet_dir)

    [aeronet_header,aerodict] = aeronet_import(aeronet_file)

    [hysplit_dir,hysplit_folder] = os.path.split(hysplit_path)
    
    aerodir = aerofilt_dir+'/'+hysplit_folder
    
    try:
        os.mkdir(aerodir)
    except OSError:
        pass
    
    
    datestring = []
    for line in aerodict:
        tempdate = line['Date(dd-mm-yyyy)'].split(':')
        year = tempdate[2][-2:]
        month = tempdate[1]
        day = tempdate[0]
        temp_datestring = year+month+day

        if temp_datestring not in datestring:
            datestring.append(temp_datestring)
    
    os.chdir(hysplit_path)
    hysplit_files = os.listdir('.')
    numdays = len(hysplit_files)
    n = 0
    for f in hysplit_files:
        for s in datestring:
            if s in f:
                n += 1
                #print f, n
                if not os.path.isfile(aerodir+'\\'+f):
                    shutil.copy2(f,aerodir)

    print  '%i out of %i total files used' %(n, numdays)
    os.chdir(startdir)
    
    return aerodir

def haversine(lat1,long1,lat2,long2):
    #function to compute distance and bearing between
    #two latitude/longitude coordinates
    #output distance is in km, bearing is in degrees
    
    from math import *
    
    R = 6371 #radius of Earth in km
    dlat = radians(lat2-lat1)
    dlong = radians(long2-long1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    a = sin(dlat/2)**2 + sin(dlong/2)**2 * cos(lat1) * cos(lat2)
    b = 2*atan2(sqrt(a),sqrt(1-a))

    d = R*b

    y = sin(dlong)*cos(lat2)
    x = cos(lat1)*sin(lat2) - sin(lat1)*cos(lat2)*cos(dlong)

    theta = degrees(atan2(y,x))

    return d,theta

def ellipserad(a,b,theta1,theta2):
    #function to output distance from center to edge of a tilted ellipse
    #a = major axis
    #b = minor axis
    #theta1 = heading between center and point in Earth-centerd coordinates (0 deg = N)
    #theta2 = angle between major axis and N-S axis
    
    
    from math import *

    dtheta = theta2-theta1

    x = b*cos(radians(dtheta))
    y = a*sin(radians(dtheta))

    r = a*b/sqrt(x**2 + y**2)

    return r

def matfile_test(filename,filelist):
    #check if a file is a .mat file
    nametest1 = filename.split('.')

    if nametest1[-1] == 'txt':

        for htest in filelist:

            nametest2 = htest.split('.')

            if  nametest2[0] == nametest1[0] and nametest2[-1] == 'mat':
                return False
        return True
    else:
        return False

def pickle_test(filename,filelist):
    #check if a file is a .pickle file
    nametest1 = filename.split('.')

    if nametest1[-1] == 'txt':

        for htest in filelist:

            nametest2 = htest.split('.')

            if  nametest2[0] == nametest1[0] and nametest2[-1] == 'pickle':
                return False
        return True
    else:
        return False

def hysplit_matfile_generator(aerofilt_dir):
    #tool for extracting data from hysplit trajectory files and putting it into
    #mat files for storage in float16 format
    import numpy as np
    import scipy.io
    import os,sys

    data_cats = ('year','month','day','hour','delta_t','lat','lon','alt','press')


    startdir = os.getcwd()

    os.chdir(aerofilt_dir)

    hysplit_files = os.listdir(os.getcwd())

    print 'Generating Hysplit .mat files ...'
                    
    for h in hysplit_files:

        if matfile_test(h,hysplit_files):

            #import hysplit text file
            [head,data] = hysplit_import(h)

            #create dictionary with {varname: array} based on column names

            output_data = [data[:,2],data[:,3],data[:,4],data[:,5],data[:,8],\
                           data[:,9],data[:,10],data[:,11],data[:,12]]

            output_dict = dict(zip(data_cats,output_data))

            #use scipy.savemat to save it as a .mat file

            savename = h.split('.')[0]

            scipy.io.savemat(savename,output_dict)

    os.chdir(startdir)
    print '... Done'

def hysplit_pandas_generator(aerofilt_dir):
    #tool for extracting data from hysplit trajectory files and putting it into
    #a pandas dataframe for storage in float16 format
    import pandas as pan
    import os,sys

    data_cats = ('delta_t','lat','lon','alt','press')


    startdir = os.getcwd()

    os.chdir(aerofilt_dir)

    hysplit_files = os.listdir(os.getcwd())

    print 'Generating Hysplit dataframe ...'
                    
    for h in hysplit_files:

        if pickle_test(h,hysplit_files):

            #import hysplit text file
            [head,data] = hysplit_import(h)

            #create dictionary with {varname: array} based on column names

            output_data = [data[:,8],data[:,9],data[:,10],data[:,11],data[:,12]]

            output_dict = dict(zip(data_cats,output_data))

            #create datetime index

            dates = []

            for n in range(0,len(data[:,2])):
                yr = data[n,2]
                mn = data[n,3]
                dy = data[n,4]
                hr = data[n,5]
                dates.append(pan.datetime(yr,mn,dy,hr))

            ind = pan.DatetimeIndex(dates)

            df_out = pan.DataFrame(output_dict, index = ind)

            #save it as a .pickle file

            savename = h.split('.')[0]

            pan.save(df_out,savename+'.pickle')

    os.chdir(startdir)
    print '... Done'

def aeronet_matfile_generator(aerofile,aerofilt_dir):
    #tool for extracting values of interest from aeronet data file, putting it into a
    #dictionary and saving i as a .mat file
    import os, sys
    import scipy.io
    import numpy as np

    startdir = os.getcwd()

    print 'Generating Aeronet .mat file ...'

    output_path = aerofilt_dir

    output_folder = os.path.split(aerofilt_dir)[1]

    numdist_keys = ['0.050000','0.065604','0.086077','0.112939','0.148184','0.194429','0.255105',\
               '0.334716','0.439173','0.576227','0.756052','0.991996','1.301571','1.707757',\
               '2.240702','2.939966','3.857452','5.061260','6.640745','8.713145','11.432287','15.000000']

    keylist = ['Inflection_Point[um]','VolCon-T','EffRad-T','VolMedianRad-T','StdDev-T',\
                        'VolCon-F','EffRad-F','VolMedianRad-F','StdDev-F',\
                        'VolCon-C','EffRad-C','VolMedianRad-C','StdDev-C']

    filename = 'Aerostats_'+output_folder

    newdict = aeronet_extract(aerofile,keylist)

    temp_dist = []
    numdist_diameters = []
    for tempkey in numdist_keys:
        tempdict = aeronet_extract(aerofile,[tempkey])
        temp_dist.append(tempdict[tempkey])
        numdist_diameters.append(float(tempkey))


    newdict['Numdist'] = np.array(temp_dist, dtype='float16')
    newdict['Diameters'] = numdist_diameters

    os.chdir(output_path)
            
    scipy.io.savemat(filename,newdict)

    os.chdir(startdir)

    print '... Done'

def aeronet_pandas_generator(aerofile,aerofilt_dir):
    #tool for extracting values of interest from aeronet data file, putting it into a
    #dictionary and saving it as a pandas dataframe
    import os, sys
    import pandas as pan
    import numpy as np

    startdir = os.getcwd()

    print 'Generating Aeronet dataframe ...'

    output_folder = os.path.split(aerofilt_dir)[1]

    keylist = ['Inflection_Point[um]','VolCon-T','EffRad-T','VolMedianRad-T','StdDev-T',\
                'VolCon-F','EffRad-F','VolMedianRad-F','StdDev-F','VolCon-C','EffRad-C',\
               'VolMedianRad-C','StdDev-C',\
               '0.050000','0.065604','0.086077','0.112939','0.148184','0.194429','0.255105',\
               '0.334716','0.439173','0.576227','0.756052','0.991996','1.301571','1.707757',\
               '2.240702','2.939966','3.857452','5.061260','6.640745','8.713145','11.432287',\
               '15.000000']

    filename = 'Aerostats_'+output_folder+'.pickle'

    newdict = aeronet_extract(aerofile,keylist)

    #convert dates to datetime index
    dates = newdict['Date']
    del(newdict['Date'])
                                     
    df_out = pan.DataFrame(newdict, index = dates)
    
    os.chdir(aerofilt_dir)
            
    pan.save(newdict,filename)

    os.chdir(startdir)

    print '... Done'


if __name__ == '__main__':
    aerodir = set_dir('Select Folder to save output')
    aerofile = get_files('Select file to be converted')

    aeronet_pandas_generator(aerofile[1:-1], aerodir)
