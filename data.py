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

	with open('raw/extracted_info.txt', "a") as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerow(table)

	data1 = []
	with open('raw/extracted_info.txt', 'r') as f:
		for line in f:
			data1.append([word for word in line.split(",") if word])

	wb = xlwt.Workbook()
	sheet1 = wb.add_sheet("Extracted data")
	for row_index in range(len(data1)):
		for col_index in range(len(data1[row_index])):
			sheet1.write(row_index, col_index, float_if_possible(data1[row_index][col_index]))
			
	wb.save("output/Extracted_data_" + name + ".xls")

	return XY

# time intervals:
def time_interval(XY, frame_rate, Y_half_lim, Y_fourth_lim, Y_third_lim, file_name, val, name, X0, Xn, Y0, Yn):
	Y1, Y2, Y3, Y4, Y5, Y6, Y7, Y8, Y9, Y10, X1, X2, X3, X4, X5, X6, X7, X8, X9, X10, XY_1_third, XY_2_third, XY_3_third, XY_4_third, XY_5_third, XY_6_third, XY_7_third, XY_8_third, XY_9_third, XY_10_third, empty = [],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]
	XY1_centre, XY1_boundary, XY2_centre, XY2_boundary, XY3_centre, XY3_boundary, XY4_centre, XY4_boundary, XY5_centre, XY5_boundary, XY6_centre, XY6_boundary, XY7_centre, XY7_boundary, XY8_centre, XY8_boundary, XY9_centre, XY9_boundary, XY10_centre, XY10_boundary = [],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]
	chunk_value = int(val/10)
	part1, part2, part3, part4, part5, part6, part7, part8, part9, part10 = (part for part in chunks((XY), chunk_value))
	
	for x, y in part1:
		if y>=Y_third_lim:
			XY_1_third.append((x,y))
		X1.append(x)
		Y1.append(y)
		V1, S1 = find_vel_dist(frame_rate, X1, Y1)	
		mean_V1 = np.mean(V1)
		sd_V1 = np.std(V1)		
		if x>=X0 and x<=Xn and y>=Y0 and y<=Yn:
			XY1_centre.append((x, y))
		else:
			XY1_boundary.append((x, y))

	for x, y in part2:
		if y>=Y_third_lim:
			XY_2_third.append((x,y))
		X2.append(x)
		Y2.append(y)
		V2, S2 = find_vel_dist(frame_rate, X2, Y2)	
		mean_V2 = np.mean(V2)
		sd_V2 = np.std(V2)
		if x>=X0 and x<=Xn and y>=Y0 and y<=Yn:
			XY2_centre.append((x, y))
		else:
			XY2_boundary.append((x, y))
	
	for x, y in part3:
		if y>=Y_third_lim:
			XY_3_third.append((x,y))
		X3.append(x)
		Y3.append(y)
		V3, S3 = find_vel_dist(frame_rate, X3, Y3)	
		mean_V3 = np.mean(V3)
		sd_V3 = np.std(V3)
		if x>=X0 and x<=Xn and y>=Y0 and y<=Yn:
			XY3_centre.append((x, y))
		else:
			XY3_boundary.append((x, y))
	
	for x, y in part4:
		if y>=Y_third_lim:
			XY_4_third.append((x,y))
		X4.append(x)
		Y4.append(y)
		V4, S4 = find_vel_dist(frame_rate, X4, Y4)	
		mean_V4 = np.mean(V4)
		sd_V4 = np.std(V4)
		if x>=X0 and x<=Xn and y>=Y0 and y<=Yn:
			XY4_centre.append((x, y))
		else:
			XY4_boundary.append((x, y))
	
	for x, y in part5:
		if y>=Y_third_lim:
			XY_5_third.append((x,y))
		X5.append(x)
		Y5.append(y)
		V5, S5 = find_vel_dist(frame_rate, X5, Y5)	
		mean_V5 = np.mean(V5)
		sd_V5 = np.std(V5)
		if x>=X0 and x<=Xn and y>=Y0 and y<=Yn:
			XY5_centre.append((x, y))
		else:
			XY5_boundary.append((x, y))
	
	for x, y in part6:
		if y>=Y_third_lim:
			XY_6_third.append((x,y))
		X6.append(x)
		Y6.append(y)
		V6, S6 = find_vel_dist(frame_rate, X6, Y6)	
		mean_V6 = np.mean(V6)
		sd_V6 = np.std(V6)
		if x>=X0 and x<=Xn and y>=Y0 and y<=Yn:
			XY6_centre.append((x, y))
		else:
			XY6_boundary.append((x, y))
	
	for x, y in part7:
		if y>=Y_third_lim:
			XY_7_third.append((x,y))
		X7.append(x)
		Y7.append(y)
		V7, S7 = find_vel_dist(frame_rate, X7, Y7)	
		mean_V7 = np.mean(V7)
		sd_V7 = np.std(V7)
		if x>=X0 and x<=Xn and y>=Y0 and y<=Yn:
			XY7_centre.append((x, y))
		else:
			XY7_boundary.append((x, y))
	
	for x, y in part8:
		if y>=Y_third_lim:
			XY_8_third.append((x,y))
		X8.append(x)
		Y8.append(y)
		V8, S8 = find_vel_dist(frame_rate, X8, Y8)	
		mean_V8 = np.mean(V8)
		sd_V8 = np.std(V8)
		if x>=X0 and x<=Xn and y>=Y0 and y<=Yn:
			XY8_centre.append((x, y))
		else:
			XY8_boundary.append((x, y))
	
	for x, y in part9:
		if y>=Y_third_lim:
			XY_9_third.append((x,y))
		X9.append(x)
		Y9.append(y)
		V9, S9 = find_vel_dist(frame_rate, X9, Y9)	
		mean_V9 = np.mean(V9)
		sd_V9 = np.std(V9)
		if x>=X0 and x<=Xn and y>=Y0 and y<=Yn:
			XY9_centre.append((x, y))
		else:
			XY9_boundary.append((x, y))
	
	for x, y in part10:
		if y>=Y_third_lim:
			XY_10_third.append((x,y))
		X10.append(x)
		Y10.append(y)
		V10, S10 = find_vel_dist(frame_rate, X10, Y10)	
		mean_V10 = np.mean(V10)
		sd_V10 = np.std(V10)
		if x>=X0 and x<=Xn and y>=Y0 and y<=Yn:
			XY10_centre.append((x, y))
		else:
			XY10_boundary.append((x, y))

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

