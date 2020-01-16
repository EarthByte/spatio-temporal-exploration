import numpy as np
import shapefile
from parameters import parameters as param

# the age is a floating-point number. map the floating-point number to the nereast integer time in the range
def get_time_from_age(ages, start, end, step):
    ret=[]
    times=range(start, end+1, step)
    for age in ages:
        age=float(age)
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

start_time = param["time"]["start"]
end_time = param["time"]["end"]
time_step =  param["time"]["step"]

#load files
f = np.loadtxt('./convergence_data/subStats_0.00.csv') #all subduction points at time 0
trench_points=f[(f[:,9])==201] #subduction points in south america TODO:make this more general

reader = shapefile.Reader('../data/CopperDeposits/XYBer14_t2_ANDES.shp')
recs    = reader.records()
andes_points_len = len(recs)
randomAges=np.random.randint(start_time+1, end_time, size=andes_points_len) #generate random ages for andes data
times = get_time_from_age(np.array(recs)[:,6], start_time, end_time, time_step)#get integer ages for andes data

#index, lon, lat, time, plate id
data=[]

# fill the andes deposit points with the real age
for i in range(andes_points_len):
    data.append([i, recs[i][3], recs[i][4], times[i], recs[i][7]])

points_with_age_size=i+1

# fill andes deposit points with random ages
for i in range(andes_points_len): 
    data.append([points_with_age_size+i, recs[i][3], recs[i][4], randomAges[i], recs[i][7] ])
    
points_with_random_age_size=i+1

# fill trench points for each time step from start_time to end_time
start_idx = points_with_age_size + points_with_random_age_size
i=0
for p in trench_points:
    for t in range(end_time):
        data.append([start_idx+i, p[0], p[1], t, 201]) 
        i+=1

with open('input_data_example.csv',"w+") as f:
    for row in data:
        if row:
            f.write('{0:d}, {1:.2f}, {2:.2f}, {3:d}, {4:d}'.format(row[0],row[1],row[2],row[3],row[4]))
        f.write('\n')

print('done!')
