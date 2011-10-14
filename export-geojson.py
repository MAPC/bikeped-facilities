"""

Export an ArcGIS feature class to GeoJSON

Project: bikeped facility mapping
Author: Christian Spanring

"""

import arcpy
import simplejson
import datetime
 
# Shapefile
# fc = r'C:/myfile.shp'
# ArcSDE feature class
# fc = 'Database Connections/mysdeconnection.sde/mysdefeatureclass'
# FGDB
# fc = 'C:/myfgdb.gdb/mylocalfeatureclass'

fc = ''

# use local_settings to specify the featureclass
try:
    from local_settings import *
except ImportError:
    pass

print ('reading features from %s' % (fc))

rows = arcpy.SearchCursor(fc)
fields = arcpy.ListFields(fc)

geojson = dict(type='FeatureCollection', crs={}, features = [])

# TODO: read from datasource obviously, Mass State Plane hardcoded for now
geojson["crs"] = {
	"type": "link",
	"properties": {
		"href": "http://spatialreference.org/ref/epsg/26986/proj4/",
		"type": "proj4"
	}
}

features = []

for row in rows:
	# FIXME: allow ID parameter
	feature = dict( type="Feature", id=row.getValue("objectid"), properties={}, geometry={})
	
	# write properties
	for field in fields:
		# add everything but the geometry to our properties
		if field.type != "Geometry":
			# FIXME: simplejson doesn't serialize datetime apparently 
			if type(row.getValue(field.name)) == datetime.datetime:
				feature["properties"][field.name] = str(row.getValue(field.name))
			else:
				feature["properties"][field.name] = row.getValue(field.name)
	
	# write geometry
	feature["geometry"] = row.getValue("Shape").__geo_interface__

	features.append(feature)

geojson["features"] = features

# write file and serialize json
geojson_file = open('data/bikeped-facilities.geojson', 'w')
geojson_file.write(simplejson.dumps(geojson))
geojson_file.close()

print('exported to data/bikeped-facilities.geojson')

del rows, row, field, fields