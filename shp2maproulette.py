#!/usr/bin/env python

"""shp2maproulette - a script that creates or updates a MapRoulette challenge from a Shapefile.

Usage:
    shp2maproulette.py OPTFILE
    shp2maproulette.py --version

Options:
    -h --help       Show this help text
    --version       Output script version
"""

import shapefile
import shapeinfo
from maproulette import MapRouletteServer, MapRouletteChallenge, MapRouletteTask, MapRouletteTaskCollection
from geojson import FeatureCollection, Feature
import sys
import yaml
from docopt import docopt

__version__ = '0.0.3'

# initialize docopt argument parsing
arguments = docopt(__doc__, version='shp2maproulette {}'.format(__version__))

# read in optfile
options = None
try:
    with open(arguments['OPTFILE']) as optfile:
        options = yaml.load(optfile)
except Exception, e:
    raise e

if not all (opt in options for opt in (
    'server',
    'shapefile',
    'challenge_slug',
    'challenge_title',
    'identifier_field',
    'instruction_template',
    'instruction_replacement_fields')):
    print 'options file does not contain all keys.'
    sys.exit(1)

# initialize counter
row_count = 0

# get a server
server = MapRouletteServer(options['server'])

# get the challenge
challenge = None
challenge = MapRouletteChallenge(
	slug=options['challenge_slug'],
	title=options['challenge_title'],
	active=True)

# there is no way to upsert a challenge, so we need this conditional
if challenge.exists(server):
	print 'updating challenge...'
	challenge.update(server)
else:
	print 'creating challenge...'
	challenge.create(server)

# read in the shapefile features
shapefile_reader = shapefile.Reader(options['shapefile'])
shapes = shapefile_reader.shapes()

# set limit
LIMIT = options['limit'] or None
limit = min(LIMIT, len(shapes))

# tasks list
tasks = []

# iterate over shapefile features + records
for shape_record in shapefile_reader.iterShapeRecords():
    task = MapRouletteTask(
    	shape_record.record[options['identifier_field']],
        challenge=challenge,
    	geometries=FeatureCollection(
    		[Feature(
    			geometry=shape_record.shape.__geo_interface__)]),
    	instruction=r'{}'.format(
            options['instruction_template'].format(
                **{key: shape_record.record[val].strip()
        		for (key, val)
                in options['instruction_replacement_fields'].items()})))
    tasks.append(task)
    row_count = row_count + 1
    if row_count == limit:
    	break

new_collection = MapRouletteTaskCollection(challenge, tasks=tasks)
print 'reconciling {} tasks with the server...'.format(len(tasks))
result = new_collection.reconcile(server)

print 'done. {new} tasks created, {changed} tasks changed, {deleted} tasks deleted'.format(
	new=len(result['new']),
    changed=len(result['changed']),
    deleted=len(result['deleted']))