#latencies: works
	latency1_1, latency1_2 = latencies(Y_half_lim, part1, frame_rate)
	latency2_1, latency2_2 = latencies(Y_half_lim, part2, frame_rate)
	latency3_1, latency3_2 = latencies(Y_half_lim, part3, frame_rate)
	latency4_1, latency4_2 = latencies(Y_half_lim, part4, frame_rate)
	latency5_1, latency5_2 = latencies(Y_half_lim, part5, frame_rate)
	latency6_1, latency6_2 = latencies(Y_half_lim, part6, frame_rate)
	latency7_1, latency7_2 = latencies(Y_half_lim, part7, frame_rate)
	latency8_1, latency8_2 = latencies(Y_half_lim, part8, frame_rate)
	latency9_1, latency9_2 = latencies(Y_half_lim, part9, frame_rate)
	latency10_1, latency10_2 = latencies(Y_half_lim, part10, frame_rate)

#transitions: works
	tran1 = find_transitions(Y1, Y_half_lim)
	tran2 = find_transitions(Y2, Y_half_lim)
	tran3 = find_transitions(Y3, Y_half_lim)
	tran4 = find_transitions(Y4, Y_half_lim)
	tran5 = find_transitions(Y5, Y_half_lim)
	tran6 = find_transitions(Y6, Y_half_lim)
	tran7 = find_transitions(Y7, Y_half_lim)
	tran8 = find_transitions(Y8, Y_half_lim)
	tran9 = find_transitions(Y9, Y_half_lim)
	tran10 = find_transitions(Y10, Y_half_lim)	

