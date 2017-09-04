#!/usr/bin/env python
from __future__ import print_function

import os,sys
import cgi
import cgitb; cgitb.enable()


from table import Table
from page import Page
from form import Form
from formselect import FormSelect


fields = [ "temperature", "humidity", "pressure", "battery_voltage",
          "panel_current", "load_current", "wind_speed", "rainfall", "wind_direction"]



def getFormValues(form):
    """
    Returns a dictionary with either the values sent by the form or default values
    for the various form elements
    """
    
    d = {}
    if "field" in form.keys():
        d["field"] = form["field"].value
    else:
        d["field"] = fields[0]
    
    return d





def showPage():

    #Deals with inputing data into python from the html form
    form = cgi.FieldStorage()
    
    
    form_settings = getFormValues(form)
    
    
    
    p = Page("GardenLab Plotting")
    
    f = Form("/cgi/plot.py","POST","Generate Plot")
    fs = FormSelect("field",fields,form_settings["field"], "Data to plot:")
    
    f.addContent(fs)
    
    
    p.addContent(f)
    
    
    
    print(p)
    print(form_settings["field"])



if __name__ == "__main__":
    showPage()

