import numpy as np
import csv
from xlrd import open_workbook
import xlwt
from xlutils.copy import copy

def find_transitions(lst, lim):
	c = 0
	for n in lst:
		if n>=lim:
			a = lst.index(n) + 1
			try:
				if lst[a]<lim:
					c += 1	
			except (IndexError):
				pass
	return c

def find_darts(lst, lim, sd):
	c = 0
	for n in lst:
		if n>((8*sd)+lim):
			c += 1 
	return c

def find_repeats(L, repeats):
	idx = 0
	while idx < len(L):
		if [L[idx]]*repeats == L[idx:idx+repeats]:
			L[idx:idx+repeats] = ["True"]
			idx += repeats
		else:
			idx += 1 
	return L.count("True")

def find_freeze(lst, frame_rate):
	c = 0
	for i in range(len(lst)):
		if lst[i-1] == lst[i]:
			c += 1
	return c/frame_rate

def nonzero(lst):
	for i in range(len(lst)):
		if lst[i] == 0:
			lst[i] = lst[i-1]
	return lst

def nonzero2(lst):
	for i in range(len(lst)):
		if lst[i] == (0,0):
			lst[i] = lst[i-1]
	return lst

def chunks(l, n):
	for i in xrange(0, len(l), n):
		yield l[i:i+n]

def latencies(lim, big_list, frame_rate):
	i = 0
	ans = [0, 0]
	hit_bottom = False
	for j in range(len(big_list)):
		if i == 2:
			break
		if not hit_bottom:
			if all_satisfy(big_list[j:j+10], lambda x : x >= lim):
				hit_bottom = True
			continue
		if all_satisfy(big_list[j:j+10], lambda x : x < lim):
			ans[i] = j
			i += 1
			hit_bottom = False			
	return (ans[0]+1)/frame_rate, (ans[1]+1)/frame_rate


def all_satisfy(lst, fn):
	for i in lst:
		if not fn(i[1]):
			return False
	return True

def avg(lst):
	mean = str(np.mean(lst))
	return mean

def time(lst, frame_rate):
	total_time = str(len(lst)/frame_rate)
	return total_time

def find_vel_dist(frame_rate, X, Y):
	X = np.array(X)
	Y = np.array(Y)
	V, S = [],[]
	V.append(0.0001)
	S.append(0.0001)
	Vx = (X[1:] - X[:-1]) * frame_rate
	Vy = (Y[1:] - Y[:-1]) * frame_rate
	Vx2 = (Vx)**2
	Vy2 = (Vy)**2
	V.extend(np.sqrt(Vx2 + Vy2))
	S.extend((np.sqrt(Vx2 + Vy2))/frame_rate)
	return V, S

def all_not_zero(lst):
	for x, y in lst:
		if x + y < 0.0000001:
			return False
	return True

def float_if_possible(strg):
    try:
        return float(strg)
    except ValueError:
        return strg

def heat_map(X0, Xn, Y0, Yn, input_file, frame_rate, Y_half_lim, Y_fourth_lim, Y_3fourth_lim, Y_third_lim, file_name, name):
	XY = []
	with open(input_file, 'r') as f:
		f.readline()
		for l in f.readlines():
			row=l.split(",")
			XY.append((float((row[0].strip())), (float(row[1].strip()))))

# getting rid of invalid files:
	num_zeros = 0
	for x, y in XY:
		if x + y <= 0.0000001:
			num_zeros += 1
	if float(num_zeros)/len(XY) > 0.75:
		with open(input_file, 'w') as out:
			out.write('More than 75%% of values were zero. Did not process file.')
		return

# getting rid of invalid data:
	start = 0
	for i in range(5, len(XY)):
		if all_not_zero(XY[i-5:i]):
			start = i - 5	
			break
	X_new, Y_new, XY_new, episode_lst = [],[],[],[]
	with open(input_file, 'r') as out:
 		i = 0
 		for x, y in XY:
			if i < start:
 				i += 1
 				continue
			X_new.append(x)
			Y_new.append(y)
			XY_new.append((x, y))
			episode_lst.append((x, y))

# freeze episode, freeze time: comment here about no. of frames
	freeze_ep = find_repeats(episode_lst, 10)
	freeze_time = find_freeze(episode_lst, frame_rate)

