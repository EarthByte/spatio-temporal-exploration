#!/usr/bin/env python
# -*- coding: utf-8 -*-

# python convergence.py 2>log

from parameters import parameters as p
import pprint, sys, math, os
sys.path.append(p["plate_tectonic_tools_path"])
from subduction_convergence import subduction_convergence_over_time
import numpy as np

#basicall the subduction_convergence.py does all the work.
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
#15 the trench plate absolute velocity orthogonal (in cm/yr)
#16 the subducting plate absolute velocity magnitude (in cm/yr)
#17 the subducting plate absolute velocityobliquity angle (in degrees)
#18 the subducting plate absolute velocity orthogonal       
#19 the subducting plate absolute velocity parallel

def run_it():
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(p)  
    
    kwargs = {    
        'output_distance_to_nearest_edge_of_trench':True,
        'output_distance_to_start_edge_of_trench':True,
        'output_convergence_velocity_components':True,
        'output_trench_absolute_velocity_components':True,
        'output_subducting_absolute_velocity':True,
        'output_subducting_absolute_velocity_components':True}

    return_code = subduction_convergence_over_time(
            p['convergence_data_filename_prefix'],
            p['convergence_data_filename_ext'],
            p["rotation_files"],
            p["topology_files"],
            math.radians(p["threshold_sampling_distance_degrees"]),
            p["time"]["start"],
            p["time"]["end"],
            p["time"]["step"],
            p["velocity_delta_time"],
            p['anchor_plate_id'],
            output_gpml_filename = None,
            **kwargs)
    
    result_dir=p['convergence_data_dir']
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    os.system('mv {0}*{1} {2}'.format( 
        p['convergence_data_filename_prefix'], p['convergence_data_filename_ext'], result_dir))
    print("")
    print('Convergence completed successfully!')
    print('The result data has been saved in {}!'.format(result_dir)) 
    
if __name__ == '__main__':
    run_it()

