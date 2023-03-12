import pandas as pd
import numpy as np
import time
import os
from progressbar import progressbar
import json
from copy import deepcopy
from nft import list_assets,list_assets_num

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


# Base metadata. MUST BE EDITED.
BASE_IMAGE_URL = "ipfs://<-- Your CID Code-->"
BASE_NAME = ""

BASE_JSON = {
    "name": BASE_NAME,
    "description": "",
    "image": BASE_IMAGE_URL,
    "attributes": [],
}


# Get metadata and JSON files path based on edition
def generate_paths(edition_name):
    edition_path = os.path.join('output', 'edition ' + str(edition_name))
    all_data = os.path.join('all_data.csv')
    metadata_path = os.path.join(edition_path, 'metadata.csv')
    json_path = os.path.join(edition_path, 'json')

    return edition_path, metadata_path, json_path, all_data

# Function to convert snake case to sentence case
def clean_attributes(attr_name):
    
    clean_name = attr_name.replace('_', ' ')
    clean_name = list(clean_name)
    
    for idx, ltr in enumerate(clean_name):
        if (idx == 0) or (idx > 0 and clean_name[idx - 1] == ' '):
            clean_name[idx] = clean_name[idx].upper()
    
    clean_name = ''.join(clean_name)
    return clean_name


def get_attribute_metadata(metadata_path):
    df = pd.read_csv(metadata_path)
    df = df.drop('Unnamed: 0', axis = 1)
    df.columns = [clean_attributes(col) for col in df.columns]
    zfill_count = len(str(df.shape[0]-1))

    return df, zfill_count

def get_attribute_alldata(all_data):
    df = pd.read_csv(all_data)
    df.columns = [clean_attributes(col) for col in df.columns]
    zfill_count = len(str(df.shape[0]-1))

    return df, zfill_count

# Main function that generates the JSON metadata
def main(name,image_total):
    edition_name = name
    while True:
        edition_path, metadata_path, json_path, all_data = generate_paths(edition_name)

        if os.path.exists(edition_path):
            print("Edition exists! Generating JSON metadata...")
            break
        else:
            print("Oops! Looks like this edition doesn't exist! Check your output folder to see what editions exist.")
            print("Enter edition you want to generate metadata for: ")
            continue
    
    # Make json folder
    if not os.path.exists(json_path):
        os.makedirs(json_path)
    
    # Get attribute data and zfill count
    df, zfill_count = get_attribute_metadata(metadata_path)
    df_all, zfill_count_all = get_attribute_alldata(all_data)
    
    for idx, row in progressbar(df.iterrows()):    
        item_json = deepcopy(BASE_JSON)
        item_json['name'] = item_json['name'] + str(idx)
        item_json['image'] = item_json['image'] + '/' + str(idx).zfill(zfill_count) + '.png'
        attr_dict = dict(row)
        row_df=row.to_frame()
        row_df=row_df.reset_index(drop=True)
        col=row_df.columns
        for attr in attr_dict:
            
            if attr_dict[attr] != 'none':
                    s=attr_dict[attr]
                    d=df_all.loc[df_all["Key"]==s]
                    d=d.reset_index()
                    x=d["Value"].iloc[0]
                    item_json['attributes'].append({ 'trait_type': attr, 'value': attr_dict[attr],'uniqueness': str(x/image_total*100)+"%" })
        item_json_path = os.path.join(json_path, str(idx))
        with open(str(item_json_path+".json"), 'w') as f:
            json.dump(item_json, f)

# Run the main function
for i,j in zip(list_assets,list_assets_num):
    main(i,j)