# getting rid of 0 vals:
	XY = nonzero2(XY_new)
	X = nonzero(X_new)
	Y = nonzero(Y_new)

	V, S = find_vel_dist(frame_rate, X, Y)

# darting episodes:	
	mean_V = np.mean(V)
	sd_V = np.std(V)
	darts = find_darts(V, mean_V, sd_V)

# transitions:
	transitions = find_transitions(Y, Y_half_lim)
 
	with open(input_file, 'w') as out:
		writer = csv.writer(out, delimiter=",")
		writer.writerow(['X, Y, Velocity, Distance'])
	with open(input_file, 'a') as out:
		writer = csv.writer(out, delimiter=",")
		for x, y, v, s in zip(X, Y, V, S):
			writer.writerow([x, y, v, s])

# latency:
	latency1, latency2 = latencies(Y_half_lim, XY, frame_rate)

# centre/wall:
	XY_centre, V_centre, XY_boundary, V_boundary, S_centre, S_boundary = [],[],[],[],[],[]
	for (X, Y), v, s in zip(XY, V, S):		
		if X>=X0 and X<=Xn and Y>=Y0 and Y<=Yn:
			XY_centre.append((X, Y))
			V_centre.append(v)
			S_centre.append(s)
		else:
			XY_boundary.append((X, Y))
			V_boundary.append(v)
			S_boundary.append(s)

	time_centre = float(time(XY_centre, frame_rate))
	avgV_centre = float(avg(V_centre))
	sumS_centre = float(sum(S_centre))
	time_boundary = float(time(XY_boundary, frame_rate))
	avgV_boundary = float(avg(V_boundary))
	sumS_boundary = float(sum(S_boundary))
	time_centre_perc = (time_centre/(time_centre+time_boundary))*100
	time_boundary_perc = 100 - time_centre_perc

