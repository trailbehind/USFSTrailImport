# USFS Trails import
Coordinating USFS Trail data import into OpenStreetMap


### Why are we doing this?

### Where is the data from
Source data: https://data.fs.usda.gov/geodata/edw/edw_resources/shp/S_USA.TrailNFS_Publish.zip

Source Metadata: https://data.fs.usda.gov/geodata/edw/edw_resources/meta/S_USA.TrailNFS_Publish.xml 


### More on this project
These scripts generate an OSM file of trails per USFS ranger district,
ready to be used in JOSM for a manual review and upload to OpenStreetMap. This repository is based heavily on the [LA building import](https://github.com/osmlab/labuildings)

This README is about data conversion. See also the [page on the OSM wiki](https://wiki.openstreetmap.org/wiki/).

Sample .osm files (**not ready for import yet**) are in this [zip file](https://github.com/JesseCrocker/USFSTrailImport/raw/master/samples/selway/transform.osm.zip).

Browse a slippy map of the data [here]()


## Prerequisites

    Python 2.7.x
    pip
    virtualenv
    libxml2
    libxslt
    spatialindex
    GDAL

### Installing prerequisites on Mac OSX

    # install brew http://brew.sh

    brew install libxml2
    brew install libxslt
    brew install spatialindex
    brew install gdal

### Installing prerequisites on Ubuntu

    apt-get install python-pip
    apt-get install python-virtualenv
    apt-get install gdal-bin
    apt-get install libgdal-dev
    apt-get install libxml2-dev
    apt-get install libxslt-dev
    apt-get install python-lxml
    apt-get install python-dev
    apt-get install libspatialindex-dev
    apt-get install unzip

## Set up Python virtualenv and get dependencies
    # may need to easy_install pip and pip install virtualenv
    virtualenv ~/venvs/usfstrails
    source ~/venvs/usfstrails/bin/activate
    pip install -r requirements.txt



## Usage

Run all stages:

    # Download all files and process them a .osm file per ranger district.
    make

You can run stages separately, like so:

    # Download and expand all files, reproject
    make download

    # Chunk data by ranger district.
    make chunks

    # Generate importable .osm files.
    # This will populate the osm/ directory with one .osm file per
    # ranger district.
    make osm

    # Clean up all intermediary files:
    make clean

## Features



## Attribute mapping

See the [ogr2osm translation script](https://github.com/JesseCrocker/ogr2osm-translations/blob/usfs-trails/usfs_trails.py) to see the implementation of these transformations.
