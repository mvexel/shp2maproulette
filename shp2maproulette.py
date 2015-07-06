#!/usr/bin/env python

import shapefile
import shapeinfo
from maproulette import MapRouletteServer, MapRouletteChallenge, MapRouletteTask, MapRouletteTaskCollection
from geojson import FeatureCollection, Feature
import sys
from fish import ProgressFish

# TODO Constants, these need to be parameters

# This is your source Shapefile
SHAPEFILE='/Users/martijnv/tmp/crossings/shape/crossings.shp'

# This is the MapRoulette challenge slug
CHALLENGE_SLUG='fix-railway-crossings'

# And the MapRoulette challenge title
CHALLENGE_TITLE='Fix U.S. railway crossings'

# The index of the field that will hold your unique identifier
IDENTIFIER_FIELD=0

# Limit the challenge to this amount of tasks (for debugging purposes)
LIMIT=100

# The template for the task instruction. Use {} for placeholders to be replaced from attribute values in the Shapefile
INSTRUCTION_TEMPLATE='The Federal Railway Administration has a record of a level railway crossing at {}. Chances are that OSM does not have a crossing yet. If you see this:\n\n![crossing](https://www.dropbox.com/s/aw5sm6gle51m63f/Screenshot%202015-07-05%2019.16.46.png?dl=1)\n\n OSM already has a crossing and you can skip the task. If the little \'X\' is missing where railway and road intersect, you may need to add a `railway=level_crossing` at the intersection node, and make sure the railway and the road share the node.'

# A list of field indices holding replacement values for the template string above.
# Make sure the length of this list matches the number of placeholders in your string.
INSTRUCTION_REPLACEMENT_FIELDS=[4]

# initialize counters
row_count = 0
tasks_created=0
tasks_updated=0

# get a server
server = MapRouletteServer()

# get the challenge
challenge = None
challenge = MapRouletteChallenge(
	slug=CHALLENGE_SLUG,
	title=CHALLENGE_TITLE,
	active=True)

# there is no way to upsert a challenge, so we need this conditional
if challenge.exists(server):
	print 'updating challenge...'
	challenge.update(server)
else:
	print 'creating challenge...'
	challenge.create(server)

# read in the shapefile features
shapefile_reader = shapefile.Reader(SHAPEFILE)
shapes = shapefile_reader.shapes()

limit = min(LIMIT, len(shapes))
# initialize progress bar
fish = ProgressFish(total=limit)

# iterate over shapefile features + records
for shape_record in shapefile_reader.iterShapeRecords():
    task = MapRouletteTask(
    	challenge,
    	identifier=shape_record.record[IDENTIFIER_FIELD],
    	geometries=FeatureCollection(
    		[Feature(
    			geometry=shape_record.shape.__geo_interface__)]),
    	instruction=INSTRUCTION_TEMPLATE.format(
    		*[shape_record.record[f].strip()
    		for f
    		in INSTRUCTION_REPLACEMENT_FIELDS]))
    if task.exists(server):
    	task.update(server)
    	tasks_updated+=1
    else:
    	task.create(server)
    	tasks_created+=1
    row_count = row_count + 1
    if row_count == limit:
    	break
    fish.animate(amount=row_count)


print 'done. {} tasks created, {} tasks updated'.format(
	tasks_created, tasks_updated)