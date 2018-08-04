from definitions import scale, get_all_sheets
from data import heat_map
from stats import calc, calc2
from plt import plot
from conf_int import conf_int_1, conf_int_2, conf_int_3
import glob
import csv
import os
import numpy as np

#user-defined inputs
folder = input(str("Define folder name (within quotations): "))
X_mm = input("Define the X-length of the tank in mm: ")
X_length = X_mm
# X_length = 200
dist = input("Define distance from wall in mm: ")
dist_from_wall = dist
# dist_from_wall = 20 
no_of_frames = input("Define the number of frames: ")
frames = no_of_frames + 10
# the frame_rate calculation assumes the data is collected over a 600 second (10min) period: can be changed if this changes by making it user-defined
frame_rate = no_of_frames/600.00

path = 'inputs/' + folder + '/'

header_1 = 'File name,Total time, ,Time %, ,Average velocity, ,Total distance, ,Total time, ,Time %, ,Average velocity, ,Total distance, ,Total time, ,Time %, ,Average velocity, ,Total distance, ,Total time, ,Time %, ,Average velocity, ,Total distance, ,Total time, ,Time %, ,Average velocity, ,Total distance, ,Latency for 1st entry,Latency for 2nd entry,No. of transitions to top half,Total freeze time,No. of freezing episodes,No. of darting episodes\n ,centre,wall,centre,wall,centre,wall,centre,wall,bottom 1/4,top 3/4,bottom 1/4,top 3/4,bottom 1/4,top 3/4,bottom 1/4,top 3/4,bottom 1/2,top 1/2,bottom 1/2,top 1/2,bottom 1/2,top 1/2,bottom 1/2,top 1/2,bottom 3/4,top 1/4,bottom 3/4,top 1/4,bottom 3/4,top 1/4,bottom 3/4,top 1/4,bottom 1/3,top 2/3,bottom 1/3,top 2/3,bottom 1/3,top 2/3,bottom 1/3,top 2/3\n'
with open(path + 'output/extracted_info.txt', 'w') as f:
	f.write(str(header_1))

header_2 = 'File name,% time in bottom 1/2, , , , , , , , , ,% time in bottom 1/4, , , , , , , , , ,% time in bottom 1/3, , , , , , , , , ,\n ,0-1 min,1-2 min,2-3 min,3-4 min,4-5 min,5-6 min,6-7 min,7-8 min,8-9 min,9-10 min,0-1 min,1-2 min,2-3 min,3-4 min,4-5 min,5-6 min,6-7 min,7-8 min,8-9 min,9-10 min,0-1 min,1-2 min,2-3 min,3-4 min,4-5 min,5-6 min,6-7 min,7-8 min,8-9 min,9-10 min, ,\n'
with open(path + 'output/time_calc.txt', 'w') as f:
	f.write(str(header_2))

os.chdir(path)
for filename in glob.glob('*.xls'):
	in_file = filename
	raw_file = 'raw/' + filename

	number = get_all_sheets(in_file, raw_file)
	pages = range(1, number+1)

	for i in pages:
		raw_sheet = raw_file + '_Tank_' + str(i) + '.xls'
		X_min, X_max, Y_min, Y_max, scaler = scale(X_length, raw_sheet, frames)

# important to not mess up:
		X0 = X_min + dist_from_wall
		Xn = X_max - dist_from_wall
		Y0 = Y_min + dist_from_wall
		Yn = Y_max - dist_from_wall
		Y_half = (Y_max - Y_min)/2
		Y_fourth = (Y_max - Y_min)/4
		Y_third = (Y_max - Y_min)/3
		Y_half_lim = Y_max - Y_half
		Y_fourth_lim = Y_max - Y_fourth
		Y_3fourth_lim = Y_max - 3*(Y_fourth)
		Y_third_lim = Y_max - Y_third

		file_name = raw_file + '_Tank_' + str(i)
		xls_input = raw_sheet + '.txt'
		heat_map(X0, Xn, Y0, Yn, xls_input, frame_rate, Y_half_lim, Y_fourth_lim, Y_3fourth_lim, Y_third_lim, file_name)

calc('output/Extracted_data.xls')
calc2('output/Extracted_data.xls')
plot('output/Extracted_data.xls')
conf_int_1('output/Extracted_data.xls')
conf_int_2('output/Extracted_data.xls')
conf_int_3('output/Extracted_data.xls')
