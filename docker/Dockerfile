# To build this docker file
# do the following in the "docker" folder (the folder contains this Dockerfile)
# git clone https://github.com/EarthByte/PlateTectonicTools.git
# download https://www.earthbyte.org/webdav/ftp/earthbyte/EarthChem/EarthChem_all.csv
# download mrds.csv from https://mrdata.usgs.gov/mrds/mrds-csv.zip
# docker build -t pyg .

# To run this, with an interactive shell temrinal, mounting your current host directory in the container directory at /workspace use:
# docker run -it --rm -v`pwd`:/workspace pyg /bin/bash

# To run a jupyter notebook server with the python conda environement
# docker run -p 8888:8888 -it --rm -v`pwd`:/workspace pyg /bin/bash -c "source activate pyGEOL && jupyter notebook --allow-root --ip=0.0.0.0 --no-browser"

# Pull base image.
FROM ubuntu:bionic
MAINTAINER Nathaniel Butterworth

#Create some directories to work with
WORKDIR /build
RUN mkdir /workspace 

#Install ubuntu libraires and packages
RUN apt-get update -y
RUN apt-get install -y wget

#Download conda python because I like it
RUN wget -O ~/miniconda.sh https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh  && \
     chmod +x ~/miniconda.sh && \
     ~/miniconda.sh -b -p /opt/conda && \
     rm ~/miniconda.sh 
     
RUN /opt/conda/bin/conda create -n pyGEOL python=3.7 scipy scikit-learn matplotlib pyshp numpy jupyter cartopy pandas notebook netCDF4 opencv

#Download pygplates and install it
ADD pygplates_2.0_amd64.deb .
RUN apt-get install -y ./pygplates_2.0_amd64.deb
RUN rm pygplates_2.0_amd64.deb

RUN apt-get install -y git
RUN git clone https://github.com/EarthByte/PlateTectonicTools.git /PlateTectonicTools

RUN apt-get install -y unzip
RUN mkdir /data
RUN wget -P /data https://www.earthbyte.org/webdav/ftp/earthbyte/EarthChem/EarthChem_all.csv
RUN wget -P /data https://mrdata.usgs.gov/mrds/mrds-csv.zip
RUN unzip /data/mrds-csv.zip -d /data
RUN rm /data/mrds-csv.zip


#Make the workspace persistant
VOLUME /workspace
WORKDIR /workspace
EXPOSE 8888

#Set the path so python can find pygplates
ENV PYTHONPATH ${PYTHONPATH}:/usr/lib:/usr/lib/pygplates/revision26/:/PlateTectonicTools/ptt/
ENV PATH "/opt/conda/bin:$PATH"

RUN ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh



