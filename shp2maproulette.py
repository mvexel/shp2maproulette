#!/usr/bin/env python

import shapefile
import shapeinfo
from maproulette import MapRouletteServer, MapRouletteChallenge, MapRouletteTask, MapRouletteTaskCollection
from geojson import FeatureCollection, Feature
import sys
from fish import ProgressFish

SHAPEFILE='/Users/martijnv/tmp/crossings/shape/crossings.shp'
CHALLENGE_SLUG='fix-railway-crossings'
CHALLENGE_TITLE='Fix U.S. railway crossings'

row_count = 0
tasks_created=0
tasks_updated=0

server = MapRouletteServer()
challenge = None
challenge = MapRouletteChallenge(
	slug=CHALLENGE_SLUG,
	title=CHALLENGE_TITLE,
	active=True)
if challenge.exists(server):
	print 'updating challenge...'
	challenge.update(server)
else:
	print 'creating challenge...'
	challenge.create(server)

collection = MapRouletteTaskCollection(
	challenge)

shapefile_reader = shapefile.Reader(SHAPEFILE)
shapes = shapefile_reader.shapes()
shapetype = shapes[0].shapeType
print 'OK, read in {} features.'.format(
    len(shapes))
fish = ProgressFish(total=len(shapes))

print 'Looks like we are dealing with {}'.format(
    shapeinfo.shapetypes[str(shapetype)].lower() + 's')
for shape_record in shapefile_reader.iterShapeRecords():
    #print shape_record.shape.__geo_interface__
    #print shape_record.record
    if shape_record.record[3] == '3' or shape_record.record[2] != '999999':
    	continue
    task = MapRouletteTask(
    	challenge,
    	identifier=shape_record.record[0],
    	geometries=FeatureCollection(
    		[Feature(
    			geometry=shape_record.shape.__geo_interface__)]),
    	instruction='The Federal Railway Administration has a record of a level railway crossing at {}. Chances are that OSM does not have a crossing yet. If you see this:\n\n![crossing](https://www.dropbox.com/s/aw5sm6gle51m63f/Screenshot%202015-07-05%2019.16.46.png?dl=1)\n\n OSM already has a crossing and you can skip the task. If the little \'X\' is missing where railway and road intersect, you may need to add a `railway=level_crossing` at the intersection node, and make sure the railway and the road share the node.'.format(shape_record.record[4].strip()))
    if task.exists(server):
    	task.update(server)
    	tasks_updated+=1
    else:
    	task.create(server)
    	tasks_created+=1
    row_count = row_count + 1
    fish.animate(amount=row_count)


print 'done. {} tasks created, {} tasks updated'.format(
	tasks_created, tasks_updated)