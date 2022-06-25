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


## Week 3 [30 May 2022 - 04 June 2022]
### Monday
- Had meeting with SERC Team
- Temporarily stopped working on Eigenfaces as image data is to be built first
- Built prototype of logging program which logs the json file into a html file with timestamps and images
### Tuesday
- Worked on formatting the html file with timestamps and images
- Searched for methods to enable labelling images in log
### Wednesday
- Added user editable captions under images in html log
- Modified html style for better usability
- Added indicators when there is no image at a timestamp
- Modified logging script to be able to run from command line
### Thursday
- Modified logging script to make it easier to understand
- Started documenting logging script
### Friday
- Searched for ways to orient feet pressure data before being processed for eigenfaces approach 
- Labelled pressure data images which can be used for eigenfaces approach
### Saturday
- Looked for methods to overcome issues when implementing Eigenfaces approach

## Week 4 [06 June 2022 - 11 June 2022]
### Monday
- Updated script for logging pressure data in github along with requirements file 
- Searched and found a method to overcome identification of foot pressure data at intial and final contact
- Started implementaion of the approach where ROI size is used to determine if eigenfaces can be applied at said timestamp
### Tuesday
- Worked on implementing the previosuly mentioned approach
### Wednesday
- Implemented prototype of the above method - calculated amount of time / time period the foot is being placed
- Identified alternate method to apply eigenfaces on only complete foot 
  - previously identified method depended on calculating roi with maximum area in the time period of the foot being placed in the mat
  - In the new method, the pressure matrices in the time period of foot being placed can be added together and eigen faces can be applied on that
  - Only initial part of the implementation is done for both the above methods
- Another possible method to find stride length would be to assign labels such as foot 1 and foot 2 and just calculate stride length for pressure data with labels foot 1 / foot 2 instead of having to identify if the foot is left or right 
- Created python script to convert text file with pressure data from 30x30 matrix into JSON file
- Modified existing logging and visualizing program to make it work with 30x30 matrix data
### Thursday
- Started implementing the method to calculate stride length without identifying the foot
- Calculated the path of travel by combining all the matrices and identifying the centers of roi of each foot
- Calculated cadence from the combined data and timestamps
### Friday
- Finished the above implementation with approximate results
- Calculated approximate stride length by taking the center of roi and calculating distance between alternate foot centers
- Have not identified / differentiated left or right foot and calculated only based on assumption that foot being placed in the mat are alternating
### Saturday
- Searched for methods to make stride length more accurate by using point of contact of heel instead of center of foot
- Converted stride length from units of the matrix to cm

## Week 5 [13 June 2022 - 18 June 2022]
### Monday
- Worked on making stride length more accurate
- Modified logging script to make it work with JSON file produced by sensing mat analytics software
  - Data recorded by the software is of different orientation from the consolidating script
  - The microseconds in timestamp stored by the software consists of varying digits while the consolidating script only uses microseconds upto 6 digits, this caused issue with parsing the timestamp
- Created a python notebook file with logging and gait stance phase scripts in order to make it easier to use
### Tuesday
- Sick - Day Off
### Wednesday
- Worked on making stride length more accurate - found an issue where the initial or final timings of a step are not accurate
- Encountered issue with logging program when using json file from sensing mat analytics software - number of digits in timestamps vary - made a function to correct the digits
- Added timestamp to stance phase timings
- Identified inaccuracy in stance phase reading - should be corrected along with step accuracy
### Thursday
- Corrected the intial and final readings of every step by checking for non zero readings in the region of the step at the start and end of duration
- Calculated the highest pressure point at the start of a step to measure stride length more accurately
- Improved stride length accuracy using higest pressure point reading. However, there is an issue where the heel might not be the highest pressure point at the start of a step therefore making the stride length measure a bit inaccurate
### Friday
- Searched for methods to overcome issue where pressure point other than heel is being chosen for stride length
- Calculated stride velocity using distance of each stride and time taken
### Saturday
- Studied about stride length due to an issue - when walking in a straight path and making a 180 degree turn to walk again, the stride length calculation is getting affected since the distance between the two steps are very less. Therefore, searched for possible methods to eliminate this issue.

## Week 6 [20 June 2022 - 25 June 2022]
### Monday
- Worked on calculating swing phase of gait cycle
- Made the gait metrics more presentable
### Tuesday
- Worked on calculating gait cycle percentage and averages
- tested the programs with 3 mats connected
- identified issue with calculating metrics when person walks out of the mat and walks in again resulting in irregular order of foot
- Made gait cycle values more accurate by similar method used for stride length
- Started consolidating all separate scripts into single program
### Wednesday
- Consolidated all separate scripts into single program
- Worked on reducing redundant code and making the code modular
### Thursday
- Srishti intern field trip - Day Off
### Friday
- Had meeting with SERC Team
- Created an executable file of the metrics script
- Started implementation to overcome issue where a person walking out of the mat and then into it again can cause incorrect metrics
### Saturday
- Modified the program to check for when the person walks out of the mat and separate the matrices into different runs based on that
- Calculated the metrics for each run individually from the separated matrices