#darting: works
	darts1 = find_darts(V1, mean_V1, sd_V1)
	darts2 = find_darts(V2, mean_V2, sd_V2)
	darts3 = find_darts(V3, mean_V3, sd_V3)
	darts4 = find_darts(V4, mean_V4, sd_V4)
	darts5 = find_darts(V5, mean_V5, sd_V5)
	darts6 = find_darts(V6, mean_V6, sd_V6)
	darts7 = find_darts(V7, mean_V7, sd_V7)
	darts8 = find_darts(V8, mean_V8, sd_V8)
	darts9 = find_darts(V9, mean_V9, sd_V9)
	darts10 = find_darts(V10, mean_V10, sd_V10)

#time centre/wall: works
	time_centre1 = float(time(XY1_centre, frame_rate))
	time_boundary1 = float(time(XY1_boundary, frame_rate))
	time_centre_perc1 = (time_centre1/(time_centre1+time_boundary1))*100
	time_boundary_perc1 = 100 - time_centre_perc1
	time_centre2 = float(time(XY2_centre, frame_rate))
	time_boundary2 = float(time(XY2_boundary, frame_rate))
	time_centre_perc2 = (time_centre2/(time_centre2+time_boundary2))*100
	time_boundary_perc2 = 100 - time_centre_perc2
	time_centre3 = float(time(XY3_centre, frame_rate))
	time_boundary3 = float(time(XY3_boundary, frame_rate))
	time_centre_perc3 = (time_centre3/(time_centre3+time_boundary3))*100
	time_boundary_perc3 = 100 - time_centre_perc3
	time_centre4 = float(time(XY4_centre, frame_rate))
	time_boundary4 = float(time(XY4_boundary, frame_rate))
	time_centre_perc4 = (time_centre4/(time_centre4+time_boundary4))*100
	time_boundary_perc4 = 100 - time_centre_perc4
	time_centre5 = float(time(XY5_centre, frame_rate))
	time_boundary5 = float(time(XY5_boundary, frame_rate))
	time_centre_perc5 = (time_centre5/(time_centre5+time_boundary5))*100
	time_boundary_perc5 = 100 - time_centre_perc5
	time_centre6 = float(time(XY6_centre, frame_rate))
	time_boundary6 = float(time(XY6_boundary, frame_rate))
	time_centre_perc6 = (time_centre6/(time_centre6+time_boundary6))*100
	time_boundary_perc6 = 100 - time_centre_perc6
	time_centre7 = float(time(XY7_centre, frame_rate))
	time_boundary7 = float(time(XY7_boundary, frame_rate))
	time_centre_perc7 = (time_centre7/(time_centre7+time_boundary7))*100
	time_boundary_perc7 = 100 - time_centre_perc7
	time_centre8 = float(time(XY8_centre, frame_rate))
	time_boundary8 = float(time(XY8_boundary, frame_rate))
	time_centre_perc8 = (time_centre8/(time_centre8+time_boundary8))*100
	time_boundary_perc8 = 100 - time_centre_perc8
	time_centre9 = float(time(XY9_centre, frame_rate))
	time_boundary9 = float(time(XY9_boundary, frame_rate))
	time_centre_perc9 = (time_centre9/(time_centre9+time_boundary9))*100
	time_boundary_perc9 = 100 - time_centre_perc9
	time_centre10 = float(time(XY10_centre, frame_rate))
	time_boundary10 = float(time(XY10_boundary, frame_rate))
	time_centre_perc10 = (time_centre10/(time_centre10+time_boundary10))*100
	time_boundary_perc10 = 100 - time_centre_perc10


	times = [file_name, time_1_third, time_2_third, time_3_third, time_4_third, time_5_third, time_6_third, time_7_third, time_8_third, time_9_third, time_10_third, empty]
	lat1 = [file_name, latency1_1, latency2_1, latency3_1, latency4_1, latency5_1, latency6_1, latency7_1, latency8_1, latency9_1, latency10_1]
	lat2 = [file_name, latency1_2, latency2_2, latency3_2, latency4_2, latency5_2, latency6_2, latency7_2, latency8_2, latency9_2, latency10_2]
	tran = [file_name, tran1, tran2, tran3, tran4, tran5, tran6, tran7, tran8, tran9, tran10]
	dart = [file_name, darts1, darts2, darts3, darts4, darts5, darts6, darts7, darts8, darts9, darts10]
	time_wall = [file_name, time_boundary_perc1, time_boundary_perc2, time_boundary_perc3, time_boundary_perc4, time_boundary_perc5, time_boundary_perc6, time_boundary_perc7, time_boundary_perc8, time_boundary_perc9, time_boundary_perc10]
	time_centre = [file_name, time_centre_perc1, time_centre_perc2, time_centre_perc3, time_centre_perc4, time_centre_perc5, time_centre_perc6, time_centre_perc7, time_centre_perc8, time_centre_perc9, time_centre_perc10]

	with open('raw/time_calc.txt', "a") as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerow(times)

	with open('raw/lat1.txt', 'a') as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerow(lat1)

	with open('raw/lat2.txt', 'a') as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerow(lat2)

	with open('raw/tran.txt', 'a') as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerow(tran)

	with open('raw/dart.txt', 'a') as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerow(dart)
	with open('raw/time_wall.txt', 'a') as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerow(time_wall)
	with open('raw/time_centre.txt', 'a') as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerow(time_centre)

	data2 = []
	with open('raw/time_calc.txt', 'r') as f:
		for line in f:
			data2.append([word for word in line.split(",") if word])
	data3 = []
	with open('raw/lat1.txt', 'r') as f:
		for line in f:
			data3.append([word for word in line.split(",") if word])
	data4 = []
	with open('raw/lat2.txt', 'r') as f:
		for line in f:
			data4.append([word for word in line.split(",") if word])
	data5 = []
	with open('raw/tran.txt', 'r') as f:
		for line in f:
			data5.append([word for word in line.split(",") if word])
	data6 = []
	with open('raw/dart.txt', 'r') as f:
		for line in f:
			data6.append([word for word in line.split(",") if word])
	data7 = []
	with open('raw/time_wall.txt', 'r') as f:
		for line in f:
			data7.append([word for word in line.split(",") if word])
	data8 = []
	with open('raw/time_centre.txt', 'r') as f:
		for line in f:
			data8.append([word for word in line.split(",") if word])

