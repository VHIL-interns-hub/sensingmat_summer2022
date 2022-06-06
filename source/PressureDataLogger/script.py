import os
import cv2
import sys
import json
import time
import logging
import numpy as np
import scipy as sp
import scipy.ndimage
import matplotlib.pyplot as plt
from datetime import datetime
from logging import FileHandler
from converter import VisualRecord
from matplotlib.colors import LinearSegmentedColormap


def get_custom_color_palette():
    return LinearSegmentedColormap.from_list("", [
        '#000000', '#222222', '#444444', '#555555', "#666666", "#777777",
        '#0052A2', '#00498D', '#00498D', '#205072', '#41a0ae', '#329D9C',
        '#4D8C57', '#78A161', '#A3B56B', '#CDCA74', '#F8DE7E', '#f5eb49',
        '#FEF001', '#FFCE03', '#FD9A01', '#FD6104', '#FF2C05', '#F00505'
    ])

def log_foot(dict):
    global name
    logger.debug("<h1 style=\"text-align: center;\">Pressure Data Log</h1>")
    name = "<h2 style=\"text-align: center;\"><i>( " + name + " )</i></h2><hr/>"
    logger.debug(name)
    cmap = get_custom_color_palette()
    print("Logging...")
    for x in range(len(dict)):
        imgList = []
        curr = dict[x]
        data = curr["pressureMatrix"]
        timeData = curr["dateTime"]
        timeData = datetime.strptime(timeData, '%Y-%m-%dT%H:%M:%S.%f%z')
        timeDataDate = timeData.strftime('%d %b %Y')
        timeDataTime = timeData.strftime('%H:%M:%S.%f')
        timeData = timeDataDate + ', ' + timeDataTime
        arr = np.array(data, dtype=np.double)
        arr = np.rot90(arr)
        arr[arr<100] = 0
        foot = find_foot(arr)
        for slice in foot:
            roi = arr[slice[0], slice[1]]
            #print(roi)
            img = plt.imshow(roi, cmap=cmap, interpolation='quadric')
            plt.axis('off')
            img.axes.get_xaxis().set_visible(False)
            img.axes.get_yaxis().set_visible(False)
            plt.savefig("plt.png", bbox_inches='tight', pad_inches = 0)
            img = cv2.imread("plt.png")
            imgList.append(img)
        logger.debug(VisualRecord(("%s" %(timeData)), imgs=imgList, fmt = "png"))
    os.remove("plt.png")

def find_foot(data, smooth_radius=5, threshold=0.0001):
    data = sp.ndimage.uniform_filter(data, smooth_radius)
    thresh = data > threshold
    filled = sp.ndimage.binary_fill_holes(thresh)
    coded_paws, num_paws = sp.ndimage.label(filled)
    data_slices = sp.ndimage.find_objects(coded_paws)
    return data_slices

# get command line arguments
filename = sys.argv[1]
name = os.path.basename(filename)
# Check if path is valid
if(os.path.exists(filename) == False):
    print("File does not exist.")
    sys.exit("Exited")

# get command line arguments
filePath = sys.argv[2]
# Check if path is valid
if(os.path.exists(filePath) == False):
    print("Invalid PATH.")
    sys.exit("Exited")

with open(filename,'r+') as file:
    file_data = json.load(file)
dict = file_data["pressureData"]

logFilename = filePath + "\PressureDataLog_" + time.strftime("%Y%m%d_%H%M%S") + ".html"
logger = logging.getLogger("Pressure_Data_log")
fh = FileHandler(logFilename, mode = "w")
logger.setLevel(logging.DEBUG)
logger.addHandler(fh)

log_foot(dict)

