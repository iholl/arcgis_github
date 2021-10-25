import arcgis
import arcpy
import time
import os
from zipfile import ZipFile
import shutil

# log into arcgis online

# list of feature services to download from arcgis online
harvest_check_in_lion_18_19 = '6ed59d8cd8da45db90d4878164405abd'
harvest_check_in_bighorn_18_19 = 'e08ff9fa0cf240438572b297f60a803f'
harvest_check_in_19_20 = 'c7b2c0986d5449fabd4f28543c28792b'
harvest_check_in_19_20_v2 = '88037ece957c4f8681d2677d073402c1'
harvest_check_in = '2296745b20234d7fa4fb5efca9ee91e3'

upland_game = 'e9b8f1ae1e0240ab99c6151d2dfef7ab'

black_bear_mortality = 'e5078c364fe745d2a0dfcf402947ab41'

aml = '5055d4e4f88a4e2d88c9cead876c6da7'

big_game_tissue = 'abbd07ffb6ac48f882135fbf84005000'

dixie_valley_toad = 'ce2e501a548a495497418d60816256c6'

contact_log = '9aaf7a54104849f19628f94a67d2af4a'
hours_log = '07219e147e93492eadd8214fc798139b'

cso_surveys = 'd1c20b188a324cf38bbafe62578191ac'

toad_crm_10 = 'bb5102d6e82745ad98d6656a1ef117e1'
toad_grid_cell = '7dfc7792741241e9831106b0d8474fe4'
toad_roving = '7c90b34620aa462e9b0fa367ebfaba11'

radio_collar = 'c55925549d704c228c7cd2677fea2623'

road_cruising = 'ad5f037175f24e8e923e9353a6930787'

sage_grouse_19_20 = 'f2471d58998b47058c59624990ea230d'
sage_grouse_v1 = 'f25feb4699004073861d03678782dbf6'
sage_grouse = '335f97205f35466fba192fe5c02d4870'

winter_raptor = '8728c607a7064c7a9a47793d3bd03cd2'

data_item = [
	harvest_check_in_lion_18_19, 
	harvest_check_in_bighorn_18_19, 
	harvest_check_in_19_20, 
	harvest_check_in_19_20_v2, 
	harvest_check_in,
	upland_game,
	black_bear_mortality,
	aml, 
	big_game_tissue, 
	dixie_valley_toad, 
	contact_log,
	hours_log, 
	cso_surveys, 
	toad_crm_10, 
	toad_grid_cell,
	toad_roving,
	radio_collar, 
	road_cruising, 
	sage_grouse_19_20, 
	sage_grouse_v1,
	sage_grouse, 
	winter_raptor
]

# path variables
pathExport = r''
scratch_gdb = r''
date_string = time.strftime('%Y%m%d')

