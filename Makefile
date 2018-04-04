all: chunks

clean:
	rm -rf source
	rm -rf chunks
	rm -rf chunks-osm
	rm -rf chunks-duplicates-osm
	rm -rf qa

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

chunks-deduplicated: chunks
	mkdir -p chunks-deduplicated
	mkdir -p chunks-duplicates
	for f in chunks/*/*.geojson; do \
		OUTPUTFILE=`echo $$f | sed -e 's/chunks/chunks-deduplicated/'`; \
		mkdir -p `dirname $$OUTPUTFILE`; \
		OUTPUTFILE_DUP=`echo $$f | sed -e 's/chunks/chunks-duplicates/'`; \
		mkdir -p `dirname $$OUTPUTFILE_DUP`; \
		python tools/remove-duplicates.py $$f $$OUTPUTFILE $$OUTPUTFILE_DUP; \
	done

chunks-osm: chunks-deduplicated
	mkdir -p chunks-osm
	for f in chunks-deduplicated/*/*.geojson; do \
		OUTPUTFILE=`echo $$f | sed -e 's/chunks-deduplicated/chunks-osm/' | sed -e 's/.geojson/.osm/'`; \
		mkdir -p `dirname $$OUTPUTFILE`; \
		python tools/ogr2osm.py --output $$OUTPUTFILE --translation usfs_trails $$f; \
	done

#QA
chunks-duplicates-osm: chunks-deduplicated
	mkdir -p chunks-duplicates-osm
	for f in chunks-duplicates/*/*.geojson; do \
		OUTPUTFILE=`echo $$f | sed -e 's/chunks-duplicates/chunks-duplicates-osm/' | sed -e 's/.geojson/.osm/'`; \
		mkdir -p `dirname $$OUTPUTFILE`; \
		python tools/ogr2osm.py --output $$OUTPUTFILE --translation usfs_trails $$f; \
	done

qa/new.geojson: chunks-osm
	mkdir -p qa
	for f in chunks-osm/*/*.osm; do \
		OSM_USE_CUSTOM_INDEXING=NO OSM_CONFIG_FILE=osm2ogr.conf ogr2ogr \
			-sql "select * from lines"\
			-f SQLite -dsco SPATIALITE=YES -append qa/new.sqlite $$f; \
	done
	ogr2ogr -f GeoJSON qa/new.geojson qa/new.sqlite

qa/duplicates.geojson: chunks-duplicates-osm
	mkdir -p qa
	for f in chunks-duplicates-osm/*/*.osm; do \
		OSM_USE_CUSTOM_INDEXING=NO OSM_CONFIG_FILE=osm2ogr.conf ogr2ogr \
			-sql "select * from lines"\
			-f SQLite -dsco SPATIALITE=YES -append qa/duplicates.sqlite $$f; \
	done
	ogr2ogr -f GeoJSON qa/duplicates.geojson qa/duplicates.sqlite

qa/combined.mbtiles: qa/new.geojson qa/duplicates.geojson	
	tippecanoe --maximum-zoom=14 --minimum-zoom=5 -o qa/combined.mbtiles qa/new.geojson qa/duplicates.geojson