# bottom/top:
	XY_bottom_third, XY_top_2third, XY_bottom_half, XY_top_half, XY_bottom_fourth, XY_top_3fourth, XY_bottom_3fourth, XY_top_fourth, V_bottom_half, V_top_half, V_bottom_fourth, V_top_3fourth, V_bottom_3fourth, V_top_fourth, V_bottom_third, V_top_2third, S_bottom_half, S_top_half, S_bottom_fourth, S_top_3fourth, S_bottom_3fourth, S_top_fourth, S_bottom_third, S_top_2third = [],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]
	for (X, Y), v, s in zip(XY, V, S):
		if Y>=Y_half_lim:
			XY_bottom_half.append((X, Y))
			V_bottom_half.append(v)
			S_bottom_half.append(s)
		else:
			XY_top_half.append((X, Y))
			V_top_half.append(v)
			S_top_half.append(s)
		if Y>=Y_fourth_lim:
			XY_bottom_fourth.append((X, Y))
			V_bottom_fourth.append(v)
			S_bottom_fourth.append(s)
		else:
			XY_top_3fourth.append((X, Y))
			V_top_3fourth.append(v)
			S_top_3fourth.append(s)
		if Y>=Y_3fourth_lim:
			XY_bottom_3fourth.append((X, Y))
			V_bottom_3fourth.append(v)
			S_bottom_3fourth.append(s)
		else:
			XY_top_fourth.append((X, Y))
			V_top_fourth.append(v)
			S_top_fourth.append(s)
		if Y>=Y_third_lim:
			XY_bottom_third.append((X, Y))
			V_bottom_third.append(v)
			S_bottom_third.append(s)
		else:
			XY_top_2third.append((X, Y))
			V_top_2third.append(v)
			S_top_2third.append(s)

	time_bottom_half = float(time(XY_bottom_half, frame_rate))
	avgV_bottom_half = float(avg(V_bottom_half))
	sumS_bottom_half = float(sum(S_bottom_half))
	time_top_half = float(time(XY_top_half, frame_rate))
	avgV_top_half = float(avg(V_top_half))
	sumS_top_half = float(sum(S_top_half))
	time_bottom_fourth = float(time(XY_bottom_fourth, frame_rate))
	avgV_bottom_fourth = float(avg(V_bottom_fourth))
	sumS_bottom_fourth = float(sum(S_bottom_fourth))
	time_top_3fourth = float(time(XY_top_3fourth, frame_rate))
	avgV_top_3fourth = float(avg(V_top_3fourth))
	sumS_top_3fourth = float(sum(S_top_3fourth))
	time_bottom_3fourth = float(time(XY_bottom_3fourth, frame_rate))
	avgV_bottom_3fourth = float(avg(V_bottom_3fourth))
	sumS_bottom_3fourth = float(sum(S_bottom_3fourth))
	time_top_fourth = float(time(XY_top_fourth, frame_rate))
	avgV_top_fourth = float(avg(V_top_fourth))
	sumS_top_fourth = float(sum(S_top_fourth))
	time_bottom_third = float(time(XY_bottom_third, frame_rate))
	avgV_bottom_third = float(avg(V_bottom_third))
	sumS_bottom_third = float(sum(S_bottom_third))
	time_top_2third = float(time(XY_top_2third, frame_rate))
	avgV_top_2third = float(avg(V_top_2third))
	sumS_top_2third = float(sum(S_top_2third))

	time_bottom_half_perc = (time_bottom_half/(time_bottom_half+time_top_half))*100
	time_top_half_perc = 100 - time_bottom_half_perc
	time_bottom_fourth_perc = (time_bottom_fourth/(time_bottom_fourth+time_top_3fourth))*100
	time_top_3fourth_perc = 100 - time_bottom_fourth_perc
	time_bottom_3fourth_perc = (time_bottom_3fourth/(time_bottom_3fourth+time_top_fourth))*100
	time_top_fourth_perc = 100 - time_bottom_3fourth_perc
	time_bottom_third_perc = (time_bottom_third/(time_bottom_third+time_top_2third))*100
	time_top_2third_perc = 100 - time_bottom_third_perc
	empty = []

	table = [file_name, time_centre, time_boundary, time_centre_perc, time_boundary_perc, avgV_centre, avgV_boundary, sumS_centre, sumS_boundary, time_bottom_fourth, time_top_3fourth, time_bottom_fourth_perc, time_top_3fourth_perc, avgV_bottom_fourth, avgV_top_3fourth, sumS_bottom_fourth, sumS_top_3fourth, time_bottom_half, time_top_half, time_bottom_half_perc, time_top_half_perc, avgV_bottom_half, avgV_top_half, sumS_bottom_half, sumS_top_half, time_bottom_3fourth, time_top_fourth, time_bottom_3fourth_perc, time_top_fourth_perc, avgV_bottom_3fourth, avgV_top_fourth, sumS_bottom_3fourth, sumS_top_fourth, time_bottom_third, time_top_2third, time_bottom_third_perc, time_top_2third_perc, avgV_bottom_third, avgV_top_2third, sumS_bottom_third, sumS_top_2third, latency1, latency2, transitions, freeze_time, freeze_ep, darts, empty]

	lat1 = [file_name, latency1]
	lat2 = [file_name, latency2]
	dart_trans = [file_name, transitions, darts]
	time_wall = [file_name, time_centre_perc, time_boundary_perc]

	with open('raw/extracted_info.txt', "a") as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerow(table)

	with open('raw/lat1.txt', 'a') as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerow(lat1)

	with open('raw/lat2.txt', 'a') as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerow(lat2)

	with open('raw/dart_trans.txt', 'a') as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerow(dart_trans)

	with open('raw/time_wall.txt', 'a') as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerow(time_wall)

	data1 = []
	with open('raw/extracted_info.txt', 'r') as f:
		for line in f:
			data1.append([word for word in line.split(",") if word])
	data2 = []
	with open('raw/lat1.txt', 'r') as f:
		for line in f:
			data2.append([word for word in line.split(",") if word])
	data3 = []
	with open('raw/lat2.txt', 'r') as f:
		for line in f:
			data3.append([word for word in line.split(",") if word])
	data4 = []
	with open('raw/dart_trans.txt', 'r') as f:
		for line in f:
			data4.append([word for word in line.split(",") if word])
	data5 = []
	with open('raw/time_wall.txt', 'r') as f:
		for line in f:
			data5.append([word for word in line.split(",") if word])

	wb = xlwt.Workbook()
	sheet1 = wb.add_sheet("Extracted data")
	for row_index in range(len(data1)):
		for col_index in range(len(data1[row_index])):
			sheet1.write(row_index, col_index, float_if_possible(data1[row_index][col_index]))
	sheet2 = wb.add_sheet("Latency for first entry")
	for row_index in range(len(data2)):
		for col_index in range(len(data2[row_index])):
			sheet2.write(row_index, col_index, float_if_possible(data2[row_index][col_index]))
	sheet3 = wb.add_sheet("Latency for second entry")
	for row_index in range(len(data3)):
		for col_index in range(len(data3[row_index])):
			sheet3.write(row_index, col_index, float_if_possible(data3[row_index][col_index]))
	sheet4 = wb.add_sheet("Transitions & Darting")
	for row_index in range(len(data4)):
		for col_index in range(len(data4[row_index])):
			sheet4.write(row_index, col_index, float_if_possible(data4[row_index][col_index]))
	sheet5 = wb.add_sheet("Time at Centre & Wall")
	for row_index in range(len(data5)):
		for col_index in range(len(data5[row_index])):
			sheet5.write(row_index, col_index, float_if_possible(data5[row_index][col_index]))

			
	wb.save("output/Extracted_data_" + name + ".xls")

	return XY	

