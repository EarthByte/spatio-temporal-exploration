#!/usr/bin/env python3

#This is an example script of creating input file for conregistration.py.
#The input file is a text file and contains comma-separated values. 
#Each row has five fields -- index, longitude, latitude, time and plate id.

#The script contains hardcoded file names. 
#You should only use this script as an example and modify the example to prepare input data suitable to your research. 

import os, sys
import numpy as np
import shapefile
from parameters import parameters as param
import Utils

# the age is a floating-point number. map the floating-point number to the nereast integer time in the range
def get_time_from_age(ages, start, end, step):
    ret=[]
    times=range(start, end+1, step)
    for age in ages:
        age=float(age)
        if age <= start:
            ret.append(start)
        elif age >= end:
            ret.append(end)
        else:
            idx = int((age - start)//step)
            mod = (age - start)%step
            if not (mod < step/2.):
                idx = idx+1 
            ret.append(times[idx])
    return ret

#
def process_real_deposits(start_time, end_time, time_step):
    if not os.path.isfile('../data/CopperDeposits/XYBer14_t2_ANDES.shp'):
        sys.exit('ERROR!!! File ../data/CopperDeposits/XYBer14_t2_ANDES.shp not found! Find the file or change the code to use another file!')
    reader = shapefile.Reader('../data/CopperDeposits/XYBer14_t2_ANDES.shp')
    recs    = reader.records()
    andes_points_len = len(recs)
    times = get_time_from_age(np.array(recs)[:,6], start_time, end_time, time_step)#get integer ages for andes data

    #index, lon, lat, time, plate id
    data=[]

    # andes deposit points with the real age
    for i in range(andes_points_len):
        data.append([i, recs[i][3], recs[i][4], times[i], recs[i][7]]) 
    return data
 
#
def generate_random_deposits(data, start_time, end_time):
    random_data=[]
    randomAges=np.random.randint(start_time+1, end_time, size=len(data)) #generate random ages for andes data
     # andes deposit points with random ages
    for i in range(len(data)): 
        random_data.append([i, data[i][1], data[i][2], randomAges[i], data[i][4] ])
    return random_data
 
#                                 
def generate_trench_points(start_time, end_time, time_step):
    trench_data=[]
    trench_points = Utils.get_trench_points(0,-85,5,-70,-60) #subduction points in south america 
    i=0
    for t in range(start_time, end_time, time_step):
        for index, p in trench_points.iterrows():
            trench_data.append([i, p['trench_lon'], p['trench_lat'], t, p['trench_pid']]) 
            i+=1   
    return trench_data    

#
def save_data(data,fn):
    # data are ready and write them to file
    with open(fn,"w+") as f:
        f.write('index,lon,lat,age,plate_id\n')
        for row in data:
            #print(row)
            if row:
                f.write('{0:d}, {1:.2f}, {2:.2f}, {3:d}, {4:d}'.format(
                    int(row[0]),float(row[1]),float(row[2]),int(row[3]),int(row[4])))
            f.write('\n')

    print(f'The data have been written into {fn} successfully!')                               

if __name__ == '__main__':
    start_time = param["time"]["start"]
    end_time = param["time"]["end"]
    time_step =  param["time"]["step"]
                                 
    data = process_real_deposits(start_time, end_time, time_step)
                                 
    random_data = generate_random_deposits(data, start_time, end_time)
                                 
    trench_data = generate_trench_points(start_time, end_time, time_step)
                                 
    all_data = data+random_data+trench_data
    for i in range(len(all_data)): 
        all_data[i][0] = i #assign correct indices
                                 
    save_data(all_data, 'coregistration_input_data_example.csv')
                                 
                                 
                                 
                                 