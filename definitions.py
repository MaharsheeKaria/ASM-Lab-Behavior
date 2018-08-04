from xlrd import open_workbook
from xlutils import copy
import csv
import xlwt
import numpy as np


def get_all_sheets(excel_file_input, excel_file_output):
	workbook = open_workbook(excel_file_input)
	number = workbook.nsheets
	pages = range(1, number+1)
	for x in pages:
		for sheet in workbook.sheets():
			new_workbook = copy.copy(workbook)
			new_workbook._Workbook__worksheets = [new_workbook._Workbook__worksheets[int(x-1)]]
			new_workbook.save(excel_file_output + '_Tank_' + str(x) + '.xls')
	return number

def scale(X_length, tank_sheet, frames):
	workbook = open_workbook(tank_sheet)
	sheet = workbook.sheet_by_index(0)
	cell = sheet.cell(6, 2)
	X_max = cell.value
	cell = sheet.cell(5, 2)
	X_min = cell.value
	cell = sheet.cell(6, 3)
	Y_max = cell.value
	cell = sheet.cell(5, 3)
	Y_min = cell.value
	
	scaler = X_length/(X_max - X_min)

	X_max = X_max*scaler
	X_min = X_min*scaler
	Y_max = Y_max*scaler
	Y_min = Y_min*scaler

	with open(tank_sheet + '.txt', 'w') as out:
		out.write('x,y\n')
	for i in range(10, frames):
		cells = [sheet.row_slice(rowx=i, start_colx=2, end_colx=4)]
		with open(tank_sheet + '.txt', 'a') as out:
			writer = csv.writer(out, delimiter=',')
			for item in cells:
				writer.writerow(item)

	format_txt = open(tank_sheet + '.txt', "r")
	a = 'number:'
	lst = []
	for line in format_txt:
		line = line.replace(a, '')
		lst.append(line)
	format_txt.close()
	format_txt = open(tank_sheet + '.txt', "w")
	for line in lst:
		format_txt.write(line)
	format_txt.close()

	lines = []
	with open(tank_sheet + '.txt', 'r') as inp:
		reader = csv.reader(inp, delimiter=',')
		lines.append(next(reader))
		for row in reader:
			row[0] = float(row[0])*scaler
			row[1] = float(row[1])*scaler
			lines.append(row)
	with open(tank_sheet + '.txt', 'w') as out:
		writer = csv.writer(out, delimiter=',')
		for row in lines:
			writer.writerow(row)

	return X_min, X_max, Y_min, Y_max, scaler