# time intervals:
def time_interval(XY, frame_rate, Y_half_lim, Y_fourth_lim, Y_third_lim, file_name, val, name):
	XY_1, XY_2, XY_3, XY_4, XY_5, XY_6, XY_7, XY_8, XY_9, XY_10, XY_1_third, XY_2_third, XY_3_third, XY_4_third, XY_5_third, XY_6_third, XY_7_third, XY_8_third, XY_9_third, XY_10_third, empty = [],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]
	chunk_value = int(val/10)
	part1, part2, part3, part4, part5, part6, part7, part8, part9, part10 = (part for part in chunks((XY), chunk_value))

	
	for x, y in part1:
		# if y>=Y_half_lim:
		# 	XY_1_half.append((x,y))
		# if y>=Y_fourth_lim:
		# 	XY_1_fourth.append((x,y))
		if y>=Y_third_lim:
			XY_1_third.append((x,y))
	
	for x, y in part2:
		# if y>=Y_half_lim:
		# 	XY_2_half.append((x,y))
		# if y>=Y_fourth_lim:
		# 	XY_2_fourth.append((x,y))
		if y>=Y_third_lim:
			XY_2_third.append((x,y))
	
	for x, y in part3:
		# if y>=Y_half_lim:
		# 	XY_3_half.append((x,y))
		# if y>=Y_fourth_lim:
		# 	XY_3_fourth.append((x,y))
		if y>=Y_third_lim:
			XY_3_third.append((x,y))
	
	for x, y in part4:
		# if y>=Y_half_lim:
		# 	XY_4_half.append((x,y))
		# if y>=Y_fourth_lim:
		# 	XY_4_fourth.append((x,y))
		if y>=Y_third_lim:
			XY_4_third.append((x,y))
	
	for x, y in part5:
		# if y>=Y_half_lim:
		# 	XY_5_half.append((x,y))
		# if y>=Y_fourth_lim:
		# 	XY_5_fourth.append((x,y))
		if y>=Y_third_lim:
			XY_5_third.append((x,y))
	
	for x, y in part6:
		# if y>=Y_half_lim:
		# 	XY_6_half.append((x,y))
		# if y>=Y_fourth_lim:
		# 	XY_6_fourth.append((x,y))
		if y>=Y_third_lim:
			XY_6_third.append((x,y))
	
	for x, y in part7:
		# if y>=Y_half_lim:
		# 	XY_7_half.append((x,y))
		# if y>=Y_fourth_lim:
		# 	XY_7_fourth.append((x,y))
		if y>=Y_third_lim:
			XY_7_third.append((x,y))
	
	for x, y in part8:
		# if y>=Y_half_lim:
		# 	XY_8_half.append((x,y))
		# if y>=Y_fourth_lim:
		# 	XY_8_fourth.append((x,y))
		if y>=Y_third_lim:
			XY_8_third.append((x,y))
	
	for x, y in part9:
		# if y>=Y_half_lim:
		# 	XY_9_half.append((x,y))
		# if y>=Y_fourth_lim:
		# 	XY_9_fourth.append((x,y))
		if y>=Y_third_lim:
			XY_9_third.append((x,y))
	
	for x, y in part10:
		# if y>=Y_half_lim:
		# 	XY_10_half.append((x,y))
		# if y>=Y_fourth_lim:
		# 	XY_10_fourth.append((x,y))
		if y>=Y_third_lim:
			XY_10_third.append((x,y))

	# time_1_half = (float(time(XY_1_half, frame_rate))/60)*100
	# time_2_half = (float(time(XY_2_half, frame_rate))/60)*100
	# time_3_half = (float(time(XY_3_half, frame_rate))/60)*100
	# time_4_half = (float(time(XY_4_half, frame_rate))/60)*100
	# time_5_half = (float(time(XY_5_half, frame_rate))/60)*100
	# time_6_half = (float(time(XY_6_half, frame_rate))/60)*100
	# time_7_half = (float(time(XY_7_half, frame_rate))/60)*100
	# time_8_half = (float(time(XY_8_half, frame_rate))/60)*100
	# time_9_half = (float(time(XY_9_half, frame_rate))/60)*100
	# time_10_half = (float(time(XY_10_half, frame_rate))/60)*100
	# time_1_fourth = (float(time(XY_1_fourth, frame_rate))/60)*100
	# time_2_fourth = (float(time(XY_2_fourth, frame_rate))/60)*100
	# time_3_fourth = (float(time(XY_3_fourth, frame_rate))/60)*100
	# time_4_fourth = (float(time(XY_4_fourth, frame_rate))/60)*100
	# time_5_fourth = (float(time(XY_5_fourth, frame_rate))/60)*100
	# time_6_fourth = (float(time(XY_6_fourth, frame_rate))/60)*100
	# time_7_fourth = (float(time(XY_7_fourth, frame_rate))/60)*100
	# time_8_fourth = (float(time(XY_8_fourth, frame_rate))/60)*100
	# time_9_fourth = (float(time(XY_9_fourth, frame_rate))/60)*100
	# time_10_fourth = (float(time(XY_10_fourth, frame_rate))/60)*100
	time_1_third = (float(time(XY_1_third, frame_rate))/60)*100
	time_2_third = (float(time(XY_2_third, frame_rate))/60)*100
	time_3_third = (float(time(XY_3_third, frame_rate))/60)*100
	time_4_third = (float(time(XY_4_third, frame_rate))/60)*100
	time_5_third = (float(time(XY_5_third, frame_rate))/60)*100
	time_6_third = (float(time(XY_6_third, frame_rate))/60)*100
	time_7_third = (float(time(XY_7_third, frame_rate))/60)*100
	time_8_third = (float(time(XY_8_third, frame_rate))/60)*100
	time_9_third = (float(time(XY_9_third, frame_rate))/60)*100
	time_10_third = (float(time(XY_10_third, frame_rate))/60)*100

	times = [file_name, time_1_third, time_2_third, time_3_third, time_4_third, time_5_third, time_6_third, time_7_third, time_8_third, time_9_third, time_10_third, empty]

	with open('raw/time_calc.txt', "a") as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerow(times)

	data6 = []
	with open('raw/time_calc.txt', 'r') as f:
		for line in f:
			data6.append([word for word in line.split(",") if word])

# write new sheet in xls:
	rb = open_workbook("output/Extracted_data_" + name + ".xls")
	wb = copy(rb)
	sheet6 = wb.add_sheet("Time in bottom third")
	for row_index in range(len(data6)):
		for col_index in range(len(data6[row_index])):
			sheet6.write(row_index, col_index, float_if_possible(data6[row_index][col_index]))
	# sheet3 = wb.add_sheet("Latency for first entry")
	# wb.get_sheet_by_name("Extracted_data")
	# for i,row in enumerate(Extracted_data.iter_rows()):
	# 	for j,col in enumerate(row):
 #  			sheet3.cell(row=0,column=0).value = col.value
	wb.save("output/Extracted_data_" + name + ".xls")