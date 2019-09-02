#!/usr/bin/env python
# -*- coding: utf-8 -*-

# python convergence.py 2>log

from parameters import parameters as p
import pprint, sys, math, os
sys.path.append(p["plate_tectonic_tools_path"])
from subduction_convergence import subduction_convergence_over_time
import numpy as np

if __name__ == '__main__':
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
    print('The result data has been saved in {}!'.format(result_dir))        

