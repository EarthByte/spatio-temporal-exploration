#!/usr/bin/env python
# -*- coding: utf-8 -*-

# python convergence.py 2>log

from parameters import parameters as p
import pprint, sys, math, os
sys.path.append(p["plate_tectonic_tools_path"])
from subduction_convergence import subduction_convergence_over_time
import numpy as np
import pandas as pd

#basicall the subduction_convergence.py does most of the work.
#see https://github.com/EarthByte/PlateTectonicTools/blob/master/ptt/subduction_convergence.py

#The columns in the output file
#0 lon
#1 lat
#2 subducting convergence (relative to trench) velocity magnitude (in cm/yr)
#3 subducting convergence velocity obliquity angle (angle between trench normal vector and convergence velocity vector)
#4 trench absolute (relative to anchor plate) velocity magnitude (in cm/yr)
#5 trench absolute velocity obliquity angle (angle between trench normal vector and trench absolute velocity vector)
#6 length of arc segment (in degrees) that current point is on
#7 trench normal azimuth angle (clockwise starting at North, ie, 0 to 360 degrees) at current point
#8 subducting plate ID
#9 trench plate ID
#10 distance (in degrees) along the trench line to the nearest trench edge
#11 the distance (in degrees) along the trench line from the start edge of the trench
#12 convergence velocity orthogonal (in cm/yr)
#13 convergence velocity parallel  (in cm/yr) 
#14 the trench plate absolute velocity orthogonal (in cm/yr)
#15 the trench plate absolute velocity parallel (in cm/yr)
#16 the subducting plate absolute velocity magnitude (in cm/yr)
#17 the subducting plate absolute velocityobliquity angle (in degrees)
#18 the subducting plate absolute velocity orthogonal       
#19 the subducting plate absolute velocity parallel

def run_it():
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(p)  
    
    start_time = p["time"]["start"]
    end_time = p["time"]["end"]
    time_step = p["time"]["step"]
    conv_dir = p['convergence_data_dir']
    conv_prefix = p['convergence_data_filename_prefix']
    conv_ext = p['convergence_data_filename_ext']

    if not os.path.exists(conv_dir):
        os.makedirs(conv_dir)
    
    kwargs = {    
        'output_distance_to_nearest_edge_of_trench':True,
        'output_distance_to_start_edge_of_trench':True,
        'output_convergence_velocity_components':True,
        'output_trench_absolute_velocity_components':True,
        'output_subducting_absolute_velocity':True,
        'output_subducting_absolute_velocity_components':True}

    return_code = subduction_convergence_over_time(
            conv_dir+conv_prefix,
            conv_ext,
            p["rotation_files"],
            p["topology_files"],
            math.radians(p["threshold_sampling_distance_degrees"]),
            start_time,
            end_time,
            time_step,
            p["velocity_delta_time"],
            p['anchor_plate_id'],
            output_gpml_filename = None,
            **kwargs)
    

    #There are some more data acquired from various grids. 
    #We need them later. Append the additional data to the subduction convergence kinematics statistics.
    #append more data
    for age in reversed(range(start_time, end_time+1, time_step)):
        d1 = pd.read_csv(conv_dir + conv_prefix + '_' + f'{age:.2f}' + '.' + conv_ext, sep=' ', header=None)
        d2 = pd.read_csv(f'../data/subStats_ex/subStats_ex_{age}.csv')
        d3 = pd.concat([d1,d2], axis=1)
        d3.to_csv(conv_dir + conv_prefix + '_' + f'{age:.2f}' + '.' + conv_ext, header=False, sep=' ', index=False, float_format='%.2f')
         
    print("")
    print('Convergence completed successfully!')
    print('The result data has been saved in {}!'.format(conv_dir)) 
    
if __name__ == '__main__':
    run_it()

