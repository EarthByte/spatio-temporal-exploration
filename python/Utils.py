import requests, os
from matplotlib.colors import LinearSegmentedColormap

def get_age_grid_color_map_from_cpt(cpt_file):
    values=[]
    colors=[]
    with open(cpt_file,'r') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            if line[0] in ['#', 'B', 'F', 'N']: continue
            vals = line.split()
            if len(vals) !=8: continue
            values.append(float(vals[0]))
            values.append(float(vals[4]))
            colors.append([float(vals[1]),float(vals[2]),float(vals[3])])
            colors.append([float(vals[5]),float(vals[6]),float(vals[7])])

    colour_list= []
    for i in range(len(values)):
        colour_list.append((values[i]/(values[-1]-values[0]), 
                        [x/255.0 for x in colors[i]]))
    return LinearSegmentedColormap.from_list('agegrid_cmap', colour_list)

import pygplates
import numpy as np

def make_GPML_velocity_feature(Long,Lat):
# function to make a velocity mesh nodes at an arbitrary set of points defined in Lat
# Long and Lat are assumed to be 1d arrays. 

    # Add points to a multipoint geometry
    multi_point = pygplates.MultiPointOnSphere([(float(lat),float(lon)) for lat, lon in zip(Lat,Long)])

    # Create a feature containing the multipoint feature, and defined as MeshNode type
    meshnode_feature = pygplates.Feature(pygplates.FeatureType.create_from_qualified_string('gpml:MeshNode'))
    meshnode_feature.set_geometry(multi_point)
    meshnode_feature.set_name('Velocity Mesh Nodes from pygplates')

    output_feature_collection = pygplates.FeatureCollection(meshnode_feature)
    
    # NB: at this point, the feature could be written to a file using
    # output_feature_collection.write('myfilename.gpmlz')
    
    # for use within the notebook, the velocity domain feature is returned from the function
    return output_feature_collection


def Get_Plate_Velocities(velocity_domain_features, topology_features, rotation_model, time, delta_time, rep='vector_comp'):
    # All domain points and associated (magnitude, azimuth, inclination) velocities for the current time.
    all_domain_points = []
    all_velocities = []

    # Partition our velocity domain features into our topological plate polygons at the current 'time'.
    plate_partitioner = pygplates.PlatePartitioner(topology_features, rotation_model, time)

    for velocity_domain_feature in velocity_domain_features:

        # A velocity domain feature usually has a single geometry but we'll assume it can be any number.
        # Iterate over them all.
        for velocity_domain_geometry in velocity_domain_feature.get_geometries():

            for velocity_domain_point in velocity_domain_geometry.get_points():

                all_domain_points.append(velocity_domain_point)

                partitioning_plate = plate_partitioner.partition_point(velocity_domain_point)
                if partitioning_plate:

                    # We need the newly assigned plate ID to get the equivalent stage rotation of that tectonic plate.
                    partitioning_plate_id = partitioning_plate.get_feature().get_reconstruction_plate_id()

                    # Get the stage rotation of partitioning plate from 'time + delta_time' to 'time'.
                    equivalent_stage_rotation = rotation_model.get_rotation(time, partitioning_plate_id, time + delta_time)

                    # Calculate velocity at the velocity domain point.
                    # This is from 'time + delta_time' to 'time' on the partitioning plate.
                    velocity_vectors = pygplates.calculate_velocities(
                        [velocity_domain_point],
                        equivalent_stage_rotation,
                        delta_time)
                    
                    if rep=='mag_azim':
                        # Convert global 3D velocity vectors to local (magnitude, azimuth, inclination) tuples (one tuple per point).
                        velocities = pygplates.LocalCartesian.convert_from_geocentric_to_magnitude_azimuth_inclination(
                            [velocity_domain_point],
                            velocity_vectors)
                        all_velocities.append(velocities[0])

                    elif rep=='vector_comp':
                        # Convert global 3D velocity vectors to local (magnitude, azimuth, inclination) tuples (one tuple per point).
                        velocities = pygplates.LocalCartesian.convert_from_geocentric_to_north_east_down(
                                [velocity_domain_point],
                                velocity_vectors)
                        all_velocities.append(velocities[0])

                else:
                    all_velocities.append((0,0,0))

    return all_velocities

