from cmath import nan
import os
import sys
import json
import math
import numpy as np
import scipy as sp
import scipy.ndimage
import matplotlib.pyplot as plt
from datetime import datetime
from tkinter import filedialog as fd
from matplotlib.colors import LinearSegmentedColormap

def get_custom_color_palette():
    return LinearSegmentedColormap.from_list("", [
        '#000000', '#222222', '#444444', '#555555', "#666666", "#777777",
        '#0052A2', '#00498D', '#00498D', '#205072', '#41a0ae', '#329D9C',
        '#4D8C57', '#78A161', '#A3B56B', '#CDCA74', '#F8DE7E', '#f5eb49',
        '#FEF001', '#FFCE03', '#FD9A01', '#FD6104', '#FF2C05', '#F00505'
    ])

def get_filedata(filename, jsonSource):
    with open(filename,'r+') as file:
        file_data = json.load(file)
    dict = file_data["pressureData"]
    inTime = datetime.strptime(correct_time(dict[0]["dateTime"]), '%Y-%m-%dT%H:%M:%S.%f').timestamp()
    pressureMatrices, timeData, timestamps = [], [], []
    for x in range(len(dict)):
        data = dict[x]["pressureMatrix"]
        arr = np.array(data, dtype=np.double)
        if jsonSource==1:
            arr = np.rot90(arr)
        elif jsonSource==2:
            arr = np.flip(arr, axis=0)
        arr[arr<300] = 0
        pressureMatrices.append(arr)
        currTime = correct_time(dict[x]["dateTime"])
        timeData.append(datetime.strptime(currTime, '%Y-%m-%dT%H:%M:%S.%f').timestamp() - inTime)
        timestamps.append(datetime.strptime(currTime, '%Y-%m-%dT%H:%M:%S.%f').strftime('%d %b %Y %H:%M:%S.%f'))
    pressureMatrices = np.dstack(pressureMatrices)
    timeData = np.asarray(timeData)
    timestamps = np.asarray(timestamps)
    return pressureMatrices, timeData, timestamps

def correct_slices(pressureMatrices, dataSlices):
    for ind in range(len(dataSlices)):
        x, y, z = dataSlices[ind]
        start = z.start
        end = z.stop
        for i in range (start, end):
            curr = pressureMatrices[i]
            curr = curr[x, y]
            if(np.any(curr)):
                start = i
                break
        for i in range(end, start, -1):
            curr = pressureMatrices[i]
            curr = curr[x, y]
            if(np.any(curr)):
                end = i+1
                break
        z = slice(start, end, None)
        dataSlices[ind] = list(dataSlices[ind])
        dataSlices[ind][2] = z
        dataSlices[ind] = tuple(dataSlices[ind])
    return dataSlices

