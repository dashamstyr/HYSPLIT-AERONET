def traceproc(aerofilt_dir):
    import hysplit_tools as tools
    import os, sys
    import numpy as np
    import pandas as pan

    startdir = os.getcwd()

    topdir = aerofilt_dir

    os.chdir(topdir)

    data_files = os.listdir(os.getcwd())

    d_mean = []
    d_std = []
    t_mean = []
    t_std = []
    endpos_mean = []
    endpos_std = []
    start_time = []
    station = []

    #run through all location folders
    for f in data_files:
        if os.path.isdir(f):
            os.chdir(f)
            tracefile = f+'traceback'
            #open traceback file
            trace_df = pan.load(tracefile)

            #create a separate dict of lists for each day and put those into a
            #list called dictlist

            dates = trace_df.index()
            keys = trace_df.columns()

            by = lambda x: lambda y: getattr(y,x)

            trace_mean = trace_df.groupby([by('month'),by('day')]).mean()
            trace_std = trace_df.groupby([by('month'),by('day')]).std()
            
       
    pan.save(df_out,'Hyproc.pickle')

    os.chdir(startdir)

    
def aeroproc(aerofilt_dir):
    import hysplit_tools as tools
    import os, sys
    import scipy.io
    import numpy as np
    import pandas as pan

    startdir = os.getcwd()

    topdir = aerofilt_dir

    os.chdir(topdir)

    data_files = os.listdir(os.getcwd())

    total_mean = []
    total_std = []
    fine_mean = []
    fine_std = []
    coarse_mean = []
    coarse_std = []
    inpoint = []
    numdist_mean = []
    numdist_std = []
    station = []
    date = []
    diameters = []

    #run through all location folders
    for f in data_files:
        if os.path.isdir(f):
            os.chdir(f)
            aerofile = 'Aerostats_'+f
            #open traceback file
            aerodict = scipy.io.loadmat(aerofile)

            #create a separate dict of lists for each day and put those into a
            #list called dictlist

            dates = aerodict['Date']

            
            keys = aerodict.keys()

            oldday = dates[0][-2]

            tempdict = dict()
            dictlist = []

            #ignore these keys that come attached to the dictionary from loadmat
            rejectlist = ['__globals__','__header__','__version__']

            for k,v in aerodict.iteritems():
                if k == 'Diameters':
                    tempdict[k] = []
                    tempdict[k].append(v)
                elif k == 'Numdist':
                    tempdict[k] = []
                    tempdict[k].append(v[:,0])
                elif k not in rejectlist:
                    tempdict[k] = []
                    tempdict[k].append(v[0])  

            for n in range(1,len(dates)):   
                newday = dates[n][-2]
                if newday == oldday:
                    for k,v in aerodict.iteritems():
                        if k == 'Diameters':
                            tempdict[k].append(v)
                        elif k == 'Numdist':
                            tempdict[k].append(v[:,n])
                        elif k not in rejectlist:
                            tempdict[k].append(v[n])
                    oldday = newday
                else:
                    dictlist.append(tempdict)
                    tempdict = dict()
                    for k,v in aerodict.iteritems():
                        if k == 'Diameters':
                            tempdict[k] = []
                            tempdict[k].append(v)
                        elif k == 'Numdist':
                            tempdict[k] = []
                            tempdict[k].append(v[:,n])
                        elif k not in rejectlist:
                            tempdict[k] = []
                            tempdict[k].append(v[n])            
                    oldday = newday

            dictlist.append(tempdict)        
            #generate mean daily values for each element of the dictionaires
            
            for line in dictlist:
                total_mean.append([np.mean(line['EffRad-T']),np.mean(line['VolMedianRad-T']),\
                               np.mean(line['VolCon-T']),np.mean(line['StdDev-T'])])
                total_std.append([np.std(line['EffRad-T']),np.std(line['VolMedianRad-T']),
                               np.std(line['VolCon-T']),np.std(line['StdDev-T'])])
                
                fine_mean.append([np.mean(line['EffRad-F']),np.mean(line['VolMedianRad-F']),
                               np.mean(line['VolCon-F']),np.mean(line['StdDev-F'])])
                fine_std.append([np.std(line['EffRad-F']),np.std(line['VolMedianRad-F']),
                               np.std(line['VolCon-F']),np.std(line['StdDev-F'])])

                coarse_mean.append([np.mean(line['EffRad-C']),np.mean(line['VolMedianRad-C']),
                               np.mean(line['VolCon-C']),np.mean(line['StdDev-C'])])
                coarse_std.append([np.std(line['EffRad-C']),np.std(line['VolMedianRad-C']),
                               np.std(line['VolCon-C']),np.std(line['StdDev-C'])])         

                inpoint.append(np.mean(line['Inflection_Point[um]']))

                numdist_mean.append(np.mean(line['Numdist'],axis=0))
                numdist_std.append(np.std(line['Numdist'],axis=0))

                station.append(f)

                date.append(np.mean(line['Date'],axis=0))

                diameters.append(line['Diameters'])
                
            os.chdir('..')

    output_dict = {'numdist_mean':numdist_mean,'numdist_std':numdist_std,\
                   'total_mean':total_mean,'total_std':total_std,'fine_mean':fine_mean,\
                   'fine_std':fine_std,'coarse_mean':coarse_mean,'coarse_std':coarse_std,\
                   'inpoint':inpoint,'diameters':diameters}

    #convert dates to datetime objects: CURRENTLY ONLY WORKS FOR MARCH/APRIL!
    
    ind_date = []
    
    for d in date:
        year = int(d[0])
        month = int(d[1])
        day = int(d[2])
        hour = int(d[3])

        if hour == 24:
            hour = 0
            if month == 3:
                if day == 31:
                    day = 1
                    month += 1
                else:
                    day += 1
            else:
                if day == 30:
                    day - 1
                    month += 1
                else:
                    day += 1
                    
            print 'Date is %i %i %i' %(month, day, hour)

        ind_date.append(pan.datetime(year,month,day,hour))

    #create multi-index tuples 

    ind = [(s,d) for s in station for d in ind_date]

    multi = pan.MultiIndex.from_tuples(ind, names=['Station','Date'])

    df = pan.DataFrame(output_dict, index = multi)

    pan.save(df,'Aeroproc.pickle')
            
    os.chdir(startdir)            
                                
                

