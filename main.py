# Import required libraries
from PIL import Image
import pandas as pd
import numpy as np
import time
import os
import random
from progressbar import progressbar
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
# Import configuration file
from config import CONFIG

data={}
def CountFrequency(my_list):
 
    # Creating an empty dictionary
    freq = {}
    for item in my_list:
        if (item in freq):
            freq[item] += 1
        else:
            freq[item] = 1
    data.update(freq)
    return data

def start(CONFIG,asset_loc,num):
    # Parse the configuration file and make sure it's valid
    def parse_config():
        
        # Input traits must be placed in the assets folder. Change this value if you want to name it something else.
        assets_path = asset_loc

        # Loop through all layers defined in CONFIG
        for layer in CONFIG:

            # Go into assets/ to look for layer folders
            layer_path = os.path.join(assets_path, layer['directory'])
            
            # Get trait array in sorted order
            traits = sorted([trait for trait in os.listdir(layer_path) if trait[0] != '.'])

            # If layer is not required, add a None to the start of the traits array
            if not layer['required']:
                traits = [None] + traits
            
            # Generate final rarity weights
            if layer['rarity_weights'] is None:
                rarities = [1 for x in traits]
            elif layer['rarity_weights'] == 'random':
                rarities = [random.random() for x in traits]
            elif type(layer['rarity_weights'] == 'list'):
                assert len(traits) == len(layer['rarity_weights']), "Make sure you have the current number of rarity weights"
                rarities = layer['rarity_weights']
            else:
                raise ValueError("Rarity weights is invalid")
            
            rarities = get_weighted_rarities(rarities)
            
            # Re-assign final values to main CONFIG
            layer['rarity_weights'] = rarities
            layer['cum_rarity_weights'] = np.cumsum(rarities)
            layer['traits'] = traits



    # Weight rarities and return a numpy array that sums up to 1
    def get_weighted_rarities(arr):
        return np.array(arr)/ sum(arr)

    # Generate a single image given an array of filepaths representing layers
    def generate_single_image(filepaths, output_filename=None):
        
        # Treat the first layer as the background
        bg = Image.open(os.path.join(asset_loc, filepaths[0]))
        
        
        # Loop through each layer.
        for filepath in filepaths[1:]:
            if filepath.endswith('.png'):
                img = Image.open(os.path.join(asset_loc, filepath))
                bg.paste(img, (0,0), img)
        
        # Save the final image into desired location
        if output_filename is not None:
            bg.save(output_filename)
        else:
            if not os.path.exists(os.path.join('output', 'single_images')):
                os.makedirs(os.path.join('output', 'single_images'))
            bg.save(os.path.join('output', 'single_images', str(int(time.time())) + '.png'))


    # Get total number of distinct possible combinations
    def get_total_combinations():
        
        total = 1
        for layer in CONFIG:
            total = total * len(layer['traits'])
        return total


    # Select an index based on rarity weights
    def select_index(cum_rarities, rand):
        
        cum_rarities = [0] + list(cum_rarities)
        for i in range(len(cum_rarities) - 1):
            if rand >= cum_rarities[i] and rand <= cum_rarities[i+1]:
                return i

        return None


    # Generate a set of traits given rarities
    def generate_trait_set_from_config():
        
        trait_set = []
        trait_paths = []
        
        # Extract list of traits and cumulative rarity weights
        for layer in CONFIG:
            traits, cum_rarities = layer['traits'], layer['cum_rarity_weights']
            rand_num = random.random()
            idx = select_index(cum_rarities, rand_num)
            trait_set.append(traits[idx])
            if traits[idx] is not None:
                trait_path = os.path.join(layer['directory'], traits[idx])
                trait_paths.append(trait_path)
            
        return trait_set, trait_paths


    # Generate the image set. Don't change drop_dup
    def generate_images(edition, count, drop_dup=True):
        
        # Initialize an empty rarity table
        rarity_table = {}
        for layer in CONFIG:
            rarity_table[layer['name']] = []

        # Define output path to output/edition {edition_num}
        op_path = os.path.join('output', 'edition ' + str(edition), 'images')

        # Will require this to name final images as 000, 001,...
        zfill_count = len(str(count - 1))
        
        # Create output directory if it doesn't exist
        if not os.path.exists(op_path):
            os.makedirs(op_path)
        
        # Create the images
        for n in progressbar(range(count)):
            
            # Set image name
            image_name = str(n).zfill(zfill_count) + '.png'
            
            # Get a random set of valid traits based on rarity weights
            trait_sets, trait_paths = generate_trait_set_from_config()

            # Generate the actual image
            generate_single_image(trait_paths, os.path.join(op_path, image_name))
            
            # Populate the rarity table with metadata of newly created image
            for idx, trait in enumerate(trait_sets):
                if trait is not None:
                    rarity_table[CONFIG[idx]['name']].append(trait[: -1 * len('.png')])
                else:
                    rarity_table[CONFIG[idx]['name']].append('none')
    
        for i in list(rarity_table.keys()):
            CountFrequency(rarity_table[i])
        print(data)
        data_csv=pd.DataFrame(list(data.items()),columns = ['Key','Value'])
        data_csv.to_csv("all_data.csv",index=False)
        
        # Create the final rarity table by removing duplicate creat
        rarity_table = pd.DataFrame(rarity_table).drop_duplicates()
        print("Generated %i images, %i are distinct" % (count, rarity_table.shape[0]))
        
        if drop_dup:
            # Get list of duplicate images
            img_tb_removed = sorted(list(set(range(count)) - set(rarity_table.index)))

            # Remove duplicate images
            print("Removing %i images..." % (len(img_tb_removed)))

            #op_path = os.path.join('output', 'edition ' + str(edition))
            for i in img_tb_removed:
                os.remove(os.path.join(op_path, str(i).zfill(zfill_count) + '.png'))

            # Rename images such that it is sequentialluy numbered
            for idx, img in enumerate(sorted(os.listdir(op_path))):
                os.rename(os.path.join(op_path, img), os.path.join(op_path, str(idx).zfill(zfill_count) + '.png'))
        
        
        # Modify rarity table to reflect removals
        rarity_table = rarity_table.reset_index()
        rarity_table = rarity_table.drop('index', axis=1)
        return rarity_table

    # Main function. Point of entry
    def main(num):

        print("Checking assets...")
        parse_config()
        print("Assets look great! We are good to go!")
        print()

        tot_comb = get_total_combinations()
        print("You can create a total of %i distinct avatars" % (tot_comb))
        print()

        # print("How many avatars would you like to create? Enter a number greater than 0: ")
        while True:
            # num_avatars = int(input())
            num_avatars = int(num)
            if num_avatars > 0:
                break

        edition_name=asset_loc
        print("Generating ",asset_loc)

        print("Working on it.")
        rt = generate_images(edition_name, num_avatars)

        print("Working on metadata...")
        rt.to_csv(os.path.join('output', 'edition ' + str(edition_name), 'metadata.csv'))

        print("Task complete!")

    main(num)

'''
TODO: 
    -- Here, you can pass the folder that contains your layers.
    -- Drop your 'layers' folder in the same directory as the 'main.py' file.
'''
list_assets=["ex_1","ex_2"]
# Number of NFT for each folder
list_assets_num=[5,5]

''' 
NOTE: len(list_assets)   ==    len(list_assets_num)
'''

for i,j,k in zip(list_assets,range(len(list_assets)),list_assets_num):
    start(CONFIG[j],i,k)
