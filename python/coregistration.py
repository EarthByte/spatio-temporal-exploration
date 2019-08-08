from netCDF4 import Dataset
import scipy.spatial
from scipy.signal import decimate
from scipy.interpolate import griddata
import numpy as np
import time, math, pickle
import pygplates
from matplotlib import pyplot as plt
import shapefile

DATA_DIR = './Week10_data/'

def degree_to_straight_distance(degree):
    return math.sin(math.radians(degree)) / math.sin(math.radians(90 - degree/2.))

#the age is a floating-point number. map the floating-point number to the nereast integer time in the range
def get_time_from_age(ages, start, end, step):
    ret=[]
    times=range(start, end+1, step)
    for age in ages:
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

def get_attributes(point, data, index):
    point[7] = data[index, 3]
    point[8] = data[index, 9]
        

tic=time.time()

raster_region_1 = 5 #degrees
raster_region_2 = 10 #degrees

#construct the grid tree
grid_x, grid_y = np.mgrid[-180:181, -90:91]
grid_points = [pygplates.PointOnSphere((row[1],row[0])).to_xyz() for row in zip(grid_x.flatten(), grid_y.flatten())]
grid_tree = scipy.spatial.cKDTree(grid_points)


#prepare points
f = np.loadtxt(DATA_DIR + "Muller_convergence/subStats_0.csv", delimiter=',')
trench_points=f[(f[:,17])==201][379:]
rotation_model = pygplates.RotationModel(DATA_DIR + "Muller_gplates/Global_EarthByte_230-0Ma_GK07_AREPS.rot" )
reader = shapefile.Reader(DATA_DIR + "CopperDeposits/XYBer14_t2_ANDES.shp")
recs    = reader.records()
andes_points_len = len(recs)
randomAges=np.random.randint(1,230,size=andes_points_len)
times = get_time_from_age(np.array(recs)[:,6], 0, 230, 1)

points=np.full((len(trench_points)*230 + andes_points_len*2,19), float('nan'))
for i in range(andes_points_len):
    points[i][0]=recs[i][3] #lon
    points[i][1]=recs[i][4] #lat
    points[i][4]=recs[i][6] #age
    points[i][5]=times[i] #time
    points[i][-1]=recs[i][7] #plate id
    
points_with_age_size=i+1

for i in range(andes_points_len): 
    points[points_with_age_size+i][0]=recs[i][3] #lon
    points[points_with_age_size+i][1]=recs[i][4] #lat
    points[points_with_age_size+i][4]=randomAges[i] #age
    points[points_with_age_size+i][5]=randomAges[i] #time
    points[points_with_age_size+i][-1]=recs[i][7] #plate id
    
points_with_random_age_size=i+1

start_idx = points_with_age_size + points_with_random_age_size
i=0
for p in trench_points:
    for t in range(230):
        points[start_idx+i][0]=p[0] #lon
        points[start_idx+i][1]=p[1] #lat
        points[start_idx+i][4]=0 #age
        points[start_idx+i][5]=t #time
        points[start_idx+i][-1]=201 #plate id
        i+=1
        
poins_all_time_size=i+1 


sorted_points = sorted(points, key = lambda x: int(x[5])) #sort by time
from itertools import groupby
for t, group in groupby(sorted_points, lambda x: int(x[5])):  #group by time
    print(t)
    rasterfile = Dataset(DATA_DIR + \
        "Muller_etal_2016_AREPS_Agegrids_v1.11/netCDF_0-230Ma/EarthByte_AREPS_v1.11_Muller_etal_2016_AgeGrid-" + \
        str(t)+".nc",'r')
    z = rasterfile.variables['z'][:] #masked array
    z = z[::10,::10]
    z = z.flatten()
    
    data=np.loadtxt(DATA_DIR + "Muller_convergence/subStats_"+str(t)+".csv", delimiter=',') 
    points_3d = [pygplates.PointOnSphere((row[1],row[0])).to_xyz() for row in data]
    points_tree = scipy.spatial.cKDTree(points_3d)
   
    rotated_points = []
    grouped_points = list(group)
    for point in grouped_points:
        point_to_rotate = pygplates.PointOnSphere((point[1], point[0]))
        finite_rotation = rotation_model.get_rotation(point[5], int(point[-1]))
        geom = finite_rotation * point_to_rotate
        rotated_points.append(geom.to_xyz())
        point[3], point[2] = geom.to_lat_lon()
    
    dists, indices = points_tree.query(
        rotated_points, k=1, distance_upper_bound=degree_to_straight_distance(raster_region_1)) 
    all_neighbors = grid_tree.query_ball_point(
            rotated_points, 
            degree_to_straight_distance(raster_region_1))
    
    for point, dist, idx, neighbors in zip(grouped_points, dists, indices, all_neighbors):
        if idx < len(data):
            get_attributes(point, data, idx)
        else:
            #try again with a bigger region
            dist_2, index_2 = points_tree.query(
                pygplates.PointOnSphere((point[3], point[2])).to_xyz(), 
                k=1, 
                distance_upper_bound=degree_to_straight_distance(raster_region_2))
            if index_2 < len(data):
                get_attributes(point, data, index_2)
            
        if np.sum(~z[neighbors].mask)>0:
            point[6] = np.nanmean(z[neighbors])
        else: 
            #try again with a bigger region
            neighbors_2 = grid_tree.query_ball_point(
                pygplates.PointOnSphere((point[3], point[2])).to_xyz(), 
                degree_to_straight_distance(raster_region_2))
            if np.sum(~z[neighbors_2].mask)>0:
                point[6] = np.nanmean(z[neighbors_2])
            
print(points)
 
'''    
    segmentLength=f[index,3]
        slabLength=f[index,9]
        distSlabEdge=f[index,15]

        SPcoregNor=f[index,4]
        SPcoregPar=f[index,12]
        OPcoregNor=f[index,5]
        OPcoregPar=f[index,13]
        CONVcoregNor=f[index,10]
        CONVcoregPar=f[index,11]

        subPolCoreg=f[index,8]
        subOblCoreg=f[index,7]
        return [lon,lat,paleo_lon,paleo_lat,age, time, c2,segmentLength,slabLength,distSlabEdge,\
             SPcoregNor,SPcoregPar,OPcoregNor,OPcoregPar,CONVcoregNor,CONVcoregPar,subPolCoreg,subOblCoreg]
'''
toc=time.time()
print("Time taken:", toc-tic, " seconds") 
