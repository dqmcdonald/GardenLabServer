#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# GardenLab Plotting Script
# Quentin McDonald
# June 2017

import sys
import mysql.connector
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, FormatStrFormatter
from matplotlib.dates import HourLocator, DateFormatter
import GardenLabDB
from enum import Enum
import datetime

class PlotType(Enum):
    LINE = 1
    HOURLY_BAR = 2
    
    
class PlotStyle(object):
    """
    Encapsulates a style of plot - line color, plot style etc
    """
    def __init__( self, face_color, plot_type = PlotType.LINE ):
        self.face_color = face_color
        self.plot_type = plot_type
        


plot_defs = {
    "temperature" : PlotStyle("#05d005"),
    "humidity" : PlotStyle("#d05050"),
    "pressure" : PlotStyle("#0505d0"),
    "battery_voltage" : PlotStyle("#d0d005"),
    "wind_speed" : PlotStyle("#d0d0d0") ,
    "panel_current" : PlotStyle("#00f000"),
    "rainfall": PlotStyle("#5a2729",PlotType.HOURLY_BAR)}






def cm2inch(*tupl):
    inch = 2.54
    if isinstance(tupl[0], tuple):
        return tuple(i/inch for i in tupl[0])
    else:
        return tuple(i/inch for i in tupl)


def generate_24hr_plot(field, color='green', plot_type=PlotType.LINE):
    """
    Generate a 24 plot for the specified field
    """

    #Start by retrieving the data:
    (dates,field_data) = GardenLabDB.last_day_data(field)

    fig,ax = plt.subplots(figsize=cm2inch(6,3))
    if plot_type == PlotType.LINE:
        ax.plot_date(dates,field_data,"-",color=color,lw=1.0)
       
    elif plot_type == PlotType.HOURLY_BAR:
        hours = []
        hourly_data = []
        current_hour = dates[0]
        hour_cnt = 0
        hours.append(current_hour)
        hourly_data.append(0)
        for i in range(len(dates)):
            if dates[i].hour != current_hour.hour:
                current_hour = dates[i]
                hours.append(current_hour)
                hourly_data.append(0)
                hour_cnt += 1
            hourly_data[hour_cnt] += field_data[i]
        ax.bar(hours,hourly_data,width=1.0/24.0,color=color)

    hours = HourLocator()
    hours_fmt = DateFormatter("%H")

    ax.xaxis.set_major_locator(hours)
    ax.xaxis.set_major_formatter(hours_fmt)
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(4)

    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(4)
    
    ax.autoscale_view()
    

    fig.autofmt_xdate()

    plt.show
    
    fig.savefig("images/latest_{0}.png".format(field), transparent=True,
                    dpi=150)

    plt.close()

def generate_all_latest_plots():
    for field in plot_defs.keys():
        generate_24hr_plot(field, plot_defs[field].face_color,
                               plot_defs[field].plot_type)



def main():
    if len(sys.argv) < 2 :
        generate_all_latest_plots()
    else:
        generate_24hr_plot( sys.argv[1] )


if __name__ == "__main__":
        main()