def get_gait(timeData, dataSlices, timestamps):
    ax = plt.gca()
    print('\n', "-" * 137, sep='')
    print("| Start\t\t| End \t\t| Duration \t| Phase \t| Foot  |\t\t\t Timestamp \t\t\t\t|")
    print("-" * 137)
    swings = []
    stances = []
    for i, dat_slice in enumerate(dataSlices):
        dx, dy, dt = dat_slice
        foot = i%2 + 1
        if(i!=0 and i!=1):
            phase = "Swing"
            swingStart = dataSlices[i-2][2]
            dur = timeData[dt].min() - timeData[swingStart].max()
            print('|', '%.8f'%timeData[swingStart].max(), "\t|", '%.8f'%timeData[dt].min(), "\t|", '%.8f'%dur, "\t|", phase, "\t|", foot, end='')
            print("\t|", timestamps[swingStart.stop], " - ", timestamps[dt.start], "\t|")
            swings.append(dur)
        phase = "Stance"
        ax.barh(y=foot, width=timeData[dt].ptp(), height=0.2, left=timeData[dt].min(), align='center', color='red')
        print('|', '%.8f'%timeData[dt].min(), "\t|", '%.8f'%timeData[dt].max(), "\t|", '%.8f'%timeData[dt].ptp(), "\t|", phase, "\t|", foot, end='')
        print("\t|", timestamps[dt.start], " - ", timestamps[dt.stop], "\t|")
        stances.append(timeData[dt].ptp())
    print("-" * 137)
    ax.set_yticks(range(1, 3))
    ax.set_yticklabels(['Foot 1', 'Foot 2'])
    ax.set_xlabel('Time')
    ax.yaxis.grid(True)
    ax.set_title('Gait Cycle')
    cycles = min(len(stances), len(swings))
    percentages = [0, 0]
    avgStance = [0, 0]
    avgSwing = [0, 0]
    for i in range(cycles):
        percentages[i%2] += (stances[i]/(stances[i]+swings[i]))*100
        avgStance[i%2] += stances[i]
        avgSwing[i%2] += swings[i]
    if(cycles%2==0):
        n1 = (cycles)/2
        n2 = (cycles)/2
    else:
        n1 = (cycles+1)/2
        n2 = n1-1
    if(n1==0 or n2==0):
        print("Gait Metrics Cannot be Calculated for this Data")
        return
    print("\n\t\t Cycles \t Avg. Stance Phase \t\t Avg. Swing Phase \t\t Percentage Comparison")
    avgStance[0] /= n1
    avgSwing[0] /= n1
    percentages[0] /= n1
    avgStance[1] /= n2
    avgSwing[1] /= n2
    percentages[1] /= n2
    footCycles = [n1, n2]
    print("foot 1\t\t", int(n1), "\t\t", avgStance[0], "\t\t", avgSwing[0], "\t\t", '%.2f'%percentages[0], "|", '%.2f'%(100-percentages[0]))
    print("foot 2\t\t", int(n2), "\t\t", avgStance[1], "\t\t", avgSwing[1], "\t\t", '%.2f'%percentages[1], "|", '%.2f'%(100-percentages[1]))
    plt.show()
    return [footCycles, avgStance, avgSwing, percentages]

def correct_time(timestamp):
    size = len(timestamp)
    size -= 6
    timestamp = timestamp[:size]
    while(size<26):
        timestamp += '0'
        size += 1
    size = 26
    timestamp = timestamp[:size]
    return timestamp

def find_heels(pressureMatrices, dataSlices):
    stepCount = len(dataSlices)
    indices = []
    for i in range(stepCount):
        curr = pressureMatrices[dataSlices[i][2].start]
        curr = curr[dataSlices[i][0], dataSlices[i][1]]
        max = np.unravel_index(np.argmax(curr), curr.shape)
        max = list(max)
        max[0] = max[0] + dataSlices[i][0].start
        max[1] = max[1] + dataSlices[i][1].start
        indices.append(max)
    return indices

def find_foot(data, smoothRadius=5, threshold=0.0001):
    data = sp.ndimage.uniform_filter(data, smoothRadius)
    thresh = data > threshold
    filled = sp.ndimage.binary_fill_holes(thresh)
    codedFoot, numFoot = sp.ndimage.label(filled)
    dataSlices = sp.ndimage.find_objects(codedFoot)
    return dataSlices

def get_stride(pressureMatrices, timeData, dataSlices):
    points = find_heels(pressureMatrices, dataSlices)
    if(len(points)<4):
        print("Stride Metrics Cannot be Calculated for this Data")
        return
    step = [0, 0]
    vel = [0, 0]
    currStep = [points[0], points[1]]
    stepTime = [dataSlices[0][2].start, dataSlices[1][2].start]
    for i in range (2, len(points)):
        ind = i%2
        currDist = math.dist(currStep[ind], points[i])*2
        currTime = timeData[dataSlices[i][2].start] - timeData[stepTime[ind]]
        vel[ind] += (currDist/currTime)
        step[ind] += currDist
        currStep[ind] = points[i]
        stepTime[ind] = dataSlices[i][2].start
    if(len(points)%2==0):
        n1 = (len(points))/2  
        n2 = (len(points))/2  
    else:
        n1 = (len(points)+1)/2
        n2 = (len(points)-1)/2
    step[0] /= (n1-1)  
    step[1] /= (n2-1)
    vel[0] /= (n1-1)  
    vel[1] /= (n2-1)
    print("Avg. Stride Length of Foot1: ", step[0], "cm", end = '')
    print("\tAvg. Stride Velocity of Foot1: ", vel[0], "cm/s")
    print("Avg. Stride Length of Foot2: ", step[1], "cm", end = '')
    print("\tAvg. Stride Velocity of Foot2: ", vel[1], "cm/s")
    return [step, vel]

