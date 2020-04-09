#!/usr/bin/env python3

#start with the main() function and follow the code
#the input file is defined in parameters.py and has the same length with the output files.

from netCDF4 import Dataset
import scipy.spatial
from scipy.signal import decimate
from scipy.interpolate import griddata
import numpy as np
import time, math, pickle, os, urllib, csv, glob
import pygplates
#from matplotlib import pyplot as plt
import shapefile
import cv2

from parameters import parameters as param

#construct the grid tree
grid_x, grid_y = np.mgrid[-90:91, -180:181]
grid_points = [pygplates.PointOnSphere((float(row[0]), float(row[1]))).to_xyz() for row in zip(grid_x.flatten(), grid_y.flatten())]
grid_tree = scipy.spatial.cKDTree(grid_points)

rotation_files=[]
for f in param["rotation_files"]:
    rotation_files += glob.glob(f)

rotation_model = pygplates.RotationModel(rotation_files) #load rotation model

# input: degrees between two points on sphere
# output: straight distance between the two points (assume the earth radius is 1)
# to get the kilometers, use the return value to multiply by the real earth radius
def degree_to_straight_distance(degree):
    return math.sin(math.radians(degree)) / math.sin(math.radians(90 - degree/2.))


def save_data(data, filename):
    row_len=0
    for row in data:
        if len(row)>row_len:
            row_len = len(row)
    with open(filename,"w+") as f:
        for row in data:
            if row:
                f.write(','.join(['{:.2f}'.format(i) for i in row]))
                if len(row)<row_len: #keep the length of rows the same
                    f.write(',')
                    f.write(','.join(['nan']*(row_len-len(row))))
            else:
                f.write('NO_DATA')
            f.write('\n')
    
    
#input: 
    #sample_points: 2D array. The columns are index, lon, lat, time and plate id.
    #vector_file: The name of the data file from which to extract attributes for sample points.
    #             The vector_file contains a set of points and each point associates with a set of attributes.
    #region: region of interest(in degree)
    
#output:
    #2D array(the same length as the sample_points). The columns are reconstructed lon, lat, distance and
    #the attributes copied from vector_file
    
#For each point(row) in a 2D array sample_points, search the nearest point from vector_file within the region
#of interest. If the nearest point is found, copy its attributes to the input point.
def query_vector(sample_points, vector_file, region):
    #prepare the list for result data and insert indices for input points 
    ret=[]
    indices_bak = []
    for i in range(len(sample_points)):
        ret.append([None, None])
        indices_bak.append(sample_points[i][0]) #keep a copy of the original indices
        sample_points[i][0] = i
        
    #sort and group by time to improve performance
    sorted_points = sorted(sample_points, key = lambda x: int(x[3])) #sort by time
    from itertools import groupby
    for t, group in groupby(sorted_points, lambda x: int(x[3])):  #group by time
        #print('querying '+vector_file.format(time=t))
        # build the points tree at time t
        data=np.loadtxt(vector_file.format(time=t), skiprows=1, delimiter=',') 

        #assume first column is lon and second column is lat
        points_3d = [pygplates.PointOnSphere((row[1],row[0])).to_xyz() for row in data]
        points_tree = scipy.spatial.cKDTree(points_3d)

        # reconstruct the points
        rotated_points = []
        grouped_points = list(group)#must make a copy, the items in "group" will be gone after first iteration
        for point in grouped_points:
            point_to_rotate = pygplates.PointOnSphere((point[2], point[1]))
            finite_rotation = rotation_model.get_rotation(point[3], int(point[4]))#time, plate_id
            geom = finite_rotation * point_to_rotate
            rotated_points.append(geom.to_xyz())
            idx = point[0]
            ret[idx][1], ret[idx][0] = geom.to_lat_lon()
                   
        # query the tree of points 
        dists, indices = points_tree.query(
            rotated_points, k=1, distance_upper_bound=degree_to_straight_distance(region)) 

        for point, dist, idx in zip(grouped_points, dists, indices):
            if idx < len(data):
                ret[point[0]] = ret[point[0]] + [dist, idx] + list(data[idx])
    
    #restore original indices
    for i in range(len(indices_bak)):
        sample_points[i][0] = indices_bak[i]
    return ret
   
    

#input: 
    #sample_points: 2D array. The columns are index, lon, lat, time and plate id.
    #grid_file: The name of the grid file from which to extract data for sample points.
    #region: region of interest(in degree)
    
#output:
    #2D array(the same length as the sample_points). 
    #The columns are reconstructed lon, lat, region and grid mean value.
    