# for each id in the data item list
for x in data_item:
	# get feature service from arcgis online content but id
	data = agoLogin.content.get(x)
	# query title of feature service for zipped shapefile name
	item_name = data.title
	print(item_name)
	# export feature service to shapefile in arcgis online content
	item = data.export(title=item_name, export_format='Shapefile', parameters=None, wait=True)
	# download zipped shapefile from arcgis online content to V:/Survey123
	temp_path = os.path.join(pathExport, item_name)
	item.download(save_path=temp_path)
	# after download delete exported shapefile in ArcGIS Online content
	item.delete()
	# get download zipped shapefile name to use for feature class name
	if item_name == 'LE Hours Log':
		initial_path = os.listdir(temp_path)
		print(initial_path)
		initial_name = initial_path[4]
		print(initial_name)
		export_name = os.path.splitext(initial_name)[0]
		print(export_name)
	else:
		initial_path = os.listdir(temp_path)
		initial_name = initial_path[0]
		print(initial_name)
		export_name = os.path.splitext(initial_name)[0]
		print(export_name)
	# extract shapefiles form zipped shapefile downloaded
	zf = ZipFile(os.path.join(temp_path, initial_name))
	zf.extractall(path=os.path.join(temp_path, ''))
	zf.close()
	# check if a main feature dataset exists, if it does then use the existing one, if not then create one
	path_set = os.path.join(scratch_gdb, export_name)
	if arcpy.Exists(path_set):
		new_dataset = path_set
		print('That feature dataset already exists at: ' + new_dataset)
	else:
		spatial_resource = arcpy.SpatialReference('NAD 1983 UTM Zone 11N')
		new_dataset = arcpy.CreateFeatureDataset_management(scratch_gdb, export_name, spatial_resource)
		print('That feature dataset does not exists, creating a new one')
	# list all the files extracted from zipped shapefile
	file_list = os.listdir(temp_path)
	for file in file_list:
		# find each .shp in the list of files
		if file.endswith('.shp'):
			# create a path to the .shp file and extract the file name with no extension
			shapefile = os.path.join(temp_path, file)
			base = os.path.basename(shapefile)
			split = os.path.splitext(base)
			name = os.path.splitext(base)[0]
			print(name)
			# export .shp file to feature class in assigned feature dataset
			arcpy.FeatureClassToFeatureClass_conversion(shapefile, new_dataset, name, '')
			# this is hacky code, new_dataset was not reading as path, this can be made cleaner
			path = str(new_dataset)
			new_feature = path + '\\' + name
			new_feature_projected_name = name + '_projected'
			new_feature_projected = scratch_gdb + '\\' + new_feature_projected_name
			# project new feature class to NAD83
			spatial_resource = arcpy.SpatialReference('NAD 1983 UTM Zone 11N')
			arcpy.Project_management(new_feature, new_feature_projected, spatial_resource)
			# name and path for root feature class
			root_name = name + '_main'
			root_path = os.path.join(path, root_name)
			# check if the root feature class exists
			if arcpy.Exists(root_path):
				print('The root feature ' + root_name + ' already exists')
			else:
				try:
					arcpy.FeatureClassToFeatureClass_conversion(new_feature_projected, path, root_name, '')
					print('No root feature class found, created new feature class named ' + root_name)
				except arcpy.ExecuteError:
					root_name = export_name + '_' + root_name
					root_path = os.path.join(path, root_name)
					if arcpy.Exists(root_path):
						print('The root ' + root_name + ' already exists')
					else:
						arcpy.FeatureClassToFeatureClass_conversion(new_feature_projected, path, root_name, '')
						print('No root feature class found, created new feature class: ' + root_name)
			# compare newly downloaded shapefile with root feature class to see if there is new data
			root_feature = os.path.join(path, root_name)
			status = arcpy.FeatureCompare_management(root_feature, new_feature_projected, 'OBJECTID', 'ALL', '','0.001 DecimalDegrees', '0.001', '0.001', '', '', 'NO_CONTINUE_COMPARE')
			status_output = status.getOutput(1)
			print('Comparing new data with current data, false if they are different, true if they are the same: ' + status_output)
			# if false the two shapefiles are different and we should use the more up to date data
			if status_output == 'false':
				print('Your data is different, lets update the root data and archive the old data')
				# copy and archive the old root feature class and assign a date for the last time the data was most recent
				archived_name = name + '_archived_' + date_string
				root_feature_archived = os.path.join(path, archived_name)
				arcpy.Copy_management(in_data=root_feature, out_data=root_feature_archived)
				# remove the old root feature class, copy the new feature class to the new root, and clear the intermediate results
				arcpy.Delete_management(root_feature)
				arcpy.Copy_management(in_data=new_feature_projected, out_data=root_feature)
				arcpy.Delete_management(new_feature_projected)
				arcpy.Delete_management(new_feature)
				print('Your data was updated with new data from app')
			# if no difference between shapefile, no need to update data just delete intermediate results
			else:
				arcpy.Delete_management(new_feature_projected)
				arcpy.Delete_management(new_feature)
				print('Your data is not different, no need to update')
	# delete the downloaded shapefile as it is added to the geodatabase
	shutil.rmtree(temp_path)
	print('Successfully completed pulling down data from ArcGIS Online to V:\\Survey123 for ' + export_name)
