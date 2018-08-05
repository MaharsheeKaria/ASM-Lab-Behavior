import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import xlrd

def conf_int_1(xls, name):
	avg, conf_int, emin, emax = [],[],[],[]
	rb = xlrd.open_workbook(xls)
	sheet1 = rb.sheet_by_index(1)
	for i in range(1, 11):
		cell_obj = sheet1.cell(sheet1.nrows-3, i)
		avg.append(cell_obj.value)
   	for i in range(1, 11):
   		cell_obj = sheet1.cell(sheet1.nrows-1, i)
   		conf_int.append(cell_obj.value)
   	emin = [x - y for x, y in zip(avg, conf_int)]
   	emax = [x + y for x, y in zip(avg, conf_int)]

   	y = avg
   	x = np.arange(0,len(y))

	plt.clf()
	plt.title('% time spent in the bottom 1/2')
	plt.ylabel('% time')
	plt.xlim(0,9)
	plt.ylim(min(emin)-1,max(emax)+1)
	plt.xticks(np.arange(10))
	plt.xlabel('step intervals')
	plt.plot(x, y, color='blue')
	plt.fill_between(x, emin, emax, color='blue', alpha=0.3)
   	plt.savefig('output/time_half_' + name + '.png')

def conf_int_2(xls, name):
	avg, conf_int, emin, emax = [],[],[],[]
	rb = xlrd.open_workbook(xls)
	sheet1 = rb.sheet_by_index(1)
	for i in range(11, 21):
		cell_obj = sheet1.cell(sheet1.nrows-3, i)
		avg.append(cell_obj.value)
	for i in range(11, 21):
		cell_obj = sheet1.cell(sheet1.nrows-1, i)
		conf_int.append(cell_obj.value)
	emin = [x - y for x, y in zip(avg, conf_int)]
   	emax = [x + y for x, y in zip(avg, conf_int)]

	y = avg
	x = np.arange(0,len(y))

	plt.clf()
	plt.title('% time spent in the bottom 1/4')
	plt.ylabel('% time')
	plt.xlim(0,9)
	plt.ylim(min(emin)-1,max(emax)+1)
	plt.xticks(np.arange(10))
	plt.xlabel('step intervals')
	plt.plot(x, y, color='red')
	plt.fill_between(x, emin, emax, color='red', alpha=0.3)
   	plt.savefig('output/time_fourth_' + name + '.png')

def conf_int_3(xls, name):
	avg, conf_int, emin, emax = [],[],[],[]
	rb = xlrd.open_workbook(xls)
	sheet1 = rb.sheet_by_index(1)
	for i in range(21, 31):
		cell_obj = sheet1.cell(sheet1.nrows-3, i)
		avg.append(cell_obj.value)
   	for i in range(21, 31):
   		cell_obj = sheet1.cell(sheet1.nrows-1, i)
   		conf_int.append(cell_obj.value)
   	emin = [x - y for x, y in zip(avg, conf_int)]
   	emax = [x + y for x, y in zip(avg, conf_int)]

   	y = avg
   	x = np.arange(0,len(y))

	plt.clf()
	plt.title('% time spent in the bottom 1/3')
	plt.ylabel('% time')
	plt.xlim(0,9)
	plt.ylim(min(emin)-1,max(emax)+1)
	plt.xticks(np.arange(10))
	plt.xlabel('step intervals')
	plt.plot(x, y, color='green')
	plt.fill_between(x, emin, emax, color='green', alpha=0.3)
   	plt.savefig('output/time_third_' + name + '.png')