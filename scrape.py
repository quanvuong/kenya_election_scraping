import json
import urllib2
import re
import os
import sys
import requests
import hashlib
import hmac
import os
import time
import shapefile
from pprint import pprint

county_url = 'http://api.iebc.or.ke/results/county/'
constituency_url = 'http://api.iebc.or.ke/results/constituency/'
ward_url = 'http://api.iebc.or.ke/results/ward/'
pollingstation_url = 'http://api.iebc.or.ke/results/pollingstation/'

token = ''
appid = ""
appsecret = ""

base_dir = './download/'
static_dir = base_dir + 'static/'
other_dir = base_dir + 'latest/'
geo_dir = './data/'

CACHE = True

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    #import unicodedata
    #value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    value = re.sub('[-\s]+', '-', value)
    return value

def loadjson(baseurl, args, download_dir):
	url = baseurl + "?" + args
	url = re.sub('\s','+', url)
	slug = slugify(url)

	if (os.path.exists(download_dir + slug)):
		filehandle = open(download_dir + slug)
		data = filehandle.read()
		filehandle.close()
	elif CACHE:
		return
	else:
		try:
			keyString = args + 'token=' + token	
			new_key = hmac.new(appsecret, keyString, hashlib.sha256).hexdigest()
			filehandle=urllib2.urlopen(url + "&token=" + token + "&key=" + new_key)
			data = filehandle.read()
			filehandle.close()
		except:
			print "Could not load " + url
			return      

		filehandle = open(download_dir + slug, 'w')
		filehandle.write(data)
		filehandle.close()

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

def get_county_results(c):
	for i in range(1,7):
		loadjson(county_url + c + '/', 'post=' + str(i),other_dir)

def get_county_result(c,i):
	return loadjson(county_url + c + '/', 'post=' + str(i),other_dir)

def get_ward_results(c):
	for i in range(1,7):
		loadjson(ward_url + c + '/', 'post=' + str(i),other_dir)

def get_ward_result(c,i):
	return loadjson(ward_url + c + '/', 'post=' + str(i),other_dir)

def get_constituency_results(c):
	for i in range(1,7):
		loadjson(constituency_url + c + '/', 'post=' + str(i),other_dir)

def get_pollingstation_results(c):
	for i in range(1,7):
		loadjson(pollingstation_url + c + '/', 'post=' + str(i),other_dir)

def get_counties():
	return loadjson("http://api.iebc.or.ke/county/","", static_dir)

def get_county_constituencies(c):
  return loadjson("http://api.iebc.or.ke/constituency/", "county=" + c, static_dir)

def get_constituency_wards(c):
	return loadjson("http://api.iebc.or.ke/ward/", "constituency=" + c, static_dir)

def get_ward_pollingplaces(c):
	return loadjson("http://api.iebc.or.ke/pollingstation/", "ward=" + c, static_dir)

def get_county(name):
	counties = get_counties()
	for county in counties['region']['locations']:
		if county['name'] == name:
			return county

def get_constituency(c, name):
	constituencies = get_county_constituencies(c)
	for constituency in constituencies['region']['locations']:
		if constituency['name'] == name:
			return constituency

def deter_attribute_type(attribute_value):
	if type(attribute_value) == str or 'unicode': 
		return 'C'
	if type(attribute_value) == float or type(attribute_value) == int:
		return 'N'

def floatify_list_item(given_list):
	for item in given_list:
		if type(item) == list: floatify_list_item(item)
		else: item = float(item)

	return given_list

