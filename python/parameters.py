
parameters = {
    "plate_tectonic_tools_path" : "../../PlateTectonicTools/ptt/",
    "time" : {
        "start" : 0,
        "end"   : 230,
        "step"  : 1
    },
    "region_1" : 5,
    "region_2" : 10,
    "rotation_files" : ["../data/Global_EarthByte_230-0Ma_GK07_AREPS.rot"],
    "topology_files" : ["../data/Global_EarthByte_230-0Ma_GK07_AREPS_PlateBoundaries.gpml.gz",  
            "../data/Global_EarthByte_230-0Ma_GK07_AREPS_Topology_BuildingBlocks.gpml.gz"],
    "threshold_sampling_distance_degrees" : 0.2,
    "velocity_delta_time" : 1,
    "convergence_data_filename_prefix" : "subStats",
    "convergence_data_filename_ext" : "csv",
    "convergence_data_dir" : "./convergence_data/",
    "anchor_plate_id" : 0,
    "age_grid_dir" : '../data/AgeGrids/',
    "age_grid_prefix" : 'EarthByte_AREPS_v1.15_Muller_etal_2016_AgeGrid-',
    "age_grid_url_prefix" : 'https://www.earthbyte.org/webdav/ftp/Data_Collections/Muller_etal_2016_AREPS/' +                
            'Muller_etal_2016_AREPS_Agegrids/Muller_etal_2016_AREPS_Agegrids_v1.15/netCDF-4_0-230Ma/' +
             'EarthByte_AREPS_v1.15_Muller_etal_2016_AgeGrid-',
    "andes_data" : '../data/CopperDeposits/XYBer14_t2_ANDES.shp'
}
