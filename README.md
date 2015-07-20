kenya-election-data
===================

Borrowed code and data from https://github.com/mikelmaron/kenya-election-data.

Rewrote his code to crawl http://vote.iebc.or.ke/ and output the shapefiles of the voting wards with all accomapnying attributes. 

Changes: 
1/ Append constituency code + "_" in front of ward name:
Ex: 1_AIRPORT means that AIRPORT ward belongs to the constituency whose code is 1. 

2/ Fixed wards with .shx/.dbf missing:
The problem was that these wards' shapes are multi-polygon, not polygon. Thus, I split the polygons inside these multi-polygons into separate files, each file containing one polygon of the original multi-polygon. The format of the name of these files are as followed:

Constituencycode_wardname_integer whereas integer indicates the position of the polygon in the original multi-polygon.

3/ Change the "/" in the name of the ward into "_", so that folders are not created when saving shapefiles. 
Ex: "6_SHIMANZI_GANJONI_1" is created instead of having "6_GANJONI_1" inside the folder SHIMANZI as existed in the previous version of the shapefiles.
