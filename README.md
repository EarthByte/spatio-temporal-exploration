### Getting started

#### Step 1: Setup runtime environment. Use Docker or install the dependencies in your computer.

#### Step 2: Open **python/workflow.ipynb** and follow the instructions inside.

### Docker

The easist way to run the workflow.ipynb is use docker.

#### step 1: go into docker folder and run 
`docker build -t pyg .`

#### step 2: 
docker run -p 8888:8888 -it --rm -v\`pwd\`:/workspace pyg /bin/bash -c "source activate pyGEOL && jupyter notebook --allow-root --ip=0.0.0.0 --no-browser" 

(IMPORTANT!!! run this command in the root directory of this repository)

#### step 3: in web browser, go to http://127.0.0.1:8888

### Dependencies:

If you would like to setup the runtime environment on your computer, you need to install the following dependencies in Python3.

For example, you can create a conda enviroment with the command below

`conda create -n pyGEOL python=3.7 scipy scikit-learn matplotlib pyshp numpy jupyter cartopy pandas notebook netCDF4 opencv`

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

opencv -- https://opencv.org/

EarthByte/PlateTectonicTools -- https://github.com/EarthByte/PlateTectonicTools.git. Edit "plate_tectonic_tools_path" parameter in python/parameters.py to specify the location of PlateTectonicTools code.

### Rotation Model and Age Grids:

The old AREPS plate model has some serious bugs which have been fixed in version 1.15.  

The v1.15 age grids can be found here https://www.earthbyte.org/webdav/ftp/Data_Collections/Muller_etal_2016_AREPS/Muller_etal_2016_AREPS_Agegrids/Muller_etal_2016_AREPS_Agegrids_v1.15/.

The v1.15 rotation model is here https://www.earthbyte.org/webdav/ftp/Data_Collections/Muller_etal_2016_AREPS/Muller_etal_2016_AREPS_Supplement/Muller_etal_2016_AREPS_Supplement_v1.15/


### FAQ
#### Why am I getting an error "ImportError: No module named subduction_convergence"?
Answer: The code you are trying to run depends on EarthByte/PlateTectonicTools -- https://github.com/EarthByte/PlateTectonicTools.git. You need to download the PlateTectonicTools code and edit the "plate_tectonic_tools_path" parameter in python/parameters.py to tell the code where to find the PlateTectonicTools code.
