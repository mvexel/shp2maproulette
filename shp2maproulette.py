#!/usr/bin/env python

import shapefile
import shapeinfo
# import simplejson as json

SHAPEFILE='/Users/martijnv/tmp/crossings/shape/crossings.shp'
CHALLENGE_SLUG='test_challenge'
SERVER='http://dev.maproulette.org'

shapefile_reader = shapefile.Reader(SHAPEFILE)
shapes = shapefile_reader.shapes()
shapetype = shapes[0].shapeType
print 'OK, read in {} features.'.format(
    len(shapes))
print 'Looks like we are dealing with {}'.format(
    shapeinfo.shapetypes[str(shapetype)].lower() + 's')
for shape_record in shapefile_reader.iterShapeRecords():
    print shape_record.shape.__geo_interface__
    print shape_record.record