def backslash_into_underscore(string):
	"Change the backslash in a string into underscore"
	new_string = string.replace("/","_")
	return new_string

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
				CONST_CODE=ward_geo['features'][0]['properties']['CONST_CODE'], \
				Shape_Area=ward_geo['features'][0]['properties']['Shape_Area'], \
				OBJECTID_1=ward_geo['features'][0]['properties']['OBJECTID_1'], \
				NAME=ward_geo['features'][0]['properties']['NAME'], \
				OBJECTID=ward_geo['features'][0]['properties']['OBJECTID'], \
				CONSTITUEN= ward_geo['features'][0]['properties']['CONSTITUEN'], \
				COUNTY_ASS=ward_geo['features'][0]['properties']['COUNTY_ASS'], \
				SPOILT=ward_geo['features'][0]['properties']['SPOILT'], \
				COUNTY_A_1=ward_geo['features'][0]['properties']['COUNTY_A_1'], \
				REJECTED=ward_geo['features'][0]['properties']['REJECTED'], \
				REPORTED=ward_geo['features'][0]['properties']['REPORTED'], \
				SPOILT_VALID=ward_geo['features'][0]['properties']['SPOILT_VALID'], \
				VALID=ward_geo['features'][0]['properties']['VALID'], \
				DISPUTED=ward_geo['features'][0]['properties']['DISPUTED'], \
				RESULT=ward_geo['features'][0]['properties']['RESULT'], \
				COUNTY_COD=ward_geo['features'][0]['properties']['COUNTY_COD'], \
				Shape_Leng=ward_geo['features'][0]['properties']['Shape_Leng'], \
				COUNTY_NAM=ward_geo['features'][0]['properties']['COUNTY_NAM'], \
				Shape_Le_1=ward_geo['features'][0]['properties']['Shape_Le_1'], \
				REGISTERED=ward_geo['features'][0]['properties']['REGISTERED']
				)

			CONST_CODE = ward_geo['features'][0]['properties']['CONST_CODE']
			name = 'shapefile_ward/' + str(CONST_CODE) + '_' + str(ward_geo['features'][0]['properties']['NAME']) + '_' + str(i+1)
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
			CONST_CODE=ward_geo['features'][0]['properties']['CONST_CODE'], \
			Shape_Area=ward_geo['features'][0]['properties']['Shape_Area'], \
			OBJECTID_1=ward_geo['features'][0]['properties']['OBJECTID_1'], \
			NAME=ward_geo['features'][0]['properties']['NAME'], \
			OBJECTID=ward_geo['features'][0]['properties']['OBJECTID'], \
			CONSTITUEN= ward_geo['features'][0]['properties']['CONSTITUEN'], \
			COUNTY_ASS=ward_geo['features'][0]['properties']['COUNTY_ASS'], \
			SPOILT=ward_geo['features'][0]['properties']['SPOILT'], \
			COUNTY_A_1=ward_geo['features'][0]['properties']['COUNTY_A_1'], \
			REJECTED=ward_geo['features'][0]['properties']['REJECTED'], \
			REPORTED=ward_geo['features'][0]['properties']['REPORTED'], \
			SPOILT_VALID=ward_geo['features'][0]['properties']['SPOILT_VALID'], \
			VALID=ward_geo['features'][0]['properties']['VALID'], \
			DISPUTED=ward_geo['features'][0]['properties']['DISPUTED'], \
			RESULT=ward_geo['features'][0]['properties']['RESULT'], \
			COUNTY_COD=ward_geo['features'][0]['properties']['COUNTY_COD'], \
			Shape_Leng=ward_geo['features'][0]['properties']['Shape_Leng'], \
			COUNTY_NAM=ward_geo['features'][0]['properties']['COUNTY_NAM'], \
			Shape_Le_1=ward_geo['features'][0]['properties']['Shape_Le_1'], \
			REGISTERED=ward_geo['features'][0]['properties']['REGISTERED']
			)

		CONST_CODE = ward_geo['features'][0]['properties']['CONST_CODE']

		name = 'shapefile_ward/' + str(CONST_CODE) + '_' + str(ward_geo['features'][0]['properties']['NAME'])
		w.save(name)

def convert_unicode_into_string_dict(dict):
	'convert all value of type unicode into type string'

	for key in dict.keys():
		if type(dict.keys()) == 'unicode':
			dict[key] = str(dict[key])

	return dict

def check_key_dict(dict, key):
	'If a dict does not have key, add key to dict and dict[key] = Not Available'
	try:
		dict[key]
	except KeyError:
		dict[key] = 'Not Available'

	return dict

twenty_attribute = ['CONST_CODE', 'Shape_Area', 'OBJECTID_1', 'NAME', 'OBJECTID', 'CONSTITUEN', 'COUNTY_ASS', 'SPOILT', 'COUNTY_A_1', 'REJECTED', 'COUNTY_NAM', 'REPORTED', 'SPOILT_VALID', 'VALID', 'RESULT', 'COUNTY_COD', 'Shape_Leng', 'DISPUTED', 'Shape_Le_1', 'REGISTERED']

first = True
counties = get_counties()
for county in counties['region']['locations']:
	constituencies = get_county_constituencies(county['code'])
	for constituency in constituencies['region']['locations']:
		wards = get_constituency_wards(constituency['code'])
		for ward in wards['region']['locations']:
			ward_geo = loadjson(ward['polygon'], "", geo_dir)
			if ward_geo is None:
				continue

			ward_result = get_ward_result(ward['code'], 1)
			if ward_result is not None and ward_result['contests'][0]['locations'] is not None:
				ward_geo['features'][0]['properties']['RESULT'] = "1"
				ward_geo['features'][0]['properties']['DISPUTED'] = ward_result['contests'][0]['locations'][0]['disputed']
				ward_geo['features'][0]['properties']['REGISTERED'] = ward_result['contests'][0]['locations'][0]['registered']
				ward_geo['features'][0]['properties']['SPOILT'] = ward_result['contests'][0]['locations'][0]['spoilt']
				ward_geo['features'][0]['properties']['REJECTED'] = ward_result['contests'][0]['locations'][0]['rejected']
				ward_geo['features'][0]['properties']['REPORTED'] = ward_result['contests'][0]['locations'][0]['reported']
				ward_geo['features'][0]['properties']['VALID'] = ward_result['contests'][0]['locations'][0]['valid']
				ward_geo['features'][0]['properties']['SPOILT_VALID'] = float(ward_result['contests'][0]['locations'][0]['spoilt']) / float(ward_result['contests'][0]['locations'][0]['valid'])
			else:
				ward_geo['features'][0]['properties']['RESULT'] = "0"

			ward_geo['features'][0]['properties']['NAME'] = backslash_into_underscore(ward['name'])

			for attribute in twenty_attribute:
				ward_geo['features'][0]['properties'] = check_key_dict(ward_geo['features'][0]['properties'], attribute)

			save_shape_file(ward_geo)
	
