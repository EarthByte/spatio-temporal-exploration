#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parameters import parameters as p
import pprint, sys, math
sys.path.append(p["plate_tectonic_tools_path"])
from subduction_convergence import subduction_convergence
import numpy as np
import pygplates

'''
INPUT: 2D array with the following columns
    0  longitude
    1  latitude 
    2  subducting convergence (relative to subduction zone) velocity magnitude (in cm/yr)
    3  subducting convergence velocity obliquity angle (angle between subduction zone normal 
        vector and convergence velocity vector)
    4  subduction zone absolute (relative to anchor plate) velocity magnitude (in cm/yr)
    5  subduction zone absolute velocity obliquity angle (angle between subduction zone normal 
        vector and absolute velocity vector)
    6  length of arc segment (in degrees) that current point is on
    7  subducting arc normal azimuth angle (clockwise starting at North, ie, 0 to 360 degrees) at current point
    8  subducting plate ID
    9  overriding plate ID
    10 subduction zone (trench) plate ID
    11 subducting plate velocity (vector3D)
    12 overriding plate velocity (vector3D)
    https://github.com/EarthByte/PlateTectonicTools/blob/master/ptt/subduction_convergence.py
    
OUTPUT:
    0  lon #longitude
    1  lat #latitude 
    2  convergence_velocity_magnitude (convRate) # the magnitude of convergence velocity(cm/yr) 
    3  arc_length (distance)                     # segmentLength(km) 
    4  orthogonal_subducting_velocity (orthAbs)  # orthogonal absolute subducting plate velocity 
    5  orthogonal_overriding_velocity (orthOP)   # orthogonal overriding plate velocity
    6  orthogonal_trench_velocity (orthTrench)   # orthogonal trench velocity(cm/yr)
    7  subducting_obliquity (subObliquity)       # subducting obliquity(degrees)
    8  arc_angle (subPolarity)                   # subducting arc normal azimuth angle(degrees)
    9  distEdge                                  # DistanceToSlabEdge(km)
    10 orthogonal_convergence_velocity           # orthogonal convergence velocity (cm/yr)
    11 parallel_convergence_velocity (convPar)   # parallel convergence velocity (cm/yr)
    12 parallel_subducting_velocity (parAbs)     # parallel absolute subducting plate velocity (mm/yr) 
    13 parallel_overriding_velocity (parOP)      # parallel overriding plate velocity (mm/yr)
    14 parallel_trench_velocity (parTrench)      # parallel trench velocity (cm/yr)
    15 distEdgeTotal                             # toal Distance To Slab Edge(km)
    16 s_pid                                     # subducting plate id
    17 trench_pid                                #subduction zone plate id (AKA trench plate id) 
    18 o_pid                                     #overriding plate id
'''
def compute_extra_stats(input_data):
    ret = []
    #get arc vectors from arc normal azimuth angle
    arc_vectors = pygplates.LocalCartesian.convert_from_magnitude_azimuth_inclination_to_geocentric(
            np.array(input_data)[:,(1,0)], 
            [(1,x,0) for x in np.array(input_data)[:,7]])
    
    for idx, row in enumerate(input_data):
        subducting_obliquity = pygplates.Vector3D.angle_between(
            np.array(row[11].to_xyz()), #subducting plate velocity
            np.array(arc_vectors[idx].to_xyz())) #arc vector
        
        overriding_obliquity = pygplates.Vector3D.angle_between(
            np.array(row[12].to_xyz()), #overriding plate velocity
            np.array(arc_vectors[idx].to_xyz())) #arc vector
        
        #######################fill the fields below################
        #longitude
        lon = row[0]
        
        #latitude
        lat = row[1]
        
        #the magnitude of convergence velocity(cm/yr) 
        convergence_velocity_magnitude = row[2] 
        
        #segmentLength(km) 
        arc_length = np.radians(row[6]) * pygplates.Earth.mean_radius_in_kms
        
        #orthogonal absolute subducting plate velocity 
        orthogonal_subducting_velocity = np.dot(
            np.array(row[11].to_xyz()),
            np.array(row[11].to_xyz())) * math.cos(math.radians(subducting_obliquity))
        
        #orthogonal overriding plate velocity
        orthogonal_overriding_velocity = np.dot(
            np.array(row[12].to_xyz()),
            np.array(row[12].to_xyz())) * math.cos(math.radians(overriding_obliquity))
        
        #orthogonal trench velocity(cm/yr)
        orthogonal_trench_velocity = row[4] * math.cos(math.radians(row[5]))
        
        #subducting obliquity(degrees)
        subducting_obliquity = row[3]
        
        #subducting arc normal azimuth angle(degrees)
        arc_angle = row[7]
        
        # DistanceToSlabEdge(km)
        distEdge = 0#TODO
        
        # orthogonal convergence velocity (cm/yr),
        orthogonal_convergence_velocity = convergence_velocity_magnitude * math.cos(math.radians(row[3]))
        
        # parallel convergence velocity (cm/yr)
        parallel_convergence_velocity = convergence_velocity_magnitude * math.sin(math.radians(row[3]))
        
        # Parallel absolute subducting plate velocity (mm/yr) 
        parallel_subducting_velocity = np.dot(
            np.array(row[11].to_xyz()),
            np.array(row[11].to_xyz())) * math.cos(math.radians(subducting_obliquity))
        
        # Parallel overriding plate velocity (mm/yr)
        parallel_overriding_velocity = np.dot(
            np.array(row[12].to_xyz()),
            np.array(row[12].to_xyz())) * math.cos(math.radians(overriding_obliquity))
        
        # parallel trench velocity (cm/yr)
        parallel_trench_velocity = row[4] * math.sin(math.radians(row[5]))
        
        # toal Distance To Slab Edge(km)
        distEdgeTotal = 0#TODO
        
        #subducting plate id
        s_pid = row[8]
        
        #subduction zone plate id (AKA trench plate id) 
        trench_pid = row[10]
        
        #overriding plate id
        o_pid = row[9]
        
        ret.append((lon, lat, convergence_velocity_magnitude, arc_length,\
            orthogonal_subducting_velocity, orthogonal_overriding_velocity,\
            orthogonal_trench_velocity, subducting_obliquity, arc_angle, distEdge,\
            orthogonal_convergence_velocity, parallel_convergence_velocity,\
            parallel_subducting_velocity, parallel_overriding_velocity,\
            parallel_trench_velocity, distEdgeTotal,\
            s_pid, trench_pid, o_pid))
    return ret
 
    
