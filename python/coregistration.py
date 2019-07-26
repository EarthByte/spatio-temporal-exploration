import scipy.spatial
import time
def co_reg(point, rotation_model, raster, points_tree, f):
    lat = point[1]
    lon = point[0]
    age = point[2]
    time = point[3]
    plate_id = point[4]
    group_id = point[5]
    
    point_to_rotate = pygplates.PointOnSphere((lat,lon))

    finite_rotation = rotation_model.get_rotation(time, plate_id)
    rotated_point = finite_rotation * point_to_rotate

    paleo_lat, paleo_lon = rotated_point.to_lat_lon()
    
    region=5.0 #degrees
                
    #-------------------#
    #Coregisterring raster 1
    #-------------------#
    #Find the region in index units
    r=numpy.round(region/(x[1]-x[0]))

    #Find the index unit of lat and lon
    idxLon = (numpy.abs(x-paleo_lon)).argmin()
    idxLat = (numpy.abs(y-paleo_lat)).argmin()

    #Raster 1
    c2=coregRaster([idxLon,idxLat],raster,r)
    #Hack to search further around the age grid if it can't find a match, note index units (not degrees)
    if numpy.isnan(c2):
        c2=coregRaster([idxLon,idxLat],raster,r+150.0)
        print("Trying raster region: ", r+150.0)

        #-------------------#
        #Coregisterring vector 1
        #-------------------#
    index=coregPoint([paleo_lon,paleo_lat],f,region,points_tree)
    if index=='inf':
        print("trying index region", region+15)
        index=coregPoint([paleo_lon,paleo_lat],f,region+15.0,points_tree)

    if numpy.isnan(c2) or index=='inf':
        return []

    else:
        #Vector 1
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
            #print mod
            if not (mod < step/2.):
                #print mod, step/2., step
                idx = idx+1 
            ret.append(times[idx])
        
    return ret  

tic=time.time()

points=[]
rotation_model = pygplates.RotationModel(DATA_DIR + "Muller_gplates/Global_EarthByte_230-0Ma_GK07_AREPS.rot" )

andeanPoints = DATA_DIR + "CopperDeposits/XYBer14_t2_ANDES.shp"
[recs,shapes,fields,Nshp]=readTopologyPlatepolygonFile(andeanPoints)  
randomAges=numpy.random.randint(1,230,size=Nshp)
times = get_time_from_age(numpy.array(recs)[:,6], 0, 230, 1)

for i in range(Nshp):
    #Longs, #Lats, #Ages, #time, #PlateIDs, group_id
    points.append((recs[i][3], recs[i][4], recs[i][6], times[i], recs[i][7], 0))
    points.append((recs[i][3], recs[i][4], randomAges[i], randomAges[i], recs[i][7], 1))

f = numpy.loadtxt(DATA_DIR + "Muller_convergence/subStats_0.csv", delimiter=',')
lonlat=f[(f[:,17])==201][379:]
print len(lonlat)
for p in lonlat:
    for t in range(230):
        points.append((p[0], p[1], 0, t, 201, 2))
        
sorted_points = sorted(points, key = lambda x: x[3]) #sort by time
from itertools import groupby
for t, group in groupby(sorted_points, lambda x: x[3]):  #group by time
    #print t
    rasterfile = DATA_DIR + \
        "Muller_etal_2016_AREPS_Agegrids_v1.11/netCDF_0-230Ma/EarthByte_AREPS_v1.11_Muller_etal_2016_AgeGrid-" + \
        str(t)+".nc"
    [x,y,z]=gridRead(rasterfile)

    data=numpy.loadtxt(DATA_DIR + "Muller_convergence/subStats_"+str(t)+".csv", delimiter=',')  
    tree = scipy.spatial.cKDTree(data[:,0:2])
    for point in group:
        #pass
        #print point
        co_reg(point, rotation_model, z, tree, data)

toc=time.time()
print("Time taken:", toc-tic, " seconds") 
