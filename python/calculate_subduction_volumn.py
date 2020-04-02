import Utils
from netCDF4 import Dataset
import scipy.spatial
import pygplates
import numpy as np
import cv2

#construct the grid tree
grid_x, grid_y = np.mgrid[-90:91, -180:181]
grid_points = [pygplates.PointOnSphere((float(row[0]), float(row[1]))).to_xyz() for row in zip(grid_x.flatten(), grid_y.flatten())]

for age in range(231):
    print(f'doing {age}Ma')
    grid_file = Utils.download_agegrid(age)
    rasterfile = Dataset(grid_file,'r')
    z = rasterfile.variables['z'][:] #masked array
    zz = cv2.resize(z, dsize=(361, 181), interpolation=cv2.INTER_CUBIC)
    zz = np.roll(zz,180)
    z = np.ma.asarray(zz.flatten())
    
    grid_points = np.asarray(grid_points)
    z_idx = ~np.isnan(z)
    z = z[z_idx]
    z[z>230] = 230
    z[z<0] = 0
    grid_tree = scipy.spatial.cKDTree(grid_points[z_idx])
    
    trench_file = f'./convergence_data/subStats_{age}.00.csv'
    trench_data= np.genfromtxt(trench_file)
    trench_points=[pygplates.PointOnSphere((float(row[1]), float(row[0]))).to_xyz() for row in trench_data]
    
    # query the tree 
    dists, indices = grid_tree.query(trench_points, k=1) 
    seafloor_ages = z[indices]
    thickness = [None]*len(seafloor_ages)
    T1 = 1150.
    for i in range(len(seafloor_ages)):
        thickness[i] = Utils.plate_isotherm_depth(seafloor_ages[i], T1)

    ## To convert arc_length from degrees on a sphere to m (using earth's radius = 6371000 m)
    arc_length_m = 2*np.pi*6371000*trench_data[:,6]/360

    ## Calculate Subduction Volume (in m^3 per year)
    subduction_volume_m3y = trench_data[:,12]/100 * np.asarray(thickness) * arc_length_m

    ## Calculate Subduciton Volume (slab flux) (in km^3 per year)
    subduction_volume_km3y = subduction_volume_m3y/1e9 
    
    subduction_volume_km3y[subduction_volume_km3y<0] = 0
    
    decompacted_sediment_thickness=Utils.query_raster(
        f'../data/carbonate_sed_thickness/decompacted_sediment_thickness_0.5_{age}.nc',
        trench_data[:,0],
        trench_data[:,1])
    
    sed_thick=Utils.query_raster(
        f'../data/predicted_oceanic_sediment_thickness/sed_thick_0.2d_{age}.nc',
        trench_data[:,0],
        trench_data[:,1])
    
    ocean_crust_carb_percent=Utils.query_raster(
        f'../data/ocean_crust_CO2_grids/ocean_crust_carb_percent_{age}.nc',
        trench_data[:,0],
        trench_data[:,1])
    
    results = np.c_[seafloor_ages,subduction_volume_km3y,decompacted_sediment_thickness,sed_thick,ocean_crust_carb_percent ]
    print(results.shape)
    np.savetxt(f'../data/subStats_ex/subStats_ex_{age}.csv', 
               results, delimiter=',', fmt='%.2f', 
               header='seafloor_age,subduction_volume_km3y,decompacted_sediment_thickness,sed_thick_0.2d,ocean_crust_carb_percent')
    
    
