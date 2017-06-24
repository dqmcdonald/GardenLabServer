#!/usr/bin/env python
from jinja2 import Environment, FileSystemLoader
import mysql.connector
import datetime


env = Environment(
   loader=FileSystemLoader('/home/pi/GardenLab/cgi')
   ) 

import cgitb

print "Content-Type: text/html;charset=utf-8"
print

DATABASE_NAME="GardenLab"
TABLE_NAME="GardenLabData"

# Read the password and username from an external file:
pd= open("private.data").read().strip()
pd = pd.split(" ")
USER_NAME=pd[0]
PASSWD=pd[1]
    
cnx = mysql.connector.connect(user=USER_NAME, password=PASSWD,
                                 database=DATABASE_NAME )

cursor = cnx.cursor()


# Get the latest record in the database:

query = ("SELECT id, ts, temperature, humidity, pressure, battery_voltage, load_current, wind_speed  FROM GardenLabData"
         " ORDER BY id DESC LIMIT 1")
cursor.execute(query)

for( id, ts, tmp,h,p, v, lc, ws ) in cursor:
    timestamp=ts.strftime("%H:%M:%S  %d %B %Y")
    temperature = tmp
    humidity=h
    pressure=p
    battery_voltage = v
    load_current = lc
    wind_speed = ws
    
cursor.close()
cnx.close()


template = env.get_template('latest.html')

print template.render(time_stamp=timestamp,temperature=temperature,
                      humidity=humidity, pressure=int(pressure), 
      battery_voltage=battery_voltage, wind_speed = wind_speed, 
	load_current=load_current)
