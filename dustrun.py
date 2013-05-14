import sys,os
import hysplit_tools as tools
import subprocess

# create list of stations in question
UBC = ('UBC',49.256,-123.250) #done
Whistler = ('WHI',50.128,-122.95) #done
Egbert = ('EGB',44.232,-79.781) #done
Yellowknife = ('YKN',62.451,-114.376) #done
Fort_McMurray = ('FMM',56.752,-111.476) #done
Kelowna = ('KEL',49.941,-119.400) #done
Saturna_Island = ('SAT',48.783,-123.133)
Chapais = ('CHA',49.822,-74.975) 
Univ_Leth = ('UOL',49.682,-112.869)
Bratts_Lake = ('BRA',50.279,-104.7)
Sioux_Falls = ('SIO',43.736,96.626)
Trinidad_head = ('TRI',41.054,-124.151) #done
UMBC = ('UMB',39.255,-76.709) #done
GSFC = ('GSF',38.9925,-76.839833) #done
Mauna_Loa = ('MAU',19.539,-155.578003)
Bonanza_Creek = ('BON',64.742805,-148.316269)

Beijing = ('BEI',39.977,116.381)
Dalanzadgad = ('DAL',43.577222,104.419167)
SACOL = ('SAC',35.946,104.137)
Xiang_he = ('XHE',39.754,116.962)

stations = [Saturna_Island, Chapais, Univ_Leth, Bratts_Lake]

#set heights
heights = range(1000,10200,200)

#set dates and times
year = '10'
month = '03'
day = range(15,32)
hour = range(0,24,6)

totalruns = len(stations)*len(day)*len(hour)*len(heights)
runs = 0

#select meteorology files

meteo_list = tools.get_files('Select Meteorology Files')
meteo_files = meteo_list.split()

#set output directory

output_dir = tools.set_dir('Select Output Directory')

for s in stations:
    for d in day:
        for h in hour:
            for z in heights:
                start_time = [year,month,d,h]

                run_hours = '-240'
                    
                tools.control_single(s,start_time,run_hours,z,meteo_files,output_dir)
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                proc = subprocess.call('c:/hysplit4/exec/hyts_std', startupinfo=startupinfo)
                runs += 1
                complete = 100.0*runs/totalruns
                print_time = ' '
                for n in start_time:
                    print_time += str(n)
                print s[0]+' '+print_time+' '+str(z)+'m'
                print str(complete)+'% complete'
                    
                
            