def combproc(aerofilt_dir):
    import hysplit_tools as tools
    import os, sys
    import numpy as np
    import pandas as pan

    startdir = os.getcwd()
    
    topdir = aerofilt_dir

    os.chdir(topdir)

    aero_df = pan.load('Aeroproc.pickle')
    hy_df = pan.load('Hyproc.pickle')

    


    hylist = []
    for stat in hystations:
        tempdict = dict()
        for n in range(0,len(hydict['station'])):
            if hydict['station'][n] == stat:
                for key in hydict.keys():
                    if key not in rejectlist:
                        if key == 'start_time':
                            tempval = np.reshape(hydict[key][n],[1,4])
                        elif key == 'station':
                            tempval = [hydict[key][n]]
                        else:
                            tempval = hydict[key][n]

                        try:
                            tempdict[key].append(tempval)
                        except KeyError:
                            tempdict[key] = np.array(tempval)
                        except AttributeError:
                            tempdict[key] = np.vstack((tempdict[key],tempval))
        if len(tempdict['station']) != 1:
            hylist.append(tempdict)

    aerolist = []
    for stat in aerostations:
        tempdict = dict()
        for n in range(0,len(aerodict['station'])):
            if aerodict['station'][n] == stat:
                for key in aerodict.keys():
                    if key not in rejectlist:
                        if key == 'start_time':
                            tempval = [np.reshape(aerodict[key][n],[1,4])]
                        elif key == 'station':
                            tempval = [aerodict[key][n]]
                        else:
                            tempval = aerodict[key][n]
                        
                        try:
                            tempdict[key].append(tempval)
                        except KeyError:
                            tempdict[key] = np.array(tempval)
                        except AttributeError:
                            tempdict[key] = np.vstack((tempdict[key],tempval))
        if len(tempdict['station']) != 1:
            aerolist.append(tempdict)
    #remove dates where hysplit didn't find traces to deserts

    aerolist_mod = []
    for h in hylist:
        hydates = h['start_time'][:,2]
        hystation = h['station'][0]
        for a in aerolist:
            aerostation = a['station'][0]
            if aerostation == hystation:
                tempdict = dict()
                for n in range(0,len(a['station'])):
                    aerodate = a['date'][n,2]
                    if aerodate in hydates:
                        for key in a.keys():
                            try:
                                tempdict[key].append(a[key][n])
                            except KeyError:
                                tempdict[key] = a[key][n]
                            except AttributeError:
                                tempdict[key] = np.vstack((tempdict[key],a[key][n]))
                aerolist_mod.append(tempdict)

    output_dict = {'Hysplit':hylist,'Aeronet':aerolist_mod}

    scipy.io.savemat('Combproc',output_dict)


if __name__ == '__main__':
    import hysplit_tools as tools
    
    aerofilt_topdir = tools.set_dir('Select Top Level Directory')

    print 'Generating Aeronet Processed Data File'
    aeroproc(aerofilt_topdir)
    
    print 'Generating Hysplit Processed Data File'
    traceproc(aerofilt_topdir)

##    print 'Generating Aeronet Combined    Data File'
##    combproc(aerofilt_topdir)
