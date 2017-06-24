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



field_colors = {
    "temperature" : "#05d005",
    "humidity" : "#d05050",
    "pressure" : "#0505d0",
    "battery_voltage" : "#d0d005",
    "wind_speed" : "#d0d0d0" ,
    "load_current" : "#00f000" }





def cm2inch(*tupl):
    inch = 2.54
    if isinstance(tupl[0], tuple):
        return tuple(i/inch for i in tupl[0])
    else:
        return tuple(i/inch for i in tupl)


def generate_24hr_plot(field, color='green'):
    """
    Generate a 24 plot for the specified field
    """

    #Start by retrieving the data:
    (dates,field_data) = GardenLabDB.last_day_data(field)

    fig,ax = plt.subplots(figsize=cm2inch(6,3))

    ax.plot_date(dates,field_data,"-",color=color,lw=1.0)

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
    for field in field_colors.keys():
        generate_24hr_plot(field, field_colors[field])



def main():
    if len(sys.argv) < 2 :
        generate_all_latest_plots()
    else:
        generate_24hr_plot( sys.argv[1] )


if __name__ == "__main__":
        main()
