all: chunks

clean:
	rm -rf source
	rm -rf chunks
	rm -rf osm

source/S_USA.TrailNFS_Publish.zip: directories
	curl -L https://data.fs.usda.gov/geodata/edw/edw_resources/shp/S_USA.TrailNFS_Publish.zip -o source/S_USA.TrailNFS_Publish.zip

source/S_USA.TrailNFS_Publish: source/S_USA.TrailNFS_Publish.zip
	rm -rf source/S_USA.TrailNFS_Publish
	unzip source/S_USA.TrailNFS_Publish.zip -d source/S_USA.TrailNFS_Publish

chunks: source/S_USA.TrailNFS_Publish
	rm -rf chunks

directories:
	mkdir -p source
	mkdir -p chunks
	mkdir -p osm
