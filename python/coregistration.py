from netCDF4 import Dataset
import scipy.spatial
from scipy.signal import decimate
from scipy.interpolate import griddata
import numpy as np
import time, math, pickle, os, urllib, csv
import pygplates
from matplotlib import pyplot as plt
import shapefile
import cv2

from parameters import parameters as param

#construct the grid tree
grid_x, grid_y = np.mgrid[-180:181, -90:91]
grid_points = [pygplates.PointOnSphere((row[1],row[0])).to_xyz() for row in zip(grid_x.flatten(), grid_y.flatten())]
grid_tree = scipy.spatial.cKDTree(grid_points)

rotation_model = pygplates.RotationModel(param['rotation_files']) #load rotation model

# input: degrees between two points on sphere
# output: straight distance between the two points (assume the earth radius is 1)
# to get the kilometers, use the return value to multiply by the real earth radius
def degree_to_straight_distance(degree):
    return math.sin(math.radians(degree)) / math.sin(math.radians(90 - degree/2.))


def save_data(data, filename):
    with open(filename,"w+") as f:
        for row in data:
            if row:
                f.write(','.join(['{:.2f}'.format(i) for i in row]))
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
    indices = []
    for i in range(len(sample_points)):
        ret.append([None, None])
        indices.append(sample_points[i][0]) #keep a copy of the original indices
        sample_points[i][0] = i
        
    #sort and group by time to improve performance
    sorted_points = sorted(sample_points, key = lambda x: int(x[3])) #sort by time
    from itertools import groupby
    for t, group in groupby(sorted_points, lambda x: int(x[3])):  #group by time
        print(vector_file.format(time=t))
        # build the points tree at time t
        data=np.loadtxt(vector_file.format(time=t)) 

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
                ret[point[0]] = ret[point[0]] + [dist] + list(data[idx])
        
    #restore original indices
    for i in range(len(indices)):
        sample_points[i][0] = indices[i]
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
    indices = []
    for i in range(len(sample_points)):
        ret.append([None, None])
        indices.append(sample_points[i][0]) #keep a copy of the original indices
        sample_points[i][0] = i
        
    #sort and group by time to improve performance
    sorted_points = sorted(sample_points, key = lambda x: int(x[3])) #sort by time
    from itertools import groupby
    for t, group in groupby(sorted_points, lambda x: int(x[3])):  #group by time
        print(grid_file.format(time=t))
        age_grid_fn = grid_file.format(time=t)

        rasterfile = Dataset(age_grid_fn,'r')
        z = rasterfile.variables['z'][:] #masked array
        zz = cv2.resize(z, dsize=(316, 181), interpolation=cv2.INTER_CUBIC)
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
    for i in range(len(indices)):
        sample_points[i][0] = indices[i]
    return ret

def main():
    tic=time.time()
    
    #load input data
    input_data=[]
    with open('input_data_example.csv') as csvfile:
        r = csv.reader(csvfile, delimiter=',')
        for row in r:
            input_data.append([int(row[0]), float(row[1]), float(row[2]), int(row[3]), int(row[4])])
    #print(input_data)
    input_data_backup = input_data
    
    #create output dir
    out_dir='coreg_output'
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
   
    count=0
    #query the vector data
    for in_file in param['vector_files']:
        input_data = input_data_backup
        result=[None]*len(input_data)
        for region in sorted(param['regions']):
            print(region)
            ret = query_vector(input_data, in_file, region)
            
            new_input_data=[]
            for i in range(len(input_data)):
                if len(ret[i]) > 2:
                    result[input_data[i][0]] = ret[i] #save the result
                else:
                    new_input_data.append(input_data[i])#prepare the input data to query again with a bigger region
            
            input_data = new_input_data
                    
        save_data(result, out_dir+'/{}_'.format(count) + os.path.basename(in_file).split("_")[0] + '.out')
        count+=1
     
    count=0
    #query the grids 
    for in_file in param['grid_files']:
        input_data = input_data_backup
        result=[None]*len(input_data)
        for region in sorted(param['regions']):
            print(region)
            ret = query_grid(input_data, in_file, region)
            
            new_input_data=[]
            for i in range(len(input_data)):
                if len(ret[i]) > 2:
                    result[input_data[i][0]] = ret[i] #save the result
                else:
                    new_input_data.append(input_data[i])#prepare the input data to query again with a bigger region
            
            input_data = new_input_data
                    
        save_data(result, out_dir+'/{}_'.format(count) + os.path.basename(in_file).split("-")[0] + '.out')
        count+=1
    toc=time.time()
    print("Time taken:", toc-tic, " seconds")
main()
