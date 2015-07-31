import json
import urllib2
import re
import os
import sys
import hashlib
import hmac
import os
import time
import shapefile
from pprint import pprint

appid = "KEA69001"
appsecret = "42aeb1d9c875d1ef1b905d2e81b7c5bf"

def loadjson(baseurl, args, token): 

	url = baseurl + '?' + args 

	try: 
		keyString = 'token=' + token
		new_key = hmac.new(appsecret, keyString, hashlib.sha256).hexdigest()
		filehandle = urllib2.urlopen(url + "&token=" + token + "&key=" + new_key)
		data = filehandle.read()
		filehandle.close()
	except:
		print "Could not load " + url 
 		return

	json_data = json.loads(data)
	return json_data 

def get_token():
	baseurl = 'http://api.iebc.or.ke/token/'

	key = hmac.new(appsecret, "appid=" + appid, hashlib.sha256).hexdigest()
	filehandle=urllib2.urlopen(baseurl + "?appid="+appid + "&key=" + key)
	data = filehandle.read()
	filehandle.close()
	json_data = json.loads(data)
	return json_data['token']

def get_counties(token):
	return loadjson('http://api.iebc.or.ke/county/', "", token)

def get_county_constituencies(c):
	return loadjson("http://api.iebc.or.ke/constituency/", "county=" + c, token)

def get_constituency_wards(c):
	return loadjson("http://api.iebc.or.ke/ward/", "constituency=" + c, token)

def backslash_into_underscore(string):
	"Change the backslash in a string into underscore"
	new_string = string.replace("/","_")
	return new_string

def check_key_dict(dict, key):
	'If a dict does not have key, add key to dict and dict[key] = Not Available'
	try:
		dict[key]
	except KeyError:
		dict[key] = 'Not Available'

	return dict

def convert_unicode_into_string_dict(dict):
	'convert all value of type unicode into type string'

	for key in dict.keys():
		if type(dict.keys()) == 'unicode':
			dict[key] = str(dict[key])

	return dict

def floatify_list_item(given_list):
	for item in given_list:
		if type(item) == list: floatify_list_item(item)
		else: item = float(item)

	return given_list