# write new sheet in xls:
	rb = open_workbook("output/Extracted_data_" + name + ".xls")
	wb = copy(rb)
	sheet2 = wb.add_sheet("Time in bottom third")
	for row_index in range(len(data2)):
		for col_index in range(len(data2[row_index])):
			sheet2.write(row_index, col_index, float_if_possible(data2[row_index][col_index]))
	sheet3 = wb.add_sheet("Latency for first entry")
	for row_index in range(len(data3)):
		for col_index in range(len(data3[row_index])):
			sheet3.write(row_index, col_index, float_if_possible(data3[row_index][col_index]))
	sheet4 = wb.add_sheet("Latency for second entry")
	for row_index in range(len(data4)):
		for col_index in range(len(data4[row_index])):
			sheet4.write(row_index, col_index, float_if_possible(data4[row_index][col_index]))
	sheet5 = wb.add_sheet("Transitions")
	for row_index in range(len(data5)):
		for col_index in range(len(data5[row_index])):
			sheet5.write(row_index, col_index, float_if_possible(data5[row_index][col_index]))
	sheet6 = wb.add_sheet("Darting")
	for row_index in range(len(data6)):
		for col_index in range(len(data6[row_index])):
			sheet6.write(row_index, col_index, float_if_possible(data6[row_index][col_index]))
	sheet7 = wb.add_sheet("%time in boundary")
	for row_index in range(len(data7)):
		for col_index in range(len(data7[row_index])):
			sheet7.write(row_index, col_index, float_if_possible(data7[row_index][col_index]))
	sheet8 = wb.add_sheet("%time in centre")
	for row_index in range(len(data8)):
		for col_index in range(len(data8[row_index])):
			sheet8.write(row_index, col_index, float_if_possible(data8[row_index][col_index]))

	wb.save("output/Extracted_data_" + name + ".xls")