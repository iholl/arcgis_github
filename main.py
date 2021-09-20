import os
import arcgis
from datetime import datetime

# set secrets from github repo
ARCGIS_ONLINE_USERNAME = os.environ['ARCGIS_ONLINE_USERNAME']
ARCGIS_ONLINE_PASSWORD = os.environ['ARCGIS_ONLINE_PASSWORD']

# get access to the fishable waters data and export the data to a GeoJson file in the arcgis online account
gis = arcgis.GIS(url=None, username=ARCGIS_ONLINE_USERNAME, password="ARCGIS_ONLINE_PASSWORD")
data = gis.content.get("69327cd8775f4683aecc5cfd71bf3b77")
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
data_title = data.title + "_" + current_time
export_geojson = data.export(title=data_title, export_format="GeoJson", parameters=None, wait=True)
print("export geojson created in arcgis online account")

# download to github and remove geojson from arcgis online
export_geojson.download(save_path="fishable_waters_lines")
export_geojson.delete()
print('downloaded fishable_waters_lines')




