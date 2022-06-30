# **Sensing Mat Metrics Calculator**

This program reads a JSON file produced either by the consolidator script or files recorded using the sensing mat analytics software and calculates the following metrics.
- Cadence
- Stride Length
- Stride Velocity
- Gait Cycle


## **Installation**

Download the folder containing the following files. 
> requirements.txt <br>
> script.py <br>

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements using terminal / command line in the directory of the program.

```bash
pip install -r requirements.txt
```

**Alternative method is to download and run the executable file**


## **Usage**

Run the script by using the following command in the directory where the script is present.

```bash
python script.py
```

The program will ask for the location of the JSON file which can be selected using a file explorer dialog box. 

In case the JSON file has been obtained using the consolidator script, input **1** has to be provided. If the JSON file has been recorded using the sensing mat analytics software, input **2** has to be given. This is done to eliminate the format issues between the different JSON files.


## **Overview of the Program**

This program reads a JSON file containing the pressure data and then identifies the foot details present in the pressure data, further using the identified foot data to calculate cadence by the number of feet present, stride length and velocity by calculating the distance between the heels of the different feet and finally gait cycle using time and foot data. This program also visualizes the foot and the path taken by the person walking on the pressure mat. Further, it can also identify if a person has walked out and then into the mat after an interval, dividing the data into different runs to accurately calculate the metrics.


## **Program**

### **Function Flow**

The functions present in the program get executed in the following order. <br>
1. Main code 
2. get_filename()
3. get_filedata()
4. correct_time()
5. find_foot()
6. correct_slices()
7. multi_runs() or single_run()
8. get_cadence()
9. get_stride()
10. get_gait()
11. find_heels()
12. plot_path()
13. get_custom_color_palette()

Each function and its specifics have been discussed below. 


#### **Main Code**

- Call get_filename() function and store the path in filename variable
- Get input from user if JSON is from Sensing Mat Software or Consolidator Script
- Call get_filedata() function and store the pressure and time data accordingly
- Call find_foot() function to calculate regions of the foot
- Sort the regions based on time
- Change te axis of pressureData to operate easily
- Call correct_slices() function to remove excess regions from the identified regions of the foot
- iterate through the pressureData to identify times when entire matrix is zero and split into runs if more then 2 consecutive empty matrices have been found
- If more than 1 run is present call multi_runs() function
- else call single_run() function 


#### **get_filename()**

- Parameters - N/A
- Return Values 
    - filename - contains path to JSON file
- Open tkinter dialog box to select the necessary JSON file
- Check if the chosen file is valid, exit program in case it is invalid
- return the path


## **Contributors**

Hemachandran B 
