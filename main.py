import arcgis
from datetime import date
from decouple import config

# set local env variables
ARCGIS_ONLINE_USERNAME = config('ARCGIS_ONLINE_USERNAME')
ARCGIS_ONLINE_PASSWORD = config('ARCGIS_ONLINE_PASSWORD')

# get access to the arcgis online content
gis = arcgis.GIS(url=None, username=ARCGIS_ONLINE_USERNAME, password=ARCGIS_ONLINE_PASSWORD)

# arcgis online feature layers
fishable_lines = "69327cd8775f4683aecc5cfd71bf3b77"
fishable_polygons = "8ec9b5ac269d40dca78af47a22e05af3"
data_list = [fishable_lines, fishable_polygons]

# set current date
today = date.today()
current_time = today.strftime("%m_%d_%Y")

for feature_layer in data_list:
	# get feature layer by id and export to a GeoJson
	data = gis.content.get(feature_layer)
	data_title = data.title + "_" + current_time
	export_geojson = data.export(title=data_title, export_format="GeoJson", parameters=None, wait=True)
	print("export geojson created in arcgis online account: " + data_title)

	# download to github and remove geojson from arcgis online
	export_geojson.download(save_path="fishable_data")
	export_geojson.delete()
	print("downloaded complete")






