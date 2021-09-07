#!/usr/bin/python3
##!/usr/bin/env python3
from jinja2 import Environment, FileSystemLoader
import mysql.connector
import datetime
import cgi
import cgitb
import os
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import os.path
import base64
from obspy.core import read
import pytz
import datetime
cgitb.enable()

STANDARD_SAMPLING_RATE = 18.7667
BASE_DIR = "/mnt/ssd/pi/jamaseisData/CASH/"

def get_file_names( date ):

    local_time = pytz.timezone("Pacific/Auckland")
    naive_datetime = datetime.datetime.strptime(date, "%Y-%m-%d")
    naive_datetime = naive_datetime + datetime.timedelta(days=1 )
    local_datetime=local_time.localize(naive_datetime, is_dst=None)
    utc_datetime = local_datetime.astimezone(pytz.utc)

    yesterday_utc = utc_datetime - datetime.timedelta(days=1)

    streams = []
    for i in range(12,24):
        streams.append(os.path.join(BASE_DIR,str(yesterday_utc.year),
            str(yesterday_utc.month), str(yesterday_utc.day) ,
            '{}.sac'.format(i)))
    for i in range(12):
        streams.append(os.path.join(BASE_DIR,str(utc_datetime.year),
            str(utc_datetime.month), str(utc_datetime.day) ,
            '{}.sac'.format(i)))
    return streams
   


def plot_day_data( st, scale, date ):
    """
    Plot the data and return the plot as a string
    """
    fig = plt.figure()
    dt = datetime.datetime.strptime(date, "%Y-%m-%d")
    title = "CASH Seismograph Data for {}".format(dt.strftime("%d-%m-%Y"))
    data=st.plot(figure=fig, format='png', type='dayplot', 
        interval=60, right_vertical_labels=False,
        vertical_scaling_range=scale, one_tick_per_line=True,
        color=['b', 'g', 'b', 'g'], show_y_UTC_label=True,
        title = title, linewidth=0.5 )
   
    image_base64 = base64.b64encode(data).decode('utf-8').replace('\n', '')
    return image_base64

def plot_detail_data( sts, hour, lower_min, upper_min ):
    """
    Plot the detail data and return the plot as a string
    """

    if hour >= 12:
        idx = hour - 12
    else:
        idx = hour + 12

    try:
        st = sts[idx]
    except:
        return ""
    fig = plt.figure()
    dt = st[0].stats.starttime
    data=st.plot(figure=fig, format='png', color='red', starttime= dt +
        lower_min*60, endtime = dt + upper_min*60, number_of_ticks=5,
        tick_format = ':%M', linewidth=0.5)

    image_base64 = base64.b64encode(data).decode('utf-8').replace('\n', '')
    return image_base64

env = Environment(
   loader=FileSystemLoader('/home/pi/GardenLabServer/cgi')
   ) 

form = cgi.FieldStorage()

if "date" in form:
   default_date =  form["date"].value
else:
   today = datetime.datetime.today()
   default_date = today.strftime('%Y-%m-%d')

if "scale" in form:
   default_scale =  form["scale"].value
else:
    default_scale = 1000

if "hour" in form:
   default_hour =  int(form["hour"].value)
else:
    default_hour = 12

if default_hour > 23:
    default_hour = 23
if default_hour < 0:
    default_hour = 0


if "lower_minute" in form:
   default_lower_minute =  int(form["lower_minute"].value)
else:
    default_lower_minute = 0

if default_lower_minute < 0:
    default_lower_minute = 0
if default_lower_minute > 60:
    default_lower_minute = 59

if "upper_minute" in form:
   default_upper_minute =  int(form["upper_minute"].value)
else:
    default_upper_minute = 60

if default_upper_minute < 0:
    default_upper_minute = 0
if default_upper_minute > 60:
    default_upper_minute = 59


print( "Content-Type: text/html;charset=utf-8")
print("")



context_dict = {}

file_names = get_file_names( default_date )

streams = []
for f in file_names:
    try:
        st = read(f)
        for tr in st:
            tr.stats.sampling_rate = STANDARD_SAMPLING_RATE
        streams.append(st)
    except Exception:
        pass

if len(streams):
    st = streams[0]
if len(streams) > 1:
    for s in streams[1:]:
        st += s

if streams:
    context_dict["plot_string"] = plot_day_data(st, int(default_scale), 
            default_date)
    context_dict["plot_detail_string"] = plot_detail_data( streams,
        default_hour, default_lower_minute,default_upper_minute )
context_dict["default_scale"] = default_scale
context_dict["default_day"] = default_date
context_dict["default_lower_minute"] = default_lower_minute
context_dict["default_upper_minute"] = default_upper_minute
context_dict["default_hour"] = default_hour


template = env.get_template('CASH.html')
print( template.render(context_dict))