def get_velocity_x_y_u_v(time,rotation_model,topology_filenames):
    delta_time = 5.
    Xnodes = np.arange(-180,180,10)
    Ynodes = np.arange(-90,90,10)
    Xg,Yg = np.meshgrid(Xnodes,Ynodes)
    Xg = Xg.flatten()
    Yg = Yg.flatten()
    velocity_domain_features = make_GPML_velocity_feature(Xg,Yg)

    # Load the topological plate polygon features.
    topology_features = []
    for fname in topology_filenames:
        for f in pygplates.FeatureCollection(fname):
            topology_features.append(f)


    # Call the function we created above to get the velocities
    all_velocities = Get_Plate_Velocities(velocity_domain_features,
                                          topology_features,
                                          rotation_model,
                                          time,
                                          delta_time,
                                          'vector_comp')

    uu=[]
    vv=[]
    for vel in all_velocities:
        if not hasattr(vel, 'get_y'): 
            uu.append(vel[1])
            vv.append(vel[0])
        else:
            uu.append(vel.get_y())
            vv.append(vel.get_x())
    u = np.asarray([uu]).reshape((Ynodes.shape[0],Xnodes.shape[0]))
    v = np.asarray([vv]).reshape((Ynodes.shape[0],Xnodes.shape[0]))

    return Xnodes, Ynodes, u, v
    # compute native x,y coordinates of grid.
    #x, y = m(Xg, Yg)

    #uproj,vproj,xx,yy = m.transform_vector(u,v,Xnodes,Ynodes,15,15,returnxy=True,masked=True)
    # now plot.
    #Q = m.quiver(xx,yy,uproj,vproj,scale=1000,color='grey')
    # make quiver key.
    #qk = plt.quiverkey(Q, 0.95, 1.05, 50, '50 mm/yr', labelpos='W')
    
def get_subduction_teeth(lons, lats, tesselation_degrees=5, triangle_base_length=3, triangle_aspect=-1):
    distance = tesselation_degrees 
    teeth=[]
    PA = np.array([lons[0], lats[0]])
    for lon, lat in zip(lons[1:], lats[1:]):
        PB = np.array([lon, lat])
        AB_dist = np.sqrt((PB[0]-PA[0])**2 + (PB[1]-PA[1])**2)
        distance += AB_dist
        if distance > tesselation_degrees:
            distance = 0
            AB_norm = (PB - PA)/AB_dist
            AB_perpendicular = np.array([AB_norm[1], -AB_norm[0]]) # perpendicular to line A->B
            B0 = PA + triangle_base_length*AB_norm #new B
            C0 = PA + 0.5*triangle_base_length*AB_norm #middle point between A and B
            # project point along normal vector
            C = C0 + triangle_base_length*triangle_aspect*AB_perpendicular
            teeth.append([PA,B0,C])#three vertices of the triagle

        PA = PB
    return teeth

def get_subduction_geometries(subduction_geoms, shared_boundary_sections):
    for shared_boundary_section in shared_boundary_sections:
        if shared_boundary_section.get_feature().get_feature_type() != pygplates.FeatureType.gpml_subduction_zone:
                continue
        for shared_sub_segment in shared_boundary_section.get_shared_sub_segments():
            subduction_polarity = shared_sub_segment.get_feature().get_enumeration(pygplates.PropertyName.gpml_subduction_polarity)
            if subduction_polarity == "Left":
                subduction_geoms.append((shared_sub_segment.get_resolved_geometry(),-1))
            else:
                subduction_geoms.append((shared_sub_segment.get_resolved_geometry(),1))
    return 

def download_agegrid(time):
    if not os.path.isdir('./AgeGrids'):
        os.system('mkdir AgeGrids')

    # download the age grid if necessary
    url_temp='https://www.earthbyte.org/webdav/ftp/Data_Collections/Muller_etal_2016_AREPS/Muller_etal_2016_AREPS_Agegrids/Muller_etal_2016_AREPS_Agegrids_v1.15/netCDF-4_0-230Ma/EarthByte_AREPS_v1.15_Muller_etal_2016_AgeGrid-{}.nc'
    file_temp='./AgeGrids/EarthByte_AREPS_v1.15_Muller_etal_2016_AgeGrid-{}.nc'
    agegrid_file = file_temp.format(time)
    print('Downloading age grids...')
    if not os.path.isfile(agegrid_file):
        myfile = requests.get(url_temp.format(time))
        open(agegrid_file, 'wb').write(myfile.content)
    return agegrid_file
 