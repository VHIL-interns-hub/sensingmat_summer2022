# **Sensing Mat Consolidator**

This program consolidates readings from multiple mats and stores it in a single JSON file which can then be visualized using Sensing Mat Analytics software.


## **Installation**

Download the folder containing the following files. 
> requirements.txt <br>
> script.py <br>
> template.json

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements using terminal / command line in the directory of the program.

```bash
pip install -r requirements.txt
```


## **Usage**

Connect the sensing mats to the USB ports of the device and note the serial ports (will be in the format COM#) being used in the order of the mats. To run the program, open a terminal / command line in the directory of the program and then run the python script following the below template.

```bash
python script.py PATH number_of_mats PORTS
```

The JSON file with the consolidated values will get stored in the provided path. This path should only specify upto the folder and not any filename. The PORTS should be given with spaces in between different ports. Below is an example where the JSON gets stored in "C:\Users\user\Desktop" with 2 mats connected in COM3 and COM4.

```bash
python script.py "C:\Users\user\Desktop" 2 COM3 COM4
```

The JSON file which is created by the program can be opened in the player present in Sensing Mat Analytics software which visualizes the data.


## **Overview**

This program connects to the sensing mat using serial port and requests data from the mat using Active Point Protocol. The data which is recieved from the mat in the form of a byte stream which follows the protocol is read by the program accordingly and the pressure values are stored in an array of size 48*(number of mats) x 48 with the indices provided by the mat. Once the data is read from all the connected mats and has been stored in the array, a dictonary with the current timestamp and the array of pressure values is created and appended to a list. This is repeated till the program is stopped. The working of the program has been discussed in detail below.


## **Program**

### **Function Flow**

The functions present in the program get executed in the following order. <br>
1. Main code 
2. getMatrix()
3. RequestPressureMap()
4. activePointsGetMap()
5. activePointsReceiveMap()
6. writeMatrix()
7. write_json()

Each function and its specifics have been discussed below.


#### **Main Code**

- Checks if the number of command line arguments are sufficient
- Gets command line arguments and stores it in necessary variables
- Checks for exceptions in the command line arguments
- Uses Serial function to initialize the ports in which mats are connected
- Initialized the number of rows and columns
- The number of rows are 48*(Number of mats)
- The number of columns are 48
- Creates an array of zeroes of size 48*(Number of mats) x 48
- Runs a loop without termination
    - Calls getMatrix() function
    - Calls writeMatrix() function
    - Check for keyboard input and exits loop is key 'q' is pressed
- Calls write_json() function


#### **getMatrix()**

- Parameters - N/A
- Return Values - N/A
- Iterates for x in range n where n = number of mats
    - Calls RequestPressureMap() function with ser[x] as parameter
    - Calls activePointsGetMap() function with ser[x], x as parameters


#### **RequestPressureMap(ser)**

- Parameters:
    - ser - object of type serial used to store serial connections
- Return Values - N/A
- Stores string 'R' in variable data
- write data to serial port which is connected to ser


#### **activePointsGetMap(ser, currMat)**

- Parameters:
    - ser - object of type serial used to store serial connections
    - currMat - index of the mat for which values are currently being read
- Return Values - N/A
- initializes an empty string with name xbyte
- Checks if there is any values to be read from the port
    - reads byte value from the port and decodes it
    - if the value follows the active point protocol function calls activePointsReceiveMap() with ser and currMat as parameters


#### **activePointsReceiveMap()**

- Parameters:
    - ser - object of type serial used to store serial connections
    - currMat - index of the mat for which values are currently being read
- Return Values - N/A
- assign offset as 48*currMat to store values in the array with proper index
- read byte value containing daa on number of points
- iterate till n is less than number of points sent by mat
    - read byte values from the serial port as per active point protocol and store necessary values such as coordinate and pressure values
    - store the pressure value in the coordinates and increment n value

**note:** Refer sensing mat developer guide for details on active points protocol. Here, the x coordinate will be used as the columns index and the y value added with the offset will be used as the row index. When multiple mats are connected, the array will expand along the row.


#### **writeMatrix()**

- Parameters - N/A
- Return Values - N/A
- Gets current timestamp in iso format and stores it
- Creates a new dictionary with timestamp data and array with pressure data as values
- The array is converted to list while initializing the dictionary
- The dictionary is appended to a list 


#### **write_json()**

- Parameters - N/A
- Return Values - N/A
- template.json file is opened and read
- The list of dictionaries is stored into another variable - writedata
- writedata is updated into the data read from the template.json file
- The path provided in command line is concatenated with filename containing timestamp
- This file is openened in write mode and the updated data is dumped into the file


### **Dependencies**

This program only stores the pressure data from the mats and does not visualize it. In order to visualize the data, Sensing Mat Analytics software has to be used to play the JSON file.   

The program also uses a JSON file as a template from which configuration data is read and the pressure data is appended with it which is then written into the target JSON file. The "rotateDegrees" and "flip" values have been changed to 0 in the configuration settings of the template file. Other configuration and calibration settings have been directly copied from the JSON file produced by the Sensing Mat Analytics software.

**Warning:** Changing the calibration or configuration settings in the template file can result in incorrect visualizations.


### **Mat Orientation**

The orientation and order of connecting the mats can alter the end result of the program. Therefore, the below format has to be followed to obtain proper results. The connector of the mat has to be on the top right and the additional mats have to be added to the right of the current mat. The mats should be ordered from left to right. 


### **Pressure Matrix Format**

The pressure matrix will have 48 columns and 48*(number of mats) rows. Therefore, as the number of mats increase, the number of rows will multply. When comparing the visualization and the raw pressure data matrix, the visualization will have 48*(number of mats) columns and 48 rows. Therefore, the orientation of the pressure matrix is a 90 degree clockwise rotation of the visualization.


## **Problems Encountered**

### **Multiple arrays approach**

- The initial approach was to read active points from each mat and store it in an array for each mat and then copy the values from multiple arrays into a single array of size 48 x 48(number of mats). 
- While using active points protocol, only the active points have to be stored in the provided coordinates. However, by using this method mutiple arrays of size 48x48 have to be iterated which increases the time delay between consecutive values. 
- Therefore, a single array in which the values will be stored using the coordinates from the active points protocol directly has been used. 
- To store values from multiple mats, an offset value has been used to correct the index of the values. 


### **JSON formatting**

- Storing list values fron python into JSON has resulted in formatting issues.
- Therefore, the indent parameter when writing into JSON has been removed. 


### **Matrix Orientation** 

- The initial size of the pressure matrix was taken as 48 x 48*(number of mats) i.e. the columns have been multiplied.
- However, this has caused issues since the visualization software rotated the matrix while visualizing.
- The visualization converted the 48 x 48*(number of mats) to 48 points in the x axis and 48*(number of mats) in the y axis.
- To resolve this, the matrix size has been changed to 48*(number of mats) x 48 i.e. the rows have been multiplied.


### **Calibration and Configuration in JSON**

- Even after changing the size of the matrix, the raw data did not get visualized as intended.
- This was due to the configuration settings present in the JSON file.
- The "rotateDegrees" and "flip" settings in the configuration have altered the way in which it was being visualized. 
- Therefore the values of "rotateDegrees" and "flip" have been changed from 90 and 2 respectively to 0.


### **Time Gap Between Consecutive Readings**

- Though the data was getting visualized properly, the time gap between consecutive values was high.
- Therefore, instead of updating JSON file with each reading, it has been changed to updating the JSON file at the end of the program.
- However, the issue was still present. It was then discovered that there was a sleep function call which made the program wait for 0.5 seconds between consecutive readings.
- Removing this had resolved this issue. 


## **Contributors**

*Hemachandran B* <br>
*Nisha Prakash*