def plot_path(pressureMatrices, indices):
    ax = plt.gca()
    cmap = get_custom_color_palette()
    pressureMatrices = np.rollaxis(pressureMatrices, 0, 3)
    ax.imshow(pressureMatrices.sum(axis=2), cmap=cmap, interpolation='quadric')
    x, y = [], []
    for i in range(len(indices)):
        x0 = indices[i][1]
        y0 = indices[i][0]
        x.append(x0); y.append(y0)
        ax.annotate('Foot %i' % (i%2 +1), (x0, y0), color='red', ha='center', va='bottom')
    ax.plot(x, y, '-wo')
    ax.axis('image')
    ax.set_title('Steps')
    plt.show()

def get_cadence(timeData, dataSlices):
    timeElapsed = (timeData[dataSlices[-1][2].stop] - timeData[dataSlices[0][2].start]) / 60
    stepCount = len(dataSlices)
    cadence = stepCount / timeElapsed
    print("\nCadence: ", cadence)
    return cadence

def get_filename():
    filename = fd.askopenfilename()
    name = os.path.basename(filename)
    # Check if path is valid
    if(os.path.exists(filename) == False):
        print("File does not exist.")
        sys.exit("Exited")
    return filename

def multi_runs(pressureData, normalisedTimeData, timestamp, footRegions):
    footRegionRuns = []
    i=0
    runRegions = []
    for region in footRegions:
        x, y, z = region
        if(z.start >= runs[i][0] and z.stop <= runs[i][1]):
            runRegions.append(region)
        else:
            i+=1
            footRegionRuns.append(runRegions)
            runRegions = []
            runRegions.append(region)
    footRegionRuns.append(runRegions)
    cadenceValues = []
    strideValues = []
    gaitValues = []
    footLabel = []
    cadence = 0
    totalTime = 0
    avgStride = [[0, 0], [0, 0]]
    avgGait = [[0, 0], [0, 0], [0, 0], [0, 0]]
    for i in range(len(footRegionRuns)):
        print('\n\n', '-' * 10, '\n|', ' Run ', i+1, ' |\n', '-' * 10, sep='')
        pressureMatrix = pressureData[runs[i][0]:runs[i][1]]
        cadenceValues.append(get_cadence(normalisedTimeData, footRegionRuns[i]))
        strideValues.append(get_stride(pressureData, normalisedTimeData, footRegionRuns[i]))
        gaitValues.append(get_gait(normalisedTimeData, footRegionRuns[i], timestamp))
        indices = find_heels(pressureData, footRegionRuns[i])
        plot_path(pressureMatrix, indices)
        footLabel.append(input("\nEnter if (foot 1) is left [l/L] or right [r/R]: "))
        footLabel[i] = footLabel[i].lower()
        while footLabel[i] != 'l' and footLabel[i] != 'r':
            footLabel[i] = input("Option Does Not Exist. Retry: ")
            footLabel[i] = footLabel[i].lower()
        if(footLabel[i] == 'r'):
            strideValues[i][0][0], strideValues[i][0][1] = strideValues[i][0][1], strideValues[i][0][0]
            strideValues[i][1][0], strideValues[i][1][1] = strideValues[i][1][1], strideValues[i][1][0]
            for j in range(4):
                gaitValues[i][j][0], gaitValues[i][j][1] = gaitValues[i][j][1], gaitValues[i][j][0] 
    for i in range(len(footRegionRuns)):
        currRun = footRegionRuns[i]
        x1, y1, z1 = currRun[0]
        z1 = z1.start
        x2, y2, z2 = currRun[-1]
        z2 = z2.stop
        t = normalisedTimeData[z2] - normalisedTimeData[z1]
        totalTime += t
        cadence += (cadenceValues[i]*t)
        avgStride[0][0] += (strideValues[i][0][0]*t)
        avgStride[0][1] += (strideValues[i][0][1]*t)
        avgStride[1][0] += (strideValues[i][1][0]*t)
        avgStride[1][1] += (strideValues[i][1][1]*t)
        avgGait[0][0] += gaitValues[i][0][0]
        avgGait[0][1] += gaitValues[i][0][1]
        for j in range(1, 4):
            avgGait[j][0] += (gaitValues[i][j][0]*t)
            avgGait[j][1] += (gaitValues[i][j][1]*t)
    n = totalTime
    cadence /= n
    avgStride[0][0] /= n
    avgStride[0][1] /= n
    avgStride[1][0] /= n
    avgStride[1][1] /= n
    for j in range(1, 4):
        avgGait[j][0] /= n
        avgGait[j][1] /= n
    print('\n\n', '-' * 25, '\n|', ' Consolidated Metrics ', ' |\n', '-' * 25, sep='')
    print("\nCadence: ", cadence)
    print("Avg. Stride Length of Left  Foot: ", avgStride[0][0], "cm", end = '')
    print(" \tAvg. Stride Velocity of Left  Foot: ", avgStride[1][0], "cm/s")
    print("Avg. Stride Length of Right Foot: ", avgStride[0][1], "cm", end = '')
    print(" \tAvg. Stride Velocity of Right Foot: ", avgStride[1][1], "cm/s")
    print("\n\t\t Cycles \t Avg. Stance Phase \t\t Avg. Swing Phase \t\t Percentage Comparison")
    print("Left  foot\t", int(avgGait[0][0]), "\t\t", avgGait[1][0], "\t\t", avgGait[2][0], "\t\t", '%.2f'%avgGait[3][0], "|", '%.2f'%(100-avgGait[3][0]))
    print("Right foot\t", int(avgGait[0][1]), "\t\t", avgGait[1][1], "\t\t", avgGait[2][1], "\t\t", '%.2f'%avgGait[3][1], "|", '%.2f'%(100-avgGait[3][1]))
        