def save_shape_file(ward_geo):
	'save the input as shapefile'
	'if data is a polygon, save as a single shapefile'
	'if data is multi polygon, save as multiple shapefile, each shapefile containing 1 polygon of the original multi-polygon'

	if ward_geo['features'][0]['geometry']['type'] == "MultiPolygon": 
		num_polygon = len(ward_geo['features'][0]['geometry']['coordinates'])

		for i in range(num_polygon):
			w = shapefile.Writer(shapeType=5)
			w.autoBalance = 1

			coordinates = ward_geo['features'][0]['geometry']['coordinates'][i]

			floatify_list_item(coordinates)

			w.poly(parts = coordinates)

			properties = ward_geo['features'][0]['properties'].keys()

			for property in properties:
				if isinstance(property, unicode):
					property = str(property)
					
				w.field(property)
			
			w.record( \
				CONST_CODE = ward_geo['features'][0]['properties']['CONST_CODE'], \
				Shape_Area = ward_geo['features'][0]['properties']['Shape_Area'], \
				OBJECTID_1 = ward_geo['features'][0]['properties']['OBJECTID_1'], \
				name = ward_geo['features'][0]['properties']['name'], \
				OBJECTID = ward_geo['features'][0]['properties']['OBJECTID'], \
				CONSTITUEN =  ward_geo['features'][0]['properties']['CONSTITUEN'], \
				COUNTY_ASS = ward_geo['features'][0]['properties']['COUNTY_ASS'], \
				COUNTY_A_1 = ward_geo['features'][0]['properties']['COUNTY_A_1'], \
				COUNTY_COD = ward_geo['features'][0]['properties']['COUNTY_COD'], \
				Shape_Leng = ward_geo['features'][0]['properties']['Shape_Leng'], \
				COUNTY_NAM = ward_geo['features'][0]['properties']['COUNTY_NAM'], \
				Shape_Le_1 = ward_geo['features'][0]['properties']['Shape_Le_1'], \
			)
				

			CONST_CODE = ward_geo['features'][0]['properties']['CONST_CODE']
			name = 'shapefile_ward/' + str(CONST_CODE) + '_' + str(ward_geo['features'][0]['properties']['name']) + '_' + str(i+1)
			w.save(name)

	elif ward_geo['features'][0]['geometry']['type'] == 'Polygon':
		w = shapefile.Writer(shapeType=5)
		w.autoBalance = 1

		coordinates = ward_geo['features'][0]['geometry']['coordinates']

		floatify_list_item(coordinates)

		w.poly(parts = coordinates)

		properties = ward_geo['features'][0]['properties'].keys()

		for property in properties:
			if isinstance(property, unicode):
				property = str(property)

			w.field(property)

		w.record( \
			CONST_CODE= ward_geo['features'][0]['properties']['CONST_CODE'], \
			Shape_Area= ward_geo['features'][0]['properties']['Shape_Area'], \
			OBJECTID_1= ward_geo['features'][0]['properties']['OBJECTID_1'], \
			name =  ward_geo['features'][0]['properties']['name'], \
			OBJECTID= ward_geo['features'][0]['properties']['OBJECTID'], \
			CONSTITUEN=  ward_geo['features'][0]['properties']['CONSTITUEN'], \
			COUNTY_ASS= ward_geo['features'][0]['properties']['COUNTY_ASS'], \
			COUNTY_A_1= ward_geo['features'][0]['properties']['COUNTY_A_1'], \
			COUNTY_COD= ward_geo['features'][0]['properties']['COUNTY_COD'], \
			Shape_Leng= ward_geo['features'][0]['properties']['Shape_Leng'], \
			COUNTY_NAM= ward_geo['features'][0]['properties']['COUNTY_NAM'], \
			Shape_Le_1= ward_geo['features'][0]['properties']['Shape_Le_1'], \
			)

		CONST_CODE = ward_geo['features'][0]['properties']['CONST_CODE']

		name = 'shapefile_ward/' + str(CONST_CODE) + '_' + str(ward_geo['features'][0]['properties']['name'])
		w.save(name)
		
	elif (ward_geo['features'][0]['geometry']['type'] != 'Polygon') \
	     (ward_geo['features'][0]['geometry']['type'] != 'MultiPolygon'):
	     	print "error: neither polygon or multipolygon" 

def convert_unicode_into_string_dict(dict):
    'convert all value of type unicode into type string'

    for key in dict.keys():
        if isinstance(dict[key], unicode):
            dict[key] = str(dict[key])

    return dict

token = get_token()
ward = [] 
counties = get_counties(token)

twelve_attribute = ['CONST_CODE', 'Shape_Area', 'OBJECTID_1', 'OBJECTID', 'CONSTITUEN', 'COUNTY_ASS', 'COUNTY_A_1', 'COUNTY_NAM', 'COUNTY_COD', 'Shape_Leng', 'Shape_Le_1', 'name']

for county in counties['region']['locations']:
	constituencies = get_county_constituencies(county['code']) 
	for constituency in constituencies['region']['locations']:
		wards = get_constituency_wards(constituency['code'])
		for ward in wards['region']['locations']:

			ward_geo = loadjson(ward['polygon'], "", token)

			if ward_geo is None: 
				continue 

			try:
				ward_name = backslash_into_underscore(ward['name'])

				CONST_CODE = ward_geo['features'][0]['properties']['CONST_CODE']

				name = 'ward_geojson/' + str(CONST_CODE) + '_' + str(ward_name)

				with open(name + '.json', 'w') as outfile:
					json.dump(ward_geo, outfile, indent = 4 ) 

			except IndexError:
				"There is an index error raise exception here because of missing information for the ward NGEI in Mathare constituency  in Nairobi county."
				print "Index Error with missing info" 

			except KeyError:
				pass
