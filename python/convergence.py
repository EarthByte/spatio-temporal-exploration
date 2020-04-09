#!/usr/bin/env python
# -*- coding: utf-8 -*-

# python convergence.py 2>log

from parameters import parameters as p
import pprint, sys, math, os, glob
sys.path.append(p["plate_tectonic_tools_path"])
from subduction_convergence import subduction_convergence_over_time
import pandas as pd
import Utils 

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
#17 the subducting plate absolute velocity obliquity angle (in degrees)
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
    
    rotation_files = Utils.get_files(p["rotation_files"])
    topology_files = Utils.get_files(p["topology_files"])
   
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
            rotation_files,
            topology_files,
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
    for age in reversed(range(start_time, end_time+1, time_step)):
        #d1 = pd.read_csv(conv_dir + conv_prefix + '_' + f'{age:.2f}' + '.' + conv_ext, sep=' ', header=None)
        #d2 = pd.read_csv(f'../data/subStats_ex/subStats_ex_{age}.csv')
        #d3 = pd.concat([d1,d2], axis=1)
        #d3.to_csv(conv_dir + conv_prefix + '_' + f'{age:.2f}' + '.' + conv_ext, header=False, sep=' ', index=False, float_format='%.2f')
        print(age, end=' ')
        trench_file = conv_dir + conv_prefix + f'_{age:.2f}.' + conv_ext
        trench_data= pd.read_csv(trench_file, sep=' ', header=None)
        
        seafloor_ages=Utils.query_raster(
            f'../data/AgeGrids/EarthByte_AREPS_v1.15_Muller_etal_2016_AgeGrid-{age}.nc',
            trench_data.iloc[:,0],
            trench_data.iloc[:,1])
        
        thickness = [None]*len(seafloor_ages)
        T1 = 1150.
        for i in range(len(seafloor_ages)):
            thickness[i] = Utils.plate_isotherm_depth(seafloor_ages[i], T1)

        ## To convert arc_length from degrees on a sphere to m (using earth's radius = 6371000 m)
        arc_length_m = 2*math.pi*6371000*trench_data.iloc[:,6]/360

        ## Calculate Subduction Volume (in m^3 per year)
        subduction_volume_m3y = trench_data.iloc[:,12]/100 * thickness * arc_length_m

        ## Calculate Subduciton Volume (slab flux) (in km^3 per year)
        subduction_volume_km3y = subduction_volume_m3y/1e9 
        subduction_volume_km3y[subduction_volume_km3y<0] = 0
    
        decompacted_sediment_thickness=Utils.query_raster(
            f'../data/carbonate_sed_thickness/decompacted_sediment_thickness_0.5_{age}.nc',
            trench_data.iloc[:,0],
            trench_data.iloc[:,1])

        sed_thick=Utils.query_raster(
            f'../data/predicted_oceanic_sediment_thickness/sed_thick_0.2d_{age}.nc',
            trench_data.iloc[:,0],
            trench_data.iloc[:,1])

        ocean_crust_carb_percent=Utils.query_raster(
            f'../data/ocean_crust_CO2_grids/ocean_crust_carb_percent_{age}.nc',
            trench_data.iloc[:,0],
            trench_data.iloc[:,1])
        
        trench_data['seafloor_age'] = seafloor_ages
        trench_data['subduction_volume_km3y'] = subduction_volume_km3y
        trench_data['carbonate_sediment_thickness'] = decompacted_sediment_thickness
        trench_data['total_sediment_thick'] = sed_thick
        trench_data['ocean_crust_carb_percent'] = ocean_crust_carb_percent
        
        #print(trench_data.shape)
        trench_data.to_csv(f'./convergence_data/subStats_{age}.00.csv', index=False, float_format='%.2f',
            header=['trench_lon','trench_lat','conv_rate','conv_angle','trench_abs_rate','trench_abs_angle',
            'arc_len','trench_norm','subducting_pid','trench_pid','dist_nearest_edge','dist_from_start',
            'conv_ortho','conv_paral','trench_abs_ortho','trench_abs_paral','subducting_abs_rate',
            'subducting_abs_angle','subducting_abs_ortho', 'subducting_abs_paral'] + trench_data.columns[-5:].tolist()
            )
        
    print("")
    print('Convergence completed successfully!')
    print('The result data has been saved in {}!'.format(conv_dir)) 
    
if __name__ == '__main__':
    run_it()

