import numpy as np
from xlutils.copy import copy
import xlrd 
import xlwt
from scipy import stats

def calc(xls):
	row_vals, avg, sd, conf, conf_int= [],[],[],[],[]
	rb = xlrd.open_workbook(xls)
	sheet1 = rb.sheet_by_index(0)
	nxt_row = sheet1.nrows + 1
	prev_col = sheet1.ncols-1
	for i in range(1, (sheet1.ncols-1)):
		col_idx = i
		for row_idx in range(2, sheet1.nrows):
			cell_obj = sheet1.cell(row_idx, col_idx)
			row_vals.append(cell_obj.value)
		avg.append(str(np.mean(row_vals)))
		sd.append(str(np.std(row_vals, ddof=1)))
		conf.append((np.std(row_vals, ddof=1)*1.96)/(np.sqrt(len(row_vals))))
		row_vals = []
	
	wb = copy(rb)
	sheet1 = wb.get_sheet(0)
	for i,items in enumerate(avg):
		sheet1.write(nxt_row, i+1, float(items))
	for i,items in enumerate(sd):
		sheet1.write(nxt_row+1, i+1, float(items))
	for i,items in enumerate(conf):
		sheet1.write(nxt_row+2, i+1, items)
	sheet1.write(nxt_row, 0, 'mean')
	sheet1.write(nxt_row+1, 0, 'standard deviation')
	sheet1.write(nxt_row+2, 0, '95%% confidence intervals')
	wb.save(xls)

def calc2(xls):
	row_vals, avg, sd, conf_int, conf = [],[],[],[],[]
	rb = xlrd.open_workbook(xls)
	sheet1 = rb.sheet_by_index(5)
	nxt_row = sheet1.nrows + 1
	prev_col = sheet1.ncols-2
	for i in range(1, (sheet1.ncols-2)):
		col_idx = i
		for row_idx in range(2, sheet1.nrows):
			cell_obj = sheet1.cell(row_idx, col_idx)
			row_vals.append(cell_obj.value)
		avg.append(str(np.mean(row_vals)))
		sd.append(str(np.std(row_vals, ddof=1)))
		conf.append((np.std(row_vals, ddof=1)*1.96)/(np.sqrt(len(row_vals))))
		row_vals = []

	wb = copy(rb)
	sheet1 = wb.get_sheet(5)
	for i,items in enumerate(avg):
		sheet1.write(nxt_row, i+1, float(items))
	for i,items in enumerate(sd):
		sheet1.write(nxt_row+1, i+1, float(items))
	for i,items in enumerate(conf):
		sheet1.write(nxt_row+2, i+1, items)
	sheet1.write(nxt_row, 0, 'mean')
	sheet1.write(nxt_row+1, 0, 'standard deviation')
	sheet1.write(nxt_row+2, 0, '95%% confidence intervals')
	wb.save(xls)

