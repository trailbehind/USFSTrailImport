#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from optparse import OptionParser
import os
import fiona
from shapely.geometry import mapping, shape
from shapely.prepared import prep
from rtree import index

trail_limit = None
def split_trails(trails_path, regions_path, dest):
    region_geometries = {}
    region_properties = {}
    region_index = index.Index()
    logging.info("Loading ranger districts")
    with fiona.open(regions_path, 'r') as regions:
        logging.info("Processing ranger districts")
        for r in regions:
            r_id = int(r['id'])
            region_properties[r_id] = r['properties']
            geometry = shape(r['geometry'])
            region_geometries[r_id] = prep(geometry)
            region_index.insert(r_id, geometry.bounds)

    region_trails = {}
    logging.info("Loading trails")
    trail_count = 0
    no_geometry_count = 0
    no_region_count = 0
    with fiona.open(trails_path, 'r') as trails:
        trails_schema = trails.schema.copy()
        logging.info("Processing trails")
        for t in trails:
            if t['geometry'] is None:
                no_geometry_count += 1
                logging.debug("Trail has null geometry" + str(t))
                continue

            trail_geometry = shape(t['geometry'])
            intersecting_regions = region_index.intersection(trail_geometry.bounds)
            trail_region = None
            for region_id in intersecting_regions:
                region_geometry = region_geometries[region_id]
                if region_geometry.intersects(trail_geometry):
                    trail_region = region_id
                    logging.debug("Found region for trail")
                    break

            if trail_region is None:
                no_region_count += 1
                logging.debug("Could not find region for trail:" + str(t))
                nearest_regions = list(region_index.nearest(trail_geometry.bounds, 1))
                if len(nearest_regions):
                    trail_region = nearest_regions[0]

            if trail_region is not None:
                if not region_id in region_trails:
                    region_trails[region_id] = []
                if t['geometry']['type'] == "LineString":
                    region_trails[region_id].append(t)
                elif t['geometry']['type'] == "MultiLineString":
                    for line in t['geometry']['coordinates']:
                        region_trails[region_id].append({
                            "properties": t["properties"],
                            "geometry": {
                                "type": "LineString",
                                "coordinates": line
                            }
                        })
                else:
                    logging.error("Unexpected geometry type:" + t['geometry']['type'])
            trail_count += 1
            if trail_limit and trail_count > trail_limit:
                break

    logging.info("Loaded %i trails" % (trail_count,))
    logging.info("%d trails had no geometry" % no_geometry_count)
    logging.info("%d trails did not intersect a region" % no_region_count)

    logging.info("Writing trails")
    for region_id, trails in region_trails.iteritems():
        region = region_properties[region_id]
        forest_name = region['FORESTNAME'].lower().replace(" ", "_").replace(",", "").replace("/", "_")
        directory = os.path.join(dest, forest_name)
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = region['DISTRICTNA'].lower().replace(" ", "_").replace(",", "").replace("/", "_") + '.geojson'
        file_path = os.path.join(directory, filename)
        logging.info("Writing %d trails for region %s/%s" % (len(trails), region['FORESTNAME'], region['DISTRICTNA']))
        with fiona.open(file_path, "w", "GeoJSON", trails_schema) as output:
            for trail in trails:
                output.write(trail)


def _main():
    usage = "usage: %prog trails.geojson rangerdistricts.geojson chunks"
    parser = OptionParser(usage=usage, description="")
    parser.add_option("-d", "--debug", action="store_true", dest="debug",
                      help="Turn on debug logging")
    parser.add_option("-q", "--quiet", action="store_true", dest="quiet",
                      help="turn off all logging")
    (options, args) = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if options.debug else
    (logging.ERROR if options.quiet else logging.INFO))
    logging.getLogger('shapely.geos').setLevel(logging.ERROR)
    logging.getLogger('Fiona').setLevel(logging.ERROR)

    trails, regions, dest = args
    if not os.path.exists(dest):
        logging.debug("Creating output directory: " + dest)
        os.makedirs(dest)

    split_trails(trails, regions, dest)


if __name__ == "__main__":
    _main()
