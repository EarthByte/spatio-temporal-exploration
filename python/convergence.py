from parameters import parameters as p
import pprint, sys, math
sys.path.append(p["plate_tectonic_tools_path"])
from subduction_convergence import subduction_convergence
import numpy as np
 
if __name__ == '__main__':
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(p)    

    for time in range(p["time"]["start"], p["time"]["end"], p["time"]["step"]):
        print(time)
        ret = subduction_convergence(
            p["rotation_files"],
            p["topology_files"],
            math.radians(p["threshold_sampling_distance_degrees"]),
            p["velocity_delta_time"],
            anchor_plate_id = 0
        )
        print(np.array(ret).shape)
        
#parameters["convergence_data_filename_prefix"],
#parameters["convergence_data_filename_ext"],

