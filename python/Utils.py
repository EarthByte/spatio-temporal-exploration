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
