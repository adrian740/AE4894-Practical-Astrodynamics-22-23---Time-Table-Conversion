import numpy as np
np.set_printoptions(suppress=True)
import os
import wget
import argparse

def exists(folder, filename):
    return os.path.exists(folder + '/' + filename)

def download_tables(folder, filename):
    if exists(folder, filename):
        os.remove(folder + '/' + filename)
    wget.download('https://maia.usno.navy.mil/ser7/' + filename, out=folder)

def read_file(filename, UT1=True):
    with open(filename) as f:
        ls = []
        for line in f:
            l = line.rstrip('\n')
            if UT1:
                try:
                    ls.append([int(l[7:12]), float(l[58:68])])
                except:
                    pass
            else:
                ls.append([float(l[17:26]), float(l[38:48])])
    return np.array(ls)

def get_offset_UT1(ls, MJD):
    a = ls[np.where(ls[:,0]-MJD==0)]
    if len(a) == 0:
        return None
    return a[0][1]

def get_offset_GPS(ls, JD):
    for a, v in ls[::-1]:
        if JD >= a:
            return v

def get_parser():
    parser = argparse.ArgumentParser(
                    prog = 'Time correction',
                    description = 'What the program does',
                    epilog = 'Text at the bottom of help')
    parser.add_argument("-download_table", 
                        help="Download the leap-second, time correction or both tables",
                        choices=['leap', 'time', 'both'])
    parser.add_argument("--show_leap", nargs=1, type=float,
                        help="Show number of leap seconds for a given JD")
    parser.add_argument("--show_time", nargs=1, type=float,
                        help="Show time correction for a given MJD")
    parser.add_argument("--preview", action='store_true')
    return parser

def process_input():
    parser = get_parser()
    args = parser.parse_args()
    
    if args.download_table is not None:
        if args.download_table == 'leap':
            download_tables('tables', 'tai-utc.dat')
        elif args.download_table == 'time':
            download_tables('tables', 'finals.daily.extended')
        else:
            download_tables('tables', 'tai-utc.dat')
            download_tables('tables', 'finals.daily.extended')
            
    if args.show_leap is not None:
        t = args.show_leap[0]
        if not exists('tables', 'tai-utc.dat'):
            print("First download using '-download_table leap'")
            return
        
        GPS_lines = read_file('tables/tai-utc.dat', UT1=False)
        
        offset = get_offset_GPS(GPS_lines, t)
        
        if offset is not None:
            print(f"Leap Seconds at '{t}': '{offset}'[s]")
        else:
            print(f"Error processing command, check input '{t}'")
    
    if args.show_time is not None:
        t = args.show_time[0]
        if not exists('tables', 'finals.daily.extended'):
            print("First download using '-download_table time'")
            return
        DUT1_lines = read_file('tables/finals.daily.extended')
        
        offset = get_offset_UT1(DUT1_lines, t)
        
        if offset is not None:
            print(f"Time correction at '{t}': '{offset}'[s]")
        else:
            print(f"Error processing command, check input '{t}'")
            
    if args.preview:
        if not exists('tables', 'tai-utc.dat'):
            print("First download using '-download_table leap'")
            return
        if not exists('tables', 'finals.daily.extended'):
            print("First download using '-download_table time'")
            return
        GPS_lines = read_file('tables/tai-utc.dat', UT1=False)
        DUT1_lines = read_file('tables/finals.daily.extended')
        print(f'Leap Second Corrections: (JD, s) \n{GPS_lines[:5]}\n\nTime corrections: (MJD, s) \n{DUT1_lines[:5]}')

if __name__ == '__main__':
    if not os.path.exists("tables"):
        os.makedirs("tables")
    
    # You can change the following line to code for time 
    # standard conversion
    use_input = True
    
    if use_input:
        print('use -h for help!')
        process_input()
    else:
        download_tables('tables', 'tai-utc.dat')
        GPS_correction_table = read_file('tables/tai-utc.dat', UT1=False)
        JD = 2439127.5
        offset = get_offset_GPS(GPS_correction_table, JD)
        print(f'For {JD=}, the GPS leap-second correction offset is {offset}[s]')
        
        download_tables('tables', 'finals.daily.extended')
        DUT1_correction_table = read_file('tables/finals.daily.extended')
        MJD = 59714.00
        offset = get_offset_UT1(DUT1_correction_table, MJD)
        print(f'For {MJD=}, the UT1 correction offset is {offset}[s]')
    