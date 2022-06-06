# **Pressure Data Logger**

This program reads JSON file produces by the consolidating script and creates an HTML file with timestamps and the corresponding pressure data visualization at that timestamp.


## **Installation**

Download the folder containing the following files. 
> converter.py <br>
> requirements.txt <br>
> script.py 

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements using terminal / command line in the directory of the program.

```bash
pip install -r requirements.txt
```


## **Usage**

First, a JSON file from the consolidating script has to be obtained. To run the program, open a terminal / command line in the directory of the program and then run the python script following the below template.

```bash
python script.py PATH_TO_JSON PATH_TO_OUTPUT
```

The HTML file with timestamps and visualizations will get stored in the provided path. This path should only specify upto the folder and not any filename. The PATH to JSON file must specify both the path and the filename.

## **Contributors**

*Hemachandran B*
