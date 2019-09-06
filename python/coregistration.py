from netCDF4 import Dataset
import scipy.spatial
from scipy.signal import decimate
from scipy.interpolate import griddata
import numpy as np
import time, math, pickle, os, urllib
import pygplates
from matplotlib import pyplot as plt
import shapefile

from parameters import parameters as param

# output data
# 
#0 lon
#1 lat
#2 reconstructed lon 
#3 reconstructed lat 
#4 age
#5 time
#6 age at reconstructed location (from age grid)
#7 subducting convergence (relative to trench) velocity magnitude (in cm/yr)
#8 subducting convergence velocity obliquity angle (angle between trench normal vector and convergence velocity vector)
#9 trench absolute (relative to anchor plate) velocity magnitude (in cm/yr)
#10 trench absolute velocity obliquity angle (angle between trench normal vector and trench absolute velocity vector)
#11 length of arc segment (in degrees) that current point is on
#12 trench normal azimuth angle (clockwise starting at North, ie, 0 to 360 degrees) at current point
#13 subducting plate ID
#14 trench plate ID
#15 distance (in degrees) along the trench line to the nearest trench edge
#16 the distance (in degrees) along the trench line from the start edge of the trench
#17 convergence velocity orthogonal (in cm/yr)
#18 convergence velocity parallel  (in cm/yr) 
#19 the trench plate absolute velocity orthogonal (in cm/yr)
#20 the trench plate absolute velocity orthogonal (in cm/yr)
#21 the subducting plate absolute velocity magnitude (in cm/yr)
#22 the subducting plate absolute velocityobliquity angle (in degrees)
#23 the subducting plate absolute velocity orthogonal       
#24 the subducting plate absolute velocity parallel
#25 plate id of the input point
ROW_LEN = 26

def main():
    start_time = param["time"]["start"]
    end_time = param["time"]["end"]
    time_step =  param["time"]["step"]

    # input: degrees between two points on sphere
    # output: straight distance between the two points (assume the earth radius is 1)
    # to get the kilometers, use the return value to multiply by the real earth radius
    def degree_to_straight_distance(degree):
        return math.sin(math.radians(degree)) / math.sin(math.radians(90 - degree/2.))


    # the age is a floating-point number. map the floating-point number to the nereast integer time in the range
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

    # copy the attributes around
    def get_attributes(point, data, index):
        point[7:25] = data[index, 2:20]

    tic=time.time()

    region_1 = param['region_1'] #degrees
    region_2 = param['region_2'] #degrees

    #construct the grid tree
    grid_x, grid_y = np.mgrid[-180:181, -90:91]
    grid_points = [pygplates.PointOnSphere((row[1],row[0])).to_xyz() for row in zip(grid_x.flatten(), grid_y.flatten())]
    grid_tree = scipy.spatial.cKDTree(grid_points)

    #load files
    f = np.loadtxt(param['convergence_data_dir'] + param['convergence_data_filename_prefix'] 
                        + "_0.00." + param['convergence_data_filename_ext'])
    trench_points=f[(f[:,9])==201]
    rotation_model = pygplates.RotationModel(param['rotation_files'])
    reader = shapefile.Reader(param['andes_data'])
    recs    = reader.records()
    andes_points_len = len(recs)
    randomAges=np.random.randint(start_time+1, end_time, size=andes_points_len)
    times = get_time_from_age(np.array(recs)[:,6], start_time, end_time, time_step)

    # create buffer for points
    points=np.full((len(trench_points)*len(range(end_time)) + andes_points_len*2, ROW_LEN), float('nan'))

    # fill the andes deposit points with the real age
    for i in range(andes_points_len):
        points[i][0]=recs[i][3] #lon
        points[i][1]=recs[i][4] #lat
        points[i][4]=recs[i][6] #age
        points[i][5]=times[i] #time
        points[i][-1]=recs[i][7] #plate id

    points_with_age_size=i+1

    # fill andes deposit points with random ages
    for i in range(andes_points_len): 
        points[points_with_age_size+i][0]=recs[i][3] #lon
        points[points_with_age_size+i][1]=recs[i][4] #lat
        points[points_with_age_size+i][4]=randomAges[i] #age
        points[points_with_age_size+i][5]=randomAges[i] #time
        points[points_with_age_size+i][-1]=recs[i][7] #plate id

    points_with_random_age_size=i+1

    # fill trench points for each time step from start_time to end_time
    start_idx = points_with_age_size + points_with_random_age_size
    i=0
    for p in trench_points:
        for t in range(end_time):
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
        age_grid_fn = param['age_grid_dir'] + param['age_grid_prefix'] + str(t) + ".nc"
        if not os.path.isfile(age_grid_fn):
            urllib.urlretrieve(param['age_grid_url_prefix']+str(t)+".nc", age_grid_fn)

        rasterfile = Dataset(age_grid_fn,'r')
        z = rasterfile.variables['z'][:] #masked array
        z = z[::10,::10] #TODO: make sure the grid is 1 degree by 1 degree
        z = z.flatten()

        # build the points tree
        data=np.loadtxt(param['convergence_data_dir'] + param['convergence_data_filename_prefix'] 
                        + '_{:0.2f}'.format(t) + "." + param['convergence_data_filename_ext']) 
        
        points_3d = [pygplates.PointOnSphere((row[1],row[0])).to_xyz() for row in data]
        points_tree = scipy.spatial.cKDTree(points_3d)

        # reconstruct the points
        rotated_points = []
        grouped_points = list(group)
        for point in grouped_points:
            point_to_rotate = pygplates.PointOnSphere((point[1], point[0]))
            finite_rotation = rotation_model.get_rotation(point[5], int(point[-1]))
            geom = finite_rotation * point_to_rotate
            rotated_points.append(geom.to_xyz())
            point[3], point[2] = geom.to_lat_lon()

        # query the trees
        dists, indices = points_tree.query(
            rotated_points, k=1, distance_upper_bound=degree_to_straight_distance(region_1)) 
        all_neighbors = grid_tree.query_ball_point(
                rotated_points, 
                degree_to_straight_distance(region_1))

        # get the attributes, query the tree again if necessary
        for point, dist, idx, neighbors in zip(grouped_points, dists, indices, all_neighbors):
            if idx < len(data):
                get_attributes(point, data, idx)
            else:
                #try again with a bigger region
                dist_2, index_2 = points_tree.query(
                    pygplates.PointOnSphere((point[3], point[2])).to_xyz(), 
                    k=1, 
                    distance_upper_bound=degree_to_straight_distance(region_2))
                if index_2 < len(data):
                    get_attributes(point, data, index_2)

            if np.sum(~z[neighbors].mask)>0:
                point[6] = np.nanmean(z[neighbors])
            else: 
                #try again with a bigger region
                neighbors_2 = grid_tree.query_ball_point(
                    pygplates.PointOnSphere((point[3], point[2])).to_xyz(), 
                    degree_to_straight_distance(region_2))
                if np.sum(~z[neighbors_2].mask)>0:
                    point[6] = np.nanmean(z[neighbors_2])

    #print(points)
    np.savetxt('./andes_real_age.csv',points[:points_with_age_size], fmt='%.2f')
    np.savetxt('./andes_random_age.csv',points[points_with_age_size:points_with_random_age_size+points_with_age_size], fmt='%.2f')
    np.savetxt('./trench_points.csv',points[points_with_random_age_size+points_with_age_size:], fmt='%.2f')
    toc=time.time()
    print("Time taken:", toc-tic, " seconds")
    
if __name__ == '__main__':
    main()
