# code to summarise simulation landscapes with Moran's I ####

# importing libraries and paths
# check python path
import sys
# should yield python 3.7 file path
for p in sys.path:
    print(p)

import os  # has listdir functions etc
import numpy as np  # some matrix and numerical functions
import imageio  # library to read images
import matplotlib  # import plotting library
import matplotlib.pyplot as plt  # assign a keyword
import seaborn as sns  # another plotting library
import re  # import regular expressions library
import pandas as pd  # import the dataframes library

from helper_functions import get_moran_local, get_lisa_proportions

# may need to use the tkagg backend on some unix systems
matplotlib.use("TkAgg")

# check the current working directory
p = os.getcwd()
currentWd = p
# check again
print(currentWd)

# gather image output
outputFolder = os.path.join(currentWd, "data")  # os.path.abspath("output")
# check for the right folder
if "data" not in outputFolder:
    raise Exception('seems like the wrong output folder...')


# gather the folders in the directory avoiding zip files
data_folders = os.listdir(outputFolder)
data_folders = list(filter(lambda x: "run" in x and ".zip" not in x, data_folders))

# here we go through all the subfolders in the data folder and
# list the files in those folders in the order of the generations
list_of_lists_images = []  # each element of the list is a 'run' or a replicate
for folder in data_folders:  # go through each run folder
    this_folder = os.path.join(outputFolder, folder)  # get the filepath to that folder
    for root, directories, filenames in os.walk(this_folder): # now look at all the files in that folder
        these_images = []
        for filename in filenames:
            these_images.append(os.path.join(root, filename))
        # sort the images in order of generations
        these_images.sort()
        these_images = list(filter(lambda x: "landscape" in x, these_images))
        list_of_lists_images.append(these_images)


# define a function to count the agents in each layer
# we also want to know which generation we are dealing with
def count_agents(landscape_file):
    # this uses regex
    replicate = int(re.findall(r'run_(\d{2})', landscape_file)[0])  # which run is it
    generation = int(re.findall(r'landscape(\d{5})', landscape_file)[0])  # get the generation as an integer
    landscape = imageio.imread(landscape_file)
    # get the numbers of klepts, handlers, and foragers
    n_klepts = landscape[:,:,0].sum()
    n_handlers = landscape[:,:,1].sum()
    n_foragers = landscape[:,:,2].sum()
    total = n_klepts+n_foragers+n_handlers
    return [replicate, generation, n_klepts/total, n_handlers/total, n_foragers/total]


# map count agents over the folders
list_of_data = []
for i in list_of_lists_images:
    tmp_list = list(map(count_agents, i))
    tmp_moran = list(map(get_moran_local, i))
    tmp_lisa = list(map(get_lisa_proportions, tmp_moran))
    tmp_data = list(map(lambda x, y: x + y, tmp_list, tmp_lisa))
    list_of_data.append(tmp_data)


# make single df
data = list(map(lambda x: pd.DataFrame(x, columns=['rep', 'gen', 'p_klepts',
                                     'p_handlers', 'p_forager',
                                     'HH', 'LH', 'LL', 'HL']),
                list_of_data))

# join all the data into a single dataframe
data = pd.concat(data)
data = pd.melt(data, id_vars=["gen", "rep"])

# write data to file
data.to_csv("data/data_strategy_lisa.csv", index=False)


# now plot the data in facets
plt.rcParams["font.family"] = "Arial"
fig = sns.FacetGrid(data, col="rep",
                    hue='variable',
                    # palette=['xkcd:red', 'xkcd:green', 'xkcd:blue'],
                    col_wrap = 3)
fig = fig.map(sns.lineplot, "gen", "value",
               linewidth = 1).add_legend()

fig.savefig(fname='figs/fig_example_strategy_per_gen.png',
            dpi=300,
            quality=90)
# ends here

