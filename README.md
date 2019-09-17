### Rotation Model and Age Grids:

The old AREPS plate model has some serious bugs which have been fixed in version 1.15.  

The v1.15 age grids can be found here https://www.earthbyte.org/webdav/ftp/Data_Collections/Muller_etal_2016_AREPS/Muller_etal_2016_AREPS_Agegrids/Muller_etal_2016_AREPS_Agegrids_v1.15/.

The v1.15 rotation model is here https://www.earthbyte.org/webdav/ftp/Data_Collections/Muller_etal_2016_AREPS/Muller_etal_2016_AREPS_Supplement/Muller_etal_2016_AREPS_Supplement_v1.15/

### Dependencies:

pygplates -- https://www.gplates.org/download.html

scikit-learn -- https://scikit-learn.org/stable/

scipy -- https://www.scipy.org/

matplotlib -- https://matplotlib.org/

pyshp -- https://pypi.org/project/pyshp/

numpy -- https://numpy.org/

jupyter notebooks -- https://jupyter.org/

cartopy -- https://scitools.org.uk/cartopy/docs/latest/

pandas -- https://pandas.pydata.org/

netCDF4 -- https://github.com/Unidata/netcdf4-python

EarthByte/PlateTectonicTools -- https://github.com/EarthByte/PlateTectonicTools.git. Edit "plate_tectonic_tools_path" parameter in python/parameters.py to specify the location of PlateTectonicTools code.

### Step 1:

Run "python convergence.py 2>log"

### Additional step:

Run extract_earth_chem.py to extract interesting data from EarthChem data. Run "python extract_earth_chem.py -h" to see 
how to use the script.

### Step 2:

Run "python coregistration.py"

### Step 3:

Start Jupyter Notebook and open and run machine_learning.ipynb
