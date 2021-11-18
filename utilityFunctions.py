import cv2
import os
import numpy as np

# read all images in given folder, if recurse is true will also get all images in sub_folders of the given folder
# prints an error if cv2.imread() throws an exception
# it is valid for there to be non image files in the directories, this will ignore those
def read_images(folder, recurse):
    all_images = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            try:
                image = cv2.imread(file)
                if image is not None:
                    all_images.append(image)
            except:
                print("Attempted to open file: {}".format(file))
        if recurse:
            for dir in dirs:
                path_to_folder = os.path.join(folder, dir)
                recursive_images = read_images(path_to_folder, recurse)
                all_images = all_images + recursive_images
    return all_images