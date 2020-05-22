#!/usr/bin/python3
##!/usr/bin/env python3
from jinja2 import Environment, FileSystemLoader
import mysql.connector
import datetime
import cgi
import cgitb
import os
import sys
import matplotlib.pyplot as plt
from io import BytesIO
import base64


cgitb.enable()


DATABASE_NAME="GardenLab"
TABLE_NAME="GardenLabData"

def plot_data( dates, data ):
    """
    Plot the data and return the plot as a string
    """
    fig = plt.figure()
    plt.plot(dates, data )
    figdata = BytesIO()
    fig.savefig(figdata, format='png')
   
    image_base64 = base64.b64encode(figdata.getvalue()).decode(
       'utf-8').replace('\n', '')
    figdata.close()
    return image_base64


def query_db( cnx, field):
    """
    Perform a query of the database for field and return a tuple of lists
    - time and value
    """

    cursor = cnx.cursor()
    query = ("SELECT ts, {} from {} WHERE ts > DATE_SUB(NOW(),  INTERVAL 24 HOUR)".format(field, TABLE_NAME));
    cursor.execute(query)

    dates = []
    data = []
    for( dt, val ) in cursor:
        dates.append(dt)
        data.append(val)
    cursor.close()

    return( dates, data)

env = Environment(
   loader=FileSystemLoader('/home/pi/GardenLabServer/cgi')
   ) 


print( "Content-Type: text/html;charset=utf-8")
print("")


form = cgi.FieldStorage()
form = cgi.FieldStorage()
if "field" in form:
   field_type =  form["field"].value
else:
   field_type = "temperature"


context_dict = {}

if field_type == "temperture":
    context_dict["temperature_selected"] = "selected"
elif field_type == "humidity":
    context_dict["humidity_selected"] = "selected"

# Read the password and username from an external file:
with open("/home/pi/GardenLabServer/private.data") as private_data:
        lines = private_data.readlines()

pd = lines[0].split(" ")
USER_NAME=pd[0].strip()
PASSWD=pd[1].strip()

    
cnx = mysql.connector.connect(user=USER_NAME, password=PASSWD,
                                 database=DATABASE_NAME )


(dates,data) = query_db(cnx, field_type)



context_dict["plot_string"] = plot_data( dates, data )


cnx.close()
template = env.get_template('plot.html')
print( template.render(context_dict))
