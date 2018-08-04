import numpy as np
import matplotlib.pyplot as plt
from xlrd import open_workbook
from xlutils import copy
import csv
import xlwt
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from scipy import stats
import xlrd


def plot(xls):

    # visual representation graph: alignment test

    workbook = open_workbook(xls)
    sheet = workbook.sheet_by_index(0)
    cell = sheet.cell(sheet.nrows-3, 3)
    centre = cell.value
    cell = sheet.cell(sheet.nrows-3, 4)
    wall = cell.value
    cell = sheet.cell(sheet.nrows-3, 11)
    bottom_fourth = cell.value
    cell = sheet.cell(sheet.nrows-3, 19)
    bottom_half = cell.value
    cell = sheet.cell(sheet.nrows-3, 27)
    bottom_3fourth = cell.value

    left, width = .25, .5
    bottom, height = .25, .5
    right = left + width
    top = bottom + height
    ax = plt.gca()
    p = plt.Rectangle((left, bottom), width, height,
                  fill=False,
                  )
    p.set_transform(ax.transAxes)
    p.set_clip_on(False)
    ax.add_patch(p)

    ax.text(left, bottom, 'bottom 1/2 = '+str(bottom_half),
            horizontalalignment='left',
            verticalalignment='bottom',
            transform=ax.transAxes)

    ax.text(right, top, 'bottom 3/4 = '+str(bottom_3fourth),
            horizontalalignment='right',
            verticalalignment='top',
            transform=ax.transAxes)

    ax.text(left, bottom, 'bottom 1/4 ='+str(bottom_fourth),
            horizontalalignment='left',
            verticalalignment='top',
            transform=ax.transAxes)

    ax.text(left, 0.5*(bottom + top), 'wall ='+str(wall),
            horizontalalignment='right',
            verticalalignment='center',
            rotation='vertical',
            transform=ax.transAxes)

    ax.text(0.5*(left + right), 0.5*(bottom + top), 'centre ='+str(centre),
            horizontalalignment='center',
            verticalalignment='center',
            transform=ax.transAxes)

    plt.axis('off')

    plt.savefig('output/%time_allignment.png') 

    # distance graphs: bar

    workbook = open_workbook(xls)
    sheet = workbook.sheet_by_index(0)
    cell = sheet.cell(sheet.nrows-3, 7)
    dist_mean_centre = cell.value
    cell = sheet.cell(sheet.nrows-3, 8)
    dist_mean_wall = cell.value
    cell = sheet.cell(sheet.nrows-3, 15)
    dist_mean_b_fourth = cell.value
    cell = sheet.cell(sheet.nrows-3, 16)
    dist_mean_t_3fourth = cell.value
    cell = sheet.cell(sheet.nrows-3, 23)
    dist_mean_b_half = cell.value
    cell = sheet.cell(sheet.nrows-3, 24)
    dist_mean_t_half = cell.value
    cell = sheet.cell(sheet.nrows-3, 31)
    dist_mean_b_3fourth = cell.value
    cell = sheet.cell(sheet.nrows-3, 32)
    dist_mean_t_fourth = cell.value

    cell = sheet.cell(sheet.nrows-2, 7)
    dist_std_centre = cell.value
    cell = sheet.cell(sheet.nrows-2, 8)
    dist_std_wall = cell.value
    cell = sheet.cell(sheet.nrows-2, 15)
    dist_std_b_fourth = cell.value
    cell = sheet.cell(sheet.nrows-2, 16)
    dist_std_t_3fourth = cell.value
    cell = sheet.cell(sheet.nrows-2, 23)
    dist_std_b_half = cell.value
    cell = sheet.cell(sheet.nrows-2, 24)
    dist_std_t_half = cell.value
    cell = sheet.cell(sheet.nrows-2, 31)
    dist_std_b_3fourth = cell.value
    cell = sheet.cell(sheet.nrows-2, 32)
    dist_std_t_fourth = cell.value

    N = 8
    means = (dist_mean_centre, dist_mean_wall, dist_mean_b_fourth, dist_mean_t_3fourth, dist_mean_b_half, dist_mean_t_half, dist_mean_b_3fourth, dist_mean_t_fourth)
    std = (dist_std_centre, dist_std_wall, dist_std_b_fourth, dist_std_t_3fourth, dist_std_b_half, dist_std_t_half, dist_std_b_3fourth, dist_std_t_fourth)

    ind = np.arange(N)  # the x locations for the groups
    width = 0.35       # the width of the bars

    fig, ax = plt.subplots()
    rects = ax.bar(ind, means, width, color='r', yerr=std)

    ax.set_ylabel('Distance (mm)')
    ax.set_title('Total distance swam')
    ax.set_xticks(ind + width/32)
    ax.set_xticklabels(('centre', 'wall', 'bottom1/4', 'top3/4', 'bottom1/2', 'top1/2', 'bottom3/4', 'top1/4'))

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                    '%d' % int(height),
                    ha='center', va='bottom')

    autolabel(rects)
    plt.savefig('output/distance_bar.png')

    # time graph: stacked bar

    workbook = open_workbook(xls)
    sheet = workbook.sheet_by_index(0)
    cell = sheet.cell(sheet.nrows-3, 3)
    time_mean_centre = cell.value
    cell = sheet.cell(sheet.nrows-3, 4)
    time_mean_wall = cell.value
    cell = sheet.cell(sheet.nrows-3, 11)
    time_mean_b_fourth = cell.value
    cell = sheet.cell(sheet.nrows-3, 12)
    time_mean_t_3fourth = cell.value
    cell = sheet.cell(sheet.nrows-3, 19)
    time_mean_b_half = cell.value
    cell = sheet.cell(sheet.nrows-3, 20)
    time_mean_t_half = cell.value
    cell = sheet.cell(sheet.nrows-3, 27)
    time_mean_b_3fourth = cell.value
    cell = sheet.cell(sheet.nrows-3, 28)
    time_mean_t_fourth = cell.value

    cell = sheet.cell(sheet.nrows-2, 3)
    time_std_centre = cell.value
    cell = sheet.cell(sheet.nrows-2, 4)
    time_std_wall = cell.value
    cell = sheet.cell(sheet.nrows-2, 11)
    time_std_b_fourth = cell.value
    cell = sheet.cell(sheet.nrows-2, 12)
    time_std_t_3fourth = cell.value
    cell = sheet.cell(sheet.nrows-2, 19)
    time_std_b_half = cell.value
    cell = sheet.cell(sheet.nrows-2, 20)
    time_std_t_half = cell.value
    cell = sheet.cell(sheet.nrows-2, 27)
    time_std_b_3fourth = cell.value
    cell = sheet.cell(sheet.nrows-2, 28)
    time_std_t_fourth = cell.value

    raw_data = {'% Time': ['wall', 'bottom 1/4', 'bottom 1/2', 'bottom 3/4'],
            '1st': [time_mean_wall, time_mean_b_fourth, time_mean_b_half, time_mean_b_3fourth],
            '2nd': [time_mean_centre, time_mean_t_3fourth, time_mean_t_half, time_mean_t_fourth]}
    df = pd.DataFrame(raw_data, columns = ['% Time', '1st', '2nd'])
    df

    f, ax1 = plt.subplots(1, figsize=(10,5))
    bar_width = 0.75
    bar_l = [i-2 for i in range(len(df['1st']))]
    tick_pos = [i+(bar_width/32) for i in bar_l]

    sd1st = [time_std_wall, time_std_b_fourth, time_std_b_half, time_std_b_3fourth]
    sd2nd = [time_std_centre, time_std_t_3fourth, time_std_t_half, time_std_t_fourth]

    ax1.bar(bar_l,
            df['1st'],
            width=bar_width,
            alpha=0.5,
            color='g',
            yerr=sd1st)

    ax1.bar(bar_l,
            df['2nd'],
            width=bar_width,
            bottom=df['1st'],
            alpha=0.5,
            color='b',
            yerr=sd2nd)

    rects = ax1.patches
    labels = ['centre', 'top 3/4', 'top 1/2', 'top 1/4']

    for rect, label in zip(rects, labels):
        height = rect.get_height()
        ax1.text(rect.get_x() + rect.get_width()/2, height + 5, label, ha='center', va='baseline')

    plt.xticks(tick_pos, df['% Time'])
    ax1.set_ylabel("% Time")
    ax1.set_xlabel("Conditions")
    plt.xlim([min(tick_pos)-(bar_width), max(tick_pos)+bar_width])
    plt.savefig('output/%time_stacked_bar.png')