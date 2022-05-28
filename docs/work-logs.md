# Sensing Mat
Hemachandran B

## Week 1 [16 May 2022 - 21 May 2022]
### Monday
### Tuesday
### Wednesday
### Thursday
- Met Supervisor 
- Got Introduced to the Project
### Friday
- **Assigned task** to consolidate outputs from multiple sensing mats into a single JSON file
- Went through the documentation for Sensing Mat Development Kit
- Tested existing program with sensing mat
- made prototype version of program to receive output from multiple mats and output into single JSON
### Saturday
- Modified the program to make it more efficient and easier to use with multiple mats
- Tried different approach to store values in json
- searched for workarounds to fix json formatting
- Program is able to get data from mat and store it in a json file but not getting visualized properly

## Week 2 [23 May 2022 - 28 May 2022]
### Monday
- Checked different set of inputs and outputs to identify the correct way to format data matrix
- Orientations of visualizations were incorrect
- Changed configuration settings of json file to visualize values correctly
- Modified the way input is stored in the matrix when getting values from mat
- Time gap between two consecutive values reduced by removing sleep function call
- Program is working as intended and values getting stored in the json file are being visualized properly
### Tuesday
- Added functionality to accept command line arguments
- Organized program and JSON file to run using command line
- Created requirements file
- Documented the program
- updated files in repository
### Wednesday
- Studied concepts related to machine learning
- **Assigned Task** to work on calculating metrics from consolidated JSON
- Read documents on [paw labeling](http://www.flipserd.com/blog/page/1)
- Went through possible solutions to identity feet from matrix values
- Read documents on Eigenfaces approach
### Thursday
- Read Concepts on Morphology in Image Processing
- Searched for ways to identify size and orientation of foot
- Tried to manually visualize pressure matrix
### Friday
- Created python script to visualize pressure matrix in real-time
- Tried to apply opening and erosion operations to remove unnecessary values [resulted in loss of pressure data - not viable]
- Calculated local maxima to identify highest pressure points [Not perfect since multiple points are being calculated as local maxima]
- Plotted the identified points in real-time along with pressure matrix plot
### Saturday
- Labelled pressure points using scipy library and extracted the object slices based on the labels 
- Calculated regions of interest using the extracted objects and plotted the ROIs in real-time along with the pressure matrix
- Started working on Eigenfaces Approach