#For each point(row) in a 2D array sample_points, calculate the mean value of the grid data within the region
#of interest. Attach the mean value to the input point.
def query_grid(sample_points, grid_file, region):
    #prepare the list for result data and insert indices for input points 
    ret=[]
    indices_bak = []
    for i in range(len(sample_points)):
        ret.append([None, None])
        indices_bak.append(sample_points[i][0]) #keep a copy of the original indices
        sample_points[i][0] = i
        
    #sort and group by time to improve performance
    sorted_points = sorted(sample_points, key = lambda x: int(x[3])) #sort by time
    from itertools import groupby
    for t, group in groupby(sorted_points, lambda x: int(x[3])):  #group by time
        #print('querying '+grid_file.format(time=t))
        age_grid_fn = grid_file.format(time=t)

        rasterfile = Dataset(age_grid_fn,'r')
        z = rasterfile.variables['z'][:] #masked array
        zz = cv2.resize(z, dsize=(316, 181), interpolation=cv2.INTER_CUBIC)
        zz = np.roll(zz,180)
        z = np.ma.asarray(zz.flatten())
        
        # reconstruct the points
        rotated_points = []
        grouped_points = list(group)#must make a copy, the items in "group" will be gone after first iteration
        for point in grouped_points:
            point_to_rotate = pygplates.PointOnSphere((point[2], point[1]))
            finite_rotation = rotation_model.get_rotation(point[3], int(point[4]))#time, plate_id
            geom = finite_rotation * point_to_rotate
            rotated_points.append(geom.to_xyz())
            idx = point[0]
            ret[idx][1], ret[idx][0] = geom.to_lat_lon()
                   

       # query the grid tree
        all_neighbors = grid_tree.query_ball_point(
                rotated_points, 
                degree_to_straight_distance(region))

        for point, neighbors in zip(grouped_points, all_neighbors): 
            if np.sum(~z[neighbors].mask)>0:
                ret[point[0]] = ret[point[0]] + [region] + [np.nanmean(z[neighbors])]
                        
    #restore original indices
    for i in range(len(indices_bak)):
        sample_points[i][0] = indices_bak[i]
    return ret

def write_readme_file():
    with open(param['output_dir']+'/readme.pls', "w+") as f:
        f.write('''the convergence attributes are
    #0 reconstructed input point lon 
    #1 reconstructed input point lat 
    #2 distance to the nearest trench point
    #3 trench point lon
    #4 trench point lat
    #5 subducting convergence (relative to trench) velocity magnitude (in cm/yr)
    #6 subducting convergence velocity obliquity angle (angle between trench normal vector and convergence velocity vector)
    #7 trench absolute (relative to anchor plate) velocity magnitude (in cm/yr)
    #8 trench absolute velocity obliquity angle (angle between trench normal vector and trench absolute velocity vector)
    #9 length of arc segment (in degrees) that current point is on
    #10 trench normal azimuth angle (clockwise starting at North, ie, 0 to 360 degrees) at current point
    #11 subducting plate ID
    #12 trench plate ID
    #13 distance (in degrees) along the trench line to the nearest trench edge
    #14 the distance (in degrees) along the trench line from the start edge of the trench
    #15 convergence velocity orthogonal (in cm/yr)
    #16 convergence velocity parallel  (in cm/yr)
    #17 the trench plate absolute velocity orthogonal (in cm/yr)
    #18 the trench plate absolute velocity orthogonal (in cm/yr)
    #19 the subducting plate absolute velocity magnitude (in cm/yr)
    #20 the subducting plate absolute velocityobliquity angle (in degrees)
    #21 the subducting plate absolute velocity orthogonal
    #22 the subducting plate absolute velocity parallel
''')
        f.write('''the grid attributes are
    #0 reconstructed lon 
    #1 reconstructed lat 
    #2 region of interest(in degree) and 
    #3 grid mean value
''')
        f.write('''the input attributes are
    #0 index 
    #1 lon 
    #2 lat 
    #3 reconstruction time 
    #4 plate id
''')
        
def main():
    #create output dir
    out_dir=param['output_dir']
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
        
    write_readme_file()
    
    os.system(f"cp {param['input_file']} {param['output_dir']}")

    tic=time.time()
    
    #load input data
    input_data=[]
    with open( param['input_file']) as csvfile:
        r = csv.reader(csvfile, delimiter=',')
        for row in r:
            try:
                input_data.append([int(row[0]), float(row[1]), float(row[2]), int(row[3]), int(row[4])])
            except:
                continue
    #print(input_data)
    input_data_backup = input_data
   
    count=0
    #query the vector data
    for in_file in param['vector_files']:
        input_data = input_data_backup
        result=[None]*len(input_data)
        for region in sorted(param['regions']):
            print('region of interest: {}'.format(region))
            print('the length of input data is: {}'.format(len(input_data)))
            
            ret = query_vector(input_data, in_file, region)
            
            new_input_data=[]
            for i in range(len(input_data)):
                result[input_data[i][0]] = ret[i] #save the result
                if not len(ret[i]) > 2:
                    new_input_data.append(input_data[i])#prepare the input data to query again with a bigger region
            
            input_data = new_input_data
                    
        save_data(result, out_dir+'/{}_vector_'.format(count) + os.path.basename(in_file).split("_")[0] + '.out')
        count+=1
     
    count=0
    #query the grids 
    for in_file in param['grid_files']:
        input_data = input_data_backup
        result=[None]*len(input_data)
        for region in sorted(param['regions']):
            print('region of interest: {}'.format(region))
            print('the length of input data is: {}'.format(len(input_data)))
            
            ret = query_grid(input_data, in_file, region)
            
            new_input_data=[]
            for i in range(len(input_data)):
                result[input_data[i][0]] = ret[i] #save the result
                if not len(ret[i]) > 2:
                    new_input_data.append(input_data[i])#prepare the input data to query again with a bigger region
            
            input_data = new_input_data
                    
        save_data(result, out_dir+'/{}_grid_'.format(count) + os.path.basename(in_file).split("-")[0] + '.out')
        count+=1
        
    toc=time.time()
    print(f'The coregistration output data have been saved in folder {out_dir} successfully!')
    print("Time taken:", toc-tic, " seconds")
  
if __name__ == "__main__":
    main()
