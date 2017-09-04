#!/usr/bin/env python
from __future__ import print_function

import os,sys
import cgi
import cgitb; cgitb.enable()

fields = [ "temperature", "humidity", "pressure", "battery_voltage",
          "panel_current", "load_current", "wind_speed", "rainfall", "wind_direction"]


from table import Table
from page import Page
from form import Form
from formselect import FormSelect


p = Page("GardenLab Plotting")

f = Form("/cgi/plot.py","POST")
fs = FormSelect("field",fields,"temperature", "Data to plot:")

f.addContent(fs)


p.addContent(f)



print(p)



