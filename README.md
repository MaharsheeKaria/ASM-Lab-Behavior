# trait-anxiety
Testing a project on automated analysis of trait anxiety in zebrafish using Python code.

Several experiments on fish have been performed using a certain set-up. The information from the experiments get saved in .xls files. This project involves extracting valuable information from the data collected. All information that is extracted gets saved in one particular .xls file called Extracted_data.xls. 

Set-up of experiment: 
A fish is placed into a tank of certain dimensions and it’s behaviour is recorded over time under different experiemental set-ups. Data about the coordinates of the fish, number of frames, etc. is obtained from the recording and is saved in raw .xls files. 

Prerequisites:
•	cycler==0.10.0
•	functools32==3.2.3.post2
•	matplotlib==2.0.2
•	numpy==1.13.1
•	pandas==0.20.3
•	pyparsing==2.2.0
•	python-dateutil==2.6.1
•	pytz==2017.2
•	scipy==0.19.1
•	seaborn==0.8
•	six==1.10.0
•	subprocess32==3.2.7

Running the tests:
There are 6 scripts. You need to run the trait_anxiety.py script which will internally call upon the other 5 scripts.