def single_run(pressureData, normalisedTimeData, timestamp, footRegions):
    get_cadence(normalisedTimeData, footRegions)
    get_stride(pressureData, normalisedTimeData, footRegions)
    get_gait(normalisedTimeData, footRegions, timestamp)
    indices = find_heels(pressureData, footRegions)
    plot_path(pressureData, indices)


filename = get_filename()

jsonSource = int(input("Enter JSON File Source (1 - Consolidator Script, 2 - Sensing Mat Software): "))
while jsonSource != 1 and jsonSource != 2:
    jsonSource = int(input("Option Does Not Exist. Retry: "))

pressureData, normalisedTimeData, timestamp = get_filedata(filename, jsonSource)

footRegions = find_foot(pressureData)
footRegions.sort(key=lambda data_slice: data_slice[2].start)
pressureData = np.rollaxis(pressureData, -1)
footRegions = correct_slices(pressureData, footRegions)

flag = 0
count = 0
runs = []

for i in range(len(pressureData)):
    if(np.any(pressureData[i])==1 and flag==0):
        start = i
        flag = 1       
    elif(np.any(pressureData[i])==0 and flag==1):
        count += 1
    if(count > 2):
        end = i
        count = 0
        flag = 0
        runs.append([start, end]) 

if(len(runs)>1):
    multi_runs(pressureData, normalisedTimeData, timestamp, footRegions)
else:
    single_run(pressureData, normalisedTimeData, timestamp, footRegions)

input("\nPress Any Key to Exit... ")