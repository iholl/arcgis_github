import os, shutil
import arcgis
from datetime import datetime

########### Script Configuration Start ###########
# arcgis online account information
PORTAL_URL = ""
PORTAL_USERNAME = ""
PORTAL_PASSWORD = ""
# feature layer to download the attachments 
feature_layer_id = ""
# output location to download attachments
output_location = r""
########### Script Configuration End ###########

def createFolder(folder_path):
  if not os.path.exists(folder_path):
    os.mkdir(folder_path)
  else:
    print("Folder location already exists")

# remove the old attachments of the output directory
for files in os.listdir(output_location):
    path = os.path.join(output_location, files)
    try:
        shutil.rmtree(path)
    except OSError:
        os.remove(path)
# log into the Nevada Department of Wildlife ArcGIS Online account
gis = arcgis.GIS(PORTAL_URL, PORTAL_USERNAME, PORTAL_PASSWORD)
# get the feature layer based on the id provided
feature_layer = gis.content.get(feature_layer_id)

# loop through all the layer in the feature layer
for i in range(len(feature_layer.layers)):
  # get the current layer from the freature layer base on the layer id
  layer = feature_layer.layers[i]
  # check if the layer has attachments
  if layer.properties.hasAttachments == True:
    # reformat layer name
    layer_name = layer.properties.name
    # create folder with layer name
    layer_folder = os.path.join(output_location, layer_name)
    createFolder(layer_folder)
    # query all the features in the layer by objectid
    features_ids = layer.query(where="1=1", return_ids_only=True)
    # loop throught all the features in the layer
    for f in range(len(features_ids["objectIds"])):
      # get the current feature id and attachments from objectid
      current_feature_id = features_ids["objectIds"][f]
      current_feature_attachments = layer.attachments.get_list(oid=current_feature_id)
      # check if the feature has attachments
      if len(current_feature_attachments) > 0:
        # loop throught all the attachments in the feature
        for a in range(len(current_feature_attachments)):
          # get attachment id and name
          attachment_id = current_feature_attachments[a]["id"]
          attachment_name = current_feature_attachments[a]["name"]
          # query features in layer with current feature id
          sql_statement = "objectid = {}".format(str(current_feature_id))
          query_data = layer.query(where=sql_statement)
          # get creation date and creator from query data
          initial_date = query_data.features[0].attributes["CreationDate"] / 1000
          creator = query_data.features[0].attributes["Creator"]
          # format feature creation date from unix timestamp (ms) to datetime
          date = datetime.fromtimestamp(initial_date)
          formatted_date = date.strftime("%Y%m%d_%H%M%S")
          attachment_folder_name = str(formatted_date) + "_" + creator + "_" + str(attachment_id)
          # create attachment folder name and path
          attachment_folder = os.path.join(layer_folder, attachment_folder_name)
          createFolder(attachment_folder)
          # format name of sound file and final output path
          file_name = "{}_{}".format(attachment_id, attachment_name)
          final_output_path = os.path.join(attachment_folder, attachment_folder_name)
          # download attachment to final output path
          download_attachment = layer.attachments.download(
            oid=current_feature_id, 
            attachment_id=attachment_id,
            save_path=final_output_path
          )
      else:
        print("No attachments in this feature")
  else:
    print("Layer {} does not have attachments".format(layer.properties.name))
