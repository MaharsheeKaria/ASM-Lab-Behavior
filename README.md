# trait-anxiety
Testing a project on automated analysis of trait anxiety in zebrafish using Python code.

Several experiments on fish have been performed using a certain set-up. The information from the experiments (coordinates of the fish, number of frames, etc.) get saved in .xls files. This project involves extracting valuable information from the data collected and analysing it. 

Prerequisites:
cycler==0.10.0, functools32==3.2.3.post2, matplotlib==2.0.2, numpy==1.13.1, pandas==0.20.3, pyparsing==2.2.0, python-dateutil==2.6.1, pytz==2017.2, scipy==0.19.1, seaborn==0.8, six==1.10.0, subprocess32==3.2.7

Running the tests: There are 6 scripts. You need to run the trait_anxiety.py script which will internally call upon the other 5 scripts. You need to store the raw .xls files in a folder named "inputs" and within this folder you need to create two other folders: "output" (where your final results will get saved) and "raw" (where the processing of the files will be done). trait_anxiety.py will prompt you to define certain values/terms in order to extract the information. These are the prompts you should expect with example answers:

Define folder name (within quotations): "ILR_DoubleMut"

Define the X-length of the tank in mm: 200

Define distance from wall in mm: 20

Define the number of frames: 18000

Define total data collection time in seconds: 600

Define data extraction start minute: 0

Define data extraction end minute: 10

# definitions.py
This script mainly involves segmenting the workbook into worksheets and scaling all the raw data into .txt files. All the information gets saved in the raw folder

# data.py
This is where all the raw data from the .txt files is manipulated and the output information is written in the output folder. This data is the final data that you will see in the Extracted_data.xls workbook.

# stats.py
The script uses the manipulated data and calculates the mean, standard deviation and 95% confidence intervals of all the data and writes it into the Extracted_data.xls workbook.

# plt.py
This plots information about time and distance using the data from the first sheet in the final excel file. Three plots are created through this which can be found in the output folder.

# conf_int.py
This script plots the remaining 3 graphs, also found in the output folder. These are representations of the information found in the second sheet of the final excel file. 
