#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from optparse import OptionParser
import os
import sys
from fiona import collection
import requests
import polyline
import json
from shapely.geometry import LineString

ROUTING_SERVER_URL = "http://localhost:8002"

def check_duplicate(feature, retries=0):
    trace_route_url = ROUTING_SERVER_URL + "/trace_route"

    params = {}
    params['encoded_polyline'] = polyline.encode(
        [(y, x) for x,y in feature['geometry']['coordinates']], 
        precision=6)
    params['costing'] = "pedestrian"
    params['shape_match'] = "map_snap"
    params['search_radius'] = 10
    try:
        r1 = requests.post(trace_route_url, data=json.dumps(params), timeout=30)
    except:
        if retries <= 2:
            logging.exception("Routing request failed, retrying. request:%s retries:%d" % 
                (json.dumps(params), retries))
            return check_duplicate(feature, retries=retries + 1)
        else:
            logging.error("Too many retries, giving up on request")
            logging.error("curl -X POST -H 'Content-Type: application/json' -d '%s' %s" % 
                (json.dumps(params), trace_route_url))
            logging.error(json.dumps(feature))
            return False

    response = r1.json()
    if 'error_code' in response:
        logging.debug("no route found")
        return False
    
    input_geometry = LineString(feature['geometry']['coordinates'])

    coordinates = []
    for leg in response['trip']['legs']:
        coordinates.extend(polyline.decode(leg['shape'], precision=6))
    coordinates = [(x, y) for y,x in coordinates]
    output_geometry = LineString(coordinates)

    input_length = input_geometry.length
    output_length = output_geometry.length
    if abs(1 - (output_length/input_length)) > .1:
        logging.debug("Distances dont match %f -> %f" % (input_length, output_length))
        return False

    return True


def remove_duplicates(input_path, output_path, output_path_duplicates):
    duplicate_count = 0
    non_duplicate_count = 0
    logging.info("Opening input " + input_path)
    with collection(input_path, "r") as inputFile:
        logging.info("Opening output " + output_path)
        with collection(output_path, "w", "GeoJSON", inputFile.schema.copy()) as nonduplicates:
            with collection(output_path_duplicates, "w", "GeoJSON", inputFile.schema.copy()) as duplicates:
                for feature in inputFile:
                    if not check_duplicate(feature):
                        logging.debug("Not a duplicate:" + str(feature))
                        non_duplicate_count += 1
                        nonduplicates.write(feature)
                    else:
                        logging.debug("Duplicate:" + str(feature))
                        duplicate_count += 1
                        duplicates.write(feature)
    logging.info("Finished, with %d duplicates, %d non-duplicates" % (duplicate_count, non_duplicate_count))


def _main():
    usage = "usage: %prog input.geojson output.geojson"
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

    input_path, output_path, duplicates = args
    if not os.path.exists(input_path):
        logging.error("Input file does not exist")
        sys.exit(-1)
    if os.path.exists(output_path):
        logging.error("Output file already exists")
        sys.exit(-1)
    if os.path.exists(duplicates):
        logging.error("Output file already exists")
        sys.exit(-1)

    remove_duplicates(input_path, output_path, duplicates)


if __name__ == "__main__":
    _main()
