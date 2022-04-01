import arcgis
import arcpy
import time
import os
from zipfile import ZipFile
import shutil

# log into arcgis online

# list of feature services to download from arcgis online

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
