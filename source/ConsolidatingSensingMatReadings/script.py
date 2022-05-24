'''
Program has to be run from command line with the following format
"python script.py PATH number_of_mats PORTS"

All the lines which print the time taken for read cycle have been commented out.
In case of any testing these can be removed.

'''

from datetime import datetime
import numpy as np
import keyboard
import serial
import sys
import os
import time
import json

# JSON file name
filename=''

# Number of Mats Connected
numMats = 1

# Ports used to connect the mats in order
ports = ['COM3']

# Store Serial connections
ser = []

# store list of dictionaries containing timestamp and pressure data
data = []

# request the mat to send active pressure points
def RequestPressureMap(ser):
    data = "R"
    ser.write(data.encode())

# function to get values and store it in array
def activePointsReceiveMap(ser, currMat):
    global Values
    # calculate offset for storing vlaues in array based on current mat
    offset = 48*currMat
    # read values according to the active points protocol
    xbyte = ser.read().decode('utf-8')
    HighByte = ser.read()
    LowByte = ser.read()
    high = int.from_bytes(HighByte, 'big')
    low = int.from_bytes(LowByte, 'big')
    nPoints = ((high << 8) | low)
    xbyte = ser.read().decode('utf-8')
    xbyte = ser.read().decode('utf-8')
    x = 0
    y = 0
    n = 0
    # iterate till all the points sent is read and stored in array
    while(n < nPoints):
        x = ser.read()
        y = ser.read()
        x = int.from_bytes(x, 'big')
        y = int.from_bytes(y, 'big')
        HighByte = ser.read()
        LowByte = ser.read()
        high = int.from_bytes(HighByte, 'big')
        low = int.from_bytes(LowByte, 'big')
        val = ((high << 8) | low)
        Values[y+offset][x] = val
        n += 1

# Check for input and call function to read point if number of points mentioned
def activePointsGetMap(ser, currMat):
    xbyte = ''
    # check for input in serial port
    if ser.in_waiting > 0:
        try:
            xbyte = ser.read().decode('utf-8')
        except Exception:
            print("Exception")
        if(xbyte == 'N'):
            activePointsReceiveMap(ser, currMat)
        else:
            ser.flush()

class Null:
    def write(self, text):
        pass
    def flush(self):
        pass

# Call functions to request and get pressure values
def getMatrix():
    for x in range(numMats):
        #startTime = time.time()
        RequestPressureMap(ser[x])
        activePointsGetMap(ser[x], x)
        #endTime = time.time()
        #print("Time Taken for Mat ", x+1, ": ", '{:.8f}'.format(endTime-startTime), "s")

# function to write all values to JSON
def write_json():
    with open("template.json",'r+') as file:
        # loading data into a dict
        file_data = json.load(file)
        # add list of dictionaries into existing data
        writeData = {"pressureData": data}
        file_data.update(writeData)
        file.seek(0)
        # convert back to json.
        writeFilename = filename + "\SensingMatData_" + time.strftime("%Y%m%d_%H%M%S") + ".json"
        with open(writeFilename, 'w') as writeFile:
            json.dump(file_data, writeFile)
        print("File saved at PATH:", writeFilename)

# Append dictionary containing timestamp and current pressure matrix to list
def writeMatrix():
    global Values
    #startTime = time.time()
    # get current timestamp
    timestampData = datetime.now().astimezone().isoformat()
    # make a dictionary with timestamp and list of pressure values
    newEntry = {
        "dateTime": timestampData,
		"pressureMatrix": Values.tolist()
    }
    data.append(newEntry)
    #endTime = time.time()
    #print("Time Taken to store matrix: ", '{:.8f}'.format(endTime-startTime), "s \n")

# Check number of arguments
if(len(sys.argv) < 4):
    print("Insufficient Parameters.\nEnter in the form \"python script.py \"PATH\" number_of_mats \'PORTS\'\"")
    sys.exit("Exited")
print("Started")

# get command line arguments
filename = sys.argv[1]
# Check if path is valid
if(os.path.exists(filename) == False):
    print("PATH does not exist.")
    sys.exit("Exited")

# Check for number of mats
try:
    numMats = int(sys.argv[2])
except Exception:
    print("Invalid Parameters.\nEnter in the form \"python script.py \"PATH\" number_of_mats \'PORTS\'\"")
    sys.exit("Exited")
if(len(sys.argv) != numMats+3):
    print("Insufficient Parameters.\nEnter in the form \"python script.py \"PATH\" number_of_mats \'PORTS\'\"")
    sys.exit("Exited")

# Connect to serial
for x in range(numMats):
    try:
        ser.insert(x, serial.Serial(sys.argv[x+3], baudrate=115200, timeout=0.1))
    except Exception:
        print("Invalid Ports.")
        sys.exit("Exited")
print("Ports Inserted")

# Final matrix size
ROWS = 48*numMats
COLS = 48

# initialize array of zeroes to store pressure values
Values = np.zeros((ROWS, COLS))

# Main
print("Running...\n\n[Press \'q\' to Stop Reading Values]\n")
while True:
    #startTime = time.time()
    getMatrix()
    #endTime = time.time() 
    #print("Total Time to get Matrix: ", '{:.8f}'.format(endTime-startTime), "s")
    writeMatrix()
    Values = np.zeros((ROWS, COLS))
    if keyboard.is_pressed('q'):   
        break
    time.sleep(0.05)

print("Writing to JSON")
#startTime = time.time()
write_json()
#endTime = time.time()
#print("Time Taken to write to JSON File: ", '{:.8f}'.format(endTime-startTime), "s \n")
print("\nFinished\n")