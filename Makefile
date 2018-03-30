all: chunks

clean:
	rm -rf source
	rm -rf chunks
	rm -rf chunks-osm

# Trail data
source/S_USA.TrailNFS_Publish.zip:
	mkdir -p source
	curl -L https://data.fs.usda.gov/geodata/edw/edw_resources/shp/S_USA.TrailNFS_Publish.zip -o source/S_USA.TrailNFS_Publish.zip

source/S_USA.TrailNFS_Publish: source/S_USA.TrailNFS_Publish.zip
	unzip source/S_USA.TrailNFS_Publish.zip -d source/S_USA.TrailNFS_Publish

source/trails.geojson: source/S_USA.TrailNFS_Publish
	ogr2ogr -t_srs EPSG:4326 -f GeoJSON \
    	-progress \
    	source/trails.geojson source/S_USA.TrailNFS_Publish/S_USA.TrailNFS_Publish.shp

#Ranger district boundaries
source/S_USA.RangerDistrict.zip:
	mkdir -p source
	curl -L https://data.fs.usda.gov/geodata/edw/edw_resources/shp/S_USA.RangerDistrict.zip -o source/S_USA.RangerDistrict.zip

source/S_USA.RangerDistrict: source/S_USA.RangerDistrict.zip
	unzip source/S_USA.RangerDistrict.zip -d source/S_USA.RangerDistrict

source/ranger_districts.geojson: source/S_USA.RangerDistrict
	ogr2ogr -t_srs EPSG:4326 -f GeoJSON \
    	-progress \
    	source/ranger_districts.geojson source/S_USA.RangerDistrict/S_USA.RangerDistrict.shp

# Processing data
chunks: source/trails.geojson source/ranger_districts.geojson
	mkdir -p chunks
	python tools/split.py source/trails.geojson source/ranger_districts.geojson chunks

chunks-osm: chunks
	mkdir -p chunks-osm
	for f in chunks/*/*.geojson; do \
		OUTPUTFILE=`echo $$f | sed -e 's/chunks/chunks-osm/' | sed -e 's/.geojson/.osm/'`; \
		mkdir -p `dirname $$OUTPUTFILE`; \
		python tools/ogr2osm.py --output $$OUTPUTFILE --translation usfs_trails $$f; \
	done
