
parameters = {
    "plate_tectonic_tools_path" : "../../PlateTectonicTools/ptt/",
    "time" : {
        "start" : 0,
        "end"   : 20,
        "step"  : 10
    },
    "rotation_files" : ["../data/Global_EarthByte_230-0Ma_GK07_AREPS.rot"],
    "topology_files" : ["../data/Global_EarthByte_230-0Ma_GK07_AREPS_PlateBoundaries.gpml.gz",  
            "../data/Global_EarthByte_230-0Ma_GK07_AREPS_Topology_BuildingBlocks.gpml.gz"],
    "threshold_sampling_distance_degrees" : 0.2,
    "velocity_delta_time" : 1,
    "convergence_data_filename_prefix" : "conv_data",
    "convergence_data_filename_ext" : "csv",
    "result_dir" : "./convergence_data",
    "anchor_plate_id" : 0

}
