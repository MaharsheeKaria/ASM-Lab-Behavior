# trait-anxiety
Testing a project on automated analysis of trait anxiety in zebrafish using Python code.

Several experiments on fish have been performed using a certain set-up. The information from the experiments (coordinates of the fish, number of frames, etc.) get saved in .xls files. This project involves extracting valuable information from the data collected and analysing it. 

Prerequisites:
cycler==0.10.0, functools32==3.2.3.post2, matplotlib==2.0.2, numpy==1.13.1, pandas==0.20.3, pyparsing==2.2.0, python-dateutil==2.6.1, pytz==2017.2, scipy==0.19.1, seaborn==0.8, six==1.10.0, subprocess32==3.2.7

Running the tests: There are 6 scripts. You need to run the trait_anxiety.py script which will internally call upon the other 5 scripts. You need to store the raw .xls files in a folder named "inputs" and within this folder you need to create two other folders: "output" (where your final results will get saved) and "raw" (where the processing of the files will be done). trait_anxiety.py will prompt you to define certain values/terms in order to extract the information. These are the prompts you should expect with example answers in bold:

Define folder name (within quotations): **"ILR_DoubleMut"**

Define the X-length of the tank in mm: **200**

Define distance from wall in mm: **20**

Define the number of frames: **18000**

Define total data collection time in seconds: **600**

# definitions.py
This script mainly involves segmenting the workbook into worksheets and scaling all the raw data into .txt files. All the information gets saved in the raw folder. It also scans the data to find X-min, X-max, Y-min, Y-max values. 

# data.py
This is where all the raw data from the .txt files is manipulated and the output information is written in the output folder. This data is the final data that you will see in the Extracted_data.xls workbook. This script also accounts for information in the raw files that may not have any valuable information in them.

It makes the following calculations in the first sheet called 'Extracted data': 
Total time, % time, Average velocity, Total distance - at the centre, wall, bottom 1/4, top 3/4, bottom 1/2, top 1/2, bottom 3/4, top 1/4, bottom 1/3, top 2/3 - Latencies, Transitions, Total freezing time, Number of freezing episodes, Number of darting episodes

It makes the following calculations through sheets 2-8: Time in bottom third; Latency for first entry; Latency for second entry; Transitions; Darting; Time at Wall; Time at Centre

# stats.py
The script uses the manipulated data and calculates the mean, standard deviation and 95% confidence intervals of all the data and writes it into the Extracted_data.xls workbook.

# plt.py
This plots information about time and distance using the data from the first sheet in the final excel file. Three plots are created through this which can be found in the output folder - one visual representation graph, one scatterplot representing mean and standard deviation along with the individual points, and one stacked bar graph showing the different conditions vs percentage time.

# conf_int.py
This script plots the remaining graph, also found in the output folder. This is a representation of the information found in the sixth sheet of the final excel file. The graph plots % time spent in the bottom third of the tank along with 95% confidence interval.

# multiple_trait_anxiety.py
This script is essentially identical to the trait_anxiety script. However, it allows the user to input multiple time interval values and then runs the scripts on loop. This saves the user time from having to recall the scripts again and again when testing for different time intervals. Like trait_anxiety, this script also prompts you to define certain values/terms in order to extract the information. These are the prompts you should expect with example answers in bold:

Define folder name (within quotations): **"ILR_DoubleMut"**

Define the X-length of the tank in mm: **200**

Define distance from wall in mm: **20**

Define the number of frames: **18000**

Define data extraction start and end minutes (in brackets and comma spaced); Can define multiple time intervals (comma spaced): **(0,2),(2,4),(4,6),(6,8),(8,10),(0,5),(5,10)**

This script however, gives you only the first sheet that trait_anxiety.py gives. 
