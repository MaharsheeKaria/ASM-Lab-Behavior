from definitions import scale, get_all_sheets
from data import heat_map
from stats import calc, calc2
from plt import plot
# from conf_int import conf_int_1, conf_int_2, conf_int_3
import glob
import csv
import os
import numpy as np

#user-defined inputs
folder = input(str("Define folder name (within quotations): "))
# folder = "ILR_DoubleMut"
path = 'inputs/' + folder + '/'
X_mm = input("Define the X-length of the tank in mm: ")
X_length = X_mm
# X_length = 200
dist = input("Define distance from wall in mm: ")
dist_from_wall = dist
# dist_from_wall = 20 
no_of_frames = input("Define the number of frames: ")
frames = no_of_frames + 10
total_time = input("Define total data collection time in seconds: ")
frame_rate = no_of_frames/total_time

start_end_time = input(str("Define data extraction start and end minutes (in brackets and comma spaced); Can define multiple time intervals (comma spaced): "))
# start_end_time = (0,5),(5,10)
og = os.getcwd()

loops = [start_end_time]
for i in loops:
	for a,b in i:
		start_ = (a)*(frame_rate*60) 
		start = start_ + 1
		# end_time = input(str("Define data extraction end minute: "))
		end = (b)*(frame_rate*60)
		name = str(a) + 'to' + str(b) + 'minutes'
		val = abs(end-start_) 

		header_1 = 'File name,Total time, ,Time %, ,Average velocity, ,Total distance, ,Total time, ,Time %, ,Average velocity, ,Total distance, ,Total time, ,Time %, ,Average velocity, ,Total distance, ,Total time, ,Time %, ,Average velocity, ,Total distance, ,Total time, ,Time %, ,Average velocity, ,Total distance, ,Latency for 1st entry,Latency for 2nd entry,No. of transitions to top half,Total freeze time,No. of freezing episodes,No. of darting episodes\n ,centre,wall,centre,wall,centre,wall,centre,wall,bottom 1/4,top 3/4,bottom 1/4,top 3/4,bottom 1/4,top 3/4,bottom 1/4,top 3/4,bottom 1/2,top 1/2,bottom 1/2,top 1/2,bottom 1/2,top 1/2,bottom 1/2,top 1/2,bottom 3/4,top 1/4,bottom 3/4,top 1/4,bottom 3/4,top 1/4,bottom 3/4,top 1/4,bottom 1/3,top 2/3,bottom 1/3,top 2/3,bottom 1/3,top 2/3,bottom 1/3,top 2/3\n'
		with open(path + 'raw/extracted_info.txt', 'w') as f:
			f.write(str(header_1))

		header_3 = 'File name, Latency for 1st entry,\n\n'
		with open(path + 'raw/lat1.txt', 'w') as f:
			f.write(str(header_3))

		header_4 = 'File name, Latency for 2nd enter,\n\n'
		with open(path + 'raw/lat2.txt', 'w') as f:
			f.write(str(header_4))

		header_5 = 'File name,No. of transitions to top half,No. of darting episodes,\n\n'
		with open(path + 'raw/dart_trans.txt', 'w') as f:
			f.write(str(header_5))

		header_6 = 'File name, Time%,\n, ,centre,wall,\n'
		with open(path + 'raw/time_wall.txt', 'w') as f:
			f.write(str(header_6))

		os.chdir(path)
		for filename in glob.glob('*.xls'):
			in_file = filename
			raw_file = 'raw/' + filename

			number = get_all_sheets(in_file, raw_file)
			pages = range(1, number+1)

			for i in pages:
				raw_sheet = raw_file + '_Tank_' + str(i) + '.xls'
				X_min, X_max, Y_min, Y_max, scaler = scale(X_length, raw_sheet, frames, start, end)

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
				XY = heat_map(X0, Xn, Y0, Yn, xls_input, frame_rate, Y_half_lim, Y_fourth_lim, Y_3fourth_lim, Y_third_lim, file_name, name)

		calc("output/Extracted_data_" + name + ".xls")
		plot("output/Extracted_data_" + name + ".xls", name)
		os.chdir(og)
