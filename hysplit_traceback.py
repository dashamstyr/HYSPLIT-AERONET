def traceback(aerofilt_dir):
    import hysplit_tools as tools
    import numpy as np
    import pandas as pan
    import os,sys
    import math
    import datetime as dt

    Tman_coord = [39.0,84.0]
    Tman_a = 800 #km semi-major axis
    Tman_b = 300 #km semi-minor axis
    Tman_tilt = 70 #degrees between North and major axis

    Gobi_coord = [43.0,106.0]
    Gobi_a = 1000 #km semi_major axis
    Gobi_b = 500
    Gobi_tilt = 65 #degrees between North and major axis

    G_maxlon = 118
    G_minlon = 95

    G_maxlat = 49
    G_minlat = 37

    T_maxlon = 93
    T_minlon = 75

    T_maxlat = 43
    T_minlat = 35


    #load .mat file

    [aerofilt_topdir, station_id] = os.path.split(aerofilt_dir)
    

    data_keys = ('station','start_loc','start_date','end_loc','delta_t','delta_d','desert_tag')
    startdir = os.getcwd()
    os.chdir(aerofilt_dir)
    output_filename = station_id+'traceback'

    hysplit_files = os.listdir(os.getcwd())

    data_index = []
    start_date = []
    start_loc = []
    end_loc = []
    delta_t = []
    station = []
    delta_d = []
    desert_tag = []
    files = 0
    tracks = 0
    G = 0
    T = 0

    print 'Traceback is Processing %s folder' %station_id
    
    for h in hysplit_files:

        filetest = h.split('.')

        try:
            if filetest[1] == 'mat' and not('Aerostats' in h or 'traceback' in h):
                files += 1
                hysplit_dict = scipy.io.loadmat(h)

                lat = hysplit_dict['lat']
                lon = hysplit_dict['lon']

                data_index = []
                d_total = 0

                tracks = tracks + len(lat)
                
                for n in range(1,len(lat)):

                    [d_temp,theta_temp] = tools.haversine(lat[n-1],lon[n-1],lat[n],lon[n])
                    d_total = d_total + d_temp
                    
                    if G_minlat < lat[n] < G_maxlat:
                        if G_minlon < lon[n] < G_maxlon:

                            [G_range,G_theta] = tools.haversine(lat[n],lon[n],Gobi_coord[0],Gobi_coord[1])

                            G_rad = tools.ellipserad(Gobi_a,Gobi_b,G_theta,Gobi_tilt)

                            if G_range < G_rad:
                                data_index.append(n)
                                delta_d.append(d_total)
                                desert_tag.append('Gobi')
                                G += 1
                                
                    if T_minlat < lat[n] < T_maxlat:
                        if T_minlon < lon[n] < T_maxlon:

                            [T_range,T_theta] = tools.haversine(lat[n],lon[n],Tman_coord[0],Tman_coord[1])
                            T_rad = tools.ellipserad(Tman_a,Tman_b,T_theta,Tman_tilt)

                            if T_range < T_rad:
                                data_index.append(n)
                                delta_d.append(d_total)
                                desert_tag.append('Tman')
                                T += 1
                        
                for n in range(0,len(data_index)):
                    tempdate = dt.datetime(hysplit_dict['year'][0],hysplit_dict['month'][0],hysplit_dict['day'][0],\
                                     hysplit_dict['hour'][0])
                    start_date.append(tempdate)
                    start_loc.append((lat[0],lon[0]))
                    end_loc.append((lat[data_index[n]],lon[data_index[n]]))
                    delta_t.append(hysplit_dict['delta_t'][data_index[n]])
                    station.append(station_id)
            
        except IndexError:
            pass

    output_data = (station,start_loc,end_loc,delta_t,delta_d,desert_tag)

    output_dict = dict(zip(data_keys,output_data))

    df_out = pan.DataFrame(output_dict, index = start_date)

    pan.save(df_out, output_filename)
           
    os.chdir(startdir)

    print 'Out of %i files, %i total tracks checked' %(files,tracks)
    G_percent = 100.0*G/tracks
    T_percent = 100.0*T/tracks
    print '%0.3f percent of tracks passed over Gobi (or %i total)' %(G_percent, G)
    print '%0.3f percent of tracks passed over Taklimikan (or %i total)' %(T_percent, T)


        


