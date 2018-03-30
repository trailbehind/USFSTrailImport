'''
A translation function for USFS trails. https://data.fs.usda.gov/geodata/edw/edw_resources/meta/S_USA.TrailNFS_Publish.xml 

'''


from osgeo import ogr
import re
import urllib
import json


def filterFeature(ogrfeature, fieldNames, reproject):
    if ogrfeature is None:
        return
    trailType = ogrfeature.GetFieldAsString("TRAIL_TYPE")
    if trailType == "TERRA":
        return ogrfeature
    else:
        return

    
def filterTags(attrs):
    if not attrs:
        return

    tags = {}
    tags['highway'] = 'path'

    if 'TRAIL_NO' in attrs:
        tags['ref'] = attrs['TRAIL_NO']#[1:] # this is necesary to make trail numbers match usgs maps, at least in MT/ID
    if 'TRAIL_NAME' in attrs:
        tags['name'] = attrs['TRAIL_NAME'].lower().title()\
        .replace("Nst", "NST")\
        .replace("Nht", "NHT")
    """
Attribute Label: NATIONAL_TRAIL_DESIGNATION
Attribute Definition: The national designation assigned to the trail or trail segment. This includes designations by federal statute for National Historic Trails (NHT), National Scenic Trails (NST), Connecting or Side Trails (C-S), and National Recreation Trails (NRT); and also includes National Millennium Trails (NMT) and Millennium Legacy Trails (MLT).
Attribute Definition Source: U.S. Forest Service
Attribute Domain Values:
Enumerated Domain:
Enumerated Domain Value: 0
Enumerated Domain Value Definition: Not populated for this attribute subset level
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: 1
Enumerated Domain Value Definition: Not designated as a National Trail
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: 2
Enumerated Domain Value Definition: All other National Trails
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: 3
Enumerated Domain Value Definition: National Scenic or National Historic Trail
Enumerated Domain Value Definition Source: U.S. Forest Service
    """
    if 'NATIONAL_T' in attrs:
        pass
    """
Attribute Label: TRAIL_CLASS
Attribute Definition: The prescribed scale of development for a trail, representing its intended design and management standards (TC 1 - 5)
Attribute Definition Source: U.S. Forest Service
Attribute Domain Values:
Enumerated Domain:
Enumerated Domain Value: 1
Enumerated Domain Value Definition: Minimally developed
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: 2
Enumerated Domain Value Definition: Moderately developed
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: 3
Enumerated Domain Value Definition: Developed
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: 4
Enumerated Domain Value Definition: Highly developed
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: 5
Enumerated Domain Value Definition: Fully developed
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: N
Enumerated Domain Value Definition: Not populated in this Attribute Subset
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: NULL
Enumerated Domain Value Definition: Not recorded for this trail segment.
Enumerated Domain Value Definition Source: U.S. Forest Service
    """
    if 'TRAIL_CLAS' in attrs:
        pass
    """
Attribute Label: TRAIL_SURFACE
Attribute Definition: The predominant surface type the user would expect to encounter on the trail or trail segment.
Attribute Definition Source: U.S. Forest Service
Attribute Domain Values:
Enumerated Domain Value: IMPORTED COMPACTED MATERIAL
Enumerated Domain Value Definition: Imported material such as gravel surface
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: NULL
Enumerated Domain Value Definition: Not recorded
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: N/A
Enumerated Domain Value Definition: Not populated for this Attribute Subset
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: AC- ASPHALT
Enumerated Domain Value Definition: Asphalt surface
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: NAT - NATIVE MATERIAL
Enumerated Domain Value Definition: Native material surface
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: SNOW
Enumerated Domain Value Definition: Snow surface
Enumerated Domain Value Definition Source: U.S. Forest Service
    """
    if 'TRAIL_SURF' in attrs:
        if attrs['TRAIL_SURF'] == "IMPORTED COMPACTED MATERIAL":
            tags['surface'] = "gravel"
        elif attrs['TRAIL_SURF'] == "AC- ASPHALT":
            tags['surface'] = "asphalt"
        elif attrs['TRAIL_SURF'] == "NAT - NATIVE MATERIAL":
            tags['surface'] = "ground"
    """
Attribute Label: SURFACE_FIRMNESS
Attribute Definition: The firmness characteristics of the surface that the user would generally expect to encounter on the trail or trail segment.
Attribute Definition Source: U.S. Forest Service
Attribute Domain Values:
Enumerated Domain:
Enumerated Domain Value: N/A
Enumerated Domain Value Definition: Not populated for this Attribute Subset
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: NULL
Enumerated Domain Value Definition: Not recorded
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: VS - VERY SOFT
Enumerated Domain Value Definition: Trail surface is generally very soft
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: S - SOFT
Enumerated Domain Value Definition: Trail surface is generally soft
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: P - PAVED
Enumerated Domain Value Definition: Trail surface is paved
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: F - FIRM
Enumerated Domain Value Definition: Trail surface is generally firm
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: H - HARD
Enumerated Domain Value Definition: Trail surface is generally hard.
Enumerated Domain Value Definition Source: U.S. Forest Service
    """
    if 'SURFACE_FI' in attrs:
        pass
    """
Attribute Label: TYPICAL_TREAD_WIDTH
Attribute Definition: The average tread width the user can generally expect on the section of trail.
Attribute Definition Source: U.S. Forest Service
Attribute Domain Values:
Unrepresentable Domain: Code describes the typical trail tread width in inches. For example the code "< 6 INCHES" indicates that the tread width is less than 6 inches, "10 INCHES" indicates the tread width is about 10 inches, and "> 42 INCHES" indicates the tread width is generally wider than 42 inches. "N/A" indicates the attribute is not populated for this Attribute Subtype and blank indicates the value has not been recorded for this trail segment.
    """
    if 'TYPICAL_TR' in attrs:
        pass
    """
Attribute Label: MINIMUM_TRAIL_WIDTH
Attribute Definition: The minimum trail width on the trail segment where passage may be physically restricted and no alternative route is readily available.
Attribute Definition Source: U.S. Forest Service
Attribute Domain Values:
Unrepresentable Domain: Code describes the minimum trail width in inches. For example the code "< 6 INCHES" indicates that the width is less than 6 inches in some places; "10 INCHES" indicates the minimum trail width is about 10 inches, and "> 42 INCHES" indicates the minimum trail width is generally wider than 42 inches. "N/A" indicates the attribute is not populated for this Attribute Subtype and blank indicates the value has not been recorded for this trail segment.
    """
    if 'MINIMUM_TR' in attrs:
        pass
    """
Attribute Label: TERRA_MOTORIZED
Attribute Definition: This field supports basic display of motorized and non-motorized TERRA trails:
Attribute Definition Source: U.S. Forest Service
Attribute Domain Values:
Enumerated Domain:
Enumerated Domain Value: X
Enumerated Domain Value Definition: Not populated for this Attribute Subset
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: NULL
Enumerated Domain Value Definition: Not recorded
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: N
Enumerated Domain Value Definition: Designated as closed to all motorized uses year-round.
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: Y
Enumerated Domain Value Definition: Designated as open to one or more motorized uses, year-round or seasonally
Enumerated Domain Value Definition Source: U.S. Forest Service
    """
    if 'TERRA_MOTO' in attrs:
        pass
    """
Attribute Label: ALLOWED_TERRA_USE
Attribute Definition: Indicates uses on TERRA Trails that are legally allowed on the trail (e.g. "Where can I take my...?" Formed by concatenating the value for each allowable use. (e.g. 12 states that use 1 and 2 are both allowed.)
Attribute Definition Source: U.S. Forest Service
Attribute Domain Values:
Enumerated Domain:
Enumerated Domain Value: 1
Enumerated Domain Value Definition: Hiker/Pedestrian
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: 2
Enumerated Domain Value Definition: pack and saddle
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: 3
Enumerated Domain Value Definition: Bicycle
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: 4
Enumerated Domain Value Definition: Motorcycle
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: 5
Enumerated Domain Value Definition: ATV
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: 6
Enumerated Domain Value Definition: 4WD>50"
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: N/A
Enumerated Domain Value Definition: Not populated for this Attribute Subset
Enumerated Domain Value Definition Source: U.S. Forest Service
Enumerated Domain:
Enumerated Domain Value: NULL
Enumerated Domain Value Definition: Not recorded
Enumerated Domain Value Definition Source: U.S. Forest Service
    """
    if 'ALLOWED_TE' in attrs:
        values = attrs['ALLOWED_TE']
        tags['foot'] = 'yes' if '1' in values else 'no'
        tags['horse'] = 'yes' if '2' in values else 'no'
        tags['bicycle'] = 'yes' if '3' in values else 'no'
        tags['motorcyle'] = 'yes' if '4' in values else 'no'
        tags['atv'] = 'yes' if '5' in values else 'no'
        if '6' in values:
            tags['motor_vehicle'] = 'yes'
            tags['highway'] = 'track'
        else:
            tags['motor_vehicle'] = 'no'

    return tags