def append_velocity(stats, pid_index, time, delta_time, rotation_model):
    new_stats = []
    sorted_stats = sorted(stats, key = lambda x: x[pid_index]) #sort by plate id
    from itertools import groupby
    for pid, group in groupby(sorted_stats, lambda x: x[pid_index]):  #group by plate id
        #print pid
        grouped_stats = [x for x in group]
        points = np.array(grouped_stats)[:,(1,0)]
        rotation = rotation_model.get_rotation(time, pid, time + delta_time, anchor_plate_id=0)
        velocities = pygplates.calculate_velocities(
            points, rotation, delta_time, pygplates.VelocityUnits.cms_per_yr)
        #print(np.array(velocities).shape)
        for i in range(len(grouped_stats)):
            new_stats.append(grouped_stats[i] + tuple([velocities[i]]))
    
    return new_stats



if __name__ == '__main__':
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(p)  
    
    rotation_model = pygplates.RotationModel(p["rotation_files"])

    for time in range(p["time"]["start"], p["time"]["end"], p["time"]["step"]):
        print('time: {}'.format(time))
        stats = subduction_convergence(
            p["rotation_files"],
            p["topology_files"],
            math.radians(p["threshold_sampling_distance_degrees"]),
            p["velocity_delta_time"],
            anchor_plate_id = 0
        )
        
        #append subducting plate velocity
        stats = append_velocity(stats, 8, time, p["velocity_delta_time"], rotation_model)
        
        #append overriding plate velocity
        stats = append_velocity(stats, 9, time, p["velocity_delta_time"], rotation_model)
            
        print(np.array(stats).shape)
        
        output = compute_extra_stats(stats)
        
        print(np.array(output).shape)
        
        #TODO: save the output data for this time step
print('done!') 

