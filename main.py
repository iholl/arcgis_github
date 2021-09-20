import arcgis

# get access to the fishable waters data and export the data to a GeoJson file in the arcgis online account
gis = arcgis.GIS(url=None, username='NDOW_DEV', password='nd0wM@PS1!')
data = gis.content.get('69327cd8775f4683aecc5cfd71bf3b77')
data_title = data.title
export_geojson = data.export(title=data_title, export_format='GeoJson', parameters=None, wait=True)
print('export geojson created in arcgis online account')

# download to github
export_geojson.download(save_path='fishable_waters_lines')

