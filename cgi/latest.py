#!/usr/bin/python3
##!/usr/bin/env python3
from jinja2 import Environment, FileSystemLoader
import mysql.connector
import datetime

import cgitb
cgitb.enable()


vege_moisture_fields = ["ts","moisture"]
lemon_moisture_fields = ["ts","moisture"]

def build_query( fields, table, condition, func=None):
    """
    Builds and SQL query to retrieve fields from table with condition
    If func is not None then it applied to each field
    """

    if func is not None:
        new_fields = ["%s(%s)" %(func,f) for f in fields]
    else:
        new_fields = fields
    q = "SELECT "
    q += ", ".join( new_fields )
    q += " FROM "
    q += table
    q += condition
    return q
    


def vege_moisture_query_db( cnx, query, cd, prefix = "" ):
    """
    Perform a query of the database and update dictionary "cd" with the
    results for the vege garden moisture sensor
    """

    cursor = cnx.cursor()
    cursor.execute(query)

    for( ts, moisture ) in cursor:
        if moisture is not None:
            cd[prefix+"vege_moisture"] = "{:3.0f}".format(moisture)
        if prefix == "":
            cd["vege_time_stamp"]=ts.strftime("%H:%M:%S  %d %B %Y")
        else:
            cd[prefix+"vege_time_stamp"] = ts
        

    cursor.close()

def lemon_moisture_query_db( cnx, query, cd, prefix = "" ):
    """
    Perform a query of the database and update dictionary "cd" with the
    results for the lemon pot moisture sensor
    """

    cursor = cnx.cursor()
    cursor.execute(query)

    for( ts, moisture ) in cursor:
        if moisture is not  None:
            cd[prefix+"lemon_moisture"] = "{:3.0f}".format(moisture)
        if prefix == "":
            cd["lemon_time_stamp"]=ts.strftime("%H:%M:%S  %d %B %Y")
        else:
            cd[prefix+"lemon_time_stamp"] = ts
        

    cursor.close()


def vege_temperature_query_db( cnx, query, cd, prefix = "" ):
    """
    Perform a query of the database and update dictionary "cd" with the
    results for the vege garden temp sensor
    """

    cursor = cnx.cursor()
    cursor.execute(query)

    for( soil_temperature ) in cursor:
        if soil_temperature[0] is not None:
            cd[prefix+"vege_soil_temperature"] = "{:3.1f}".format(
                soil_temperature[0])

    cursor.close()


env = Environment(
   loader=FileSystemLoader('/home/pi/GardenLabServer/cgi')
   ) 


print( "Content-Type: text/html;charset=utf-8")
print("")

DATABASE_NAME="GardenLab"
SM_TABLE_NAME="SoilMoistureData"

DAY_COND = " where ts > DATE_SUB( NOW(), INTERVAL 1 DAY )"
WEEK_COND = " where ts > DATE_SUB( NOW(), INTERVAL 1 WEEK )"
MONTH_COND = " where ts > DATE_SUB( NOW(), INTERVAL 1 MONTH )"
YEAR_COND = " where ts > DATE_SUB( NOW(), INTERVAL 1 YEAR )"

PERIODS = [("day",DAY_COND),("week",WEEK_COND),("month",MONTH_COND),
           ("year",YEAR_COND)]
FUNCS = [("min","MIN"), ("max","MAX"), ("avg","AVG"), ("sum","SUM" )]


context_dict = {}


# Read the password and username from an external file:
with open("/home/pi/GardenLabServer/private.data") as private_data:
        lines = private_data.readlines()

pd = lines[0].split(" ")
USER_NAME=pd[0].strip()
PASSWD=pd[1].strip()

    
cnx = mysql.connector.connect(user=USER_NAME, password=PASSWD,
                                 database=DATABASE_NAME )

# Get the latest record in the database:
vege_latest_query = build_query( vege_moisture_fields, SM_TABLE_NAME, 
 " WHERE station='MOIS01' AND has_temperature=0 ORDER BY id DESC LIMIT 1")
vege_moisture_query_db(cnx, vege_latest_query, context_dict)

lemon_latest_query = build_query( lemon_moisture_fields, SM_TABLE_NAME, 
 " WHERE station='MOIS02' AND has_temperature=0 ORDER BY id DESC LIMIT 1")
lemon_moisture_query_db(cnx, lemon_latest_query, context_dict)


# Get the min, max and average for the last 24 hours:

for (plab,period) in PERIODS:
    for ( flab, func) in FUNCS:
        condition = "{} {}".format(period, "AND station='MOIS01' AND has_temperature=0")
        query = build_query(vege_moisture_fields, SM_TABLE_NAME, condition,func)
        vege_moisture_query_db(cnx, query, context_dict, "%s_%s_"%(plab,flab))

        condition = "{} {}".format(period, "AND station='MOIS02' AND has_temperature=0")
        query = build_query(lemon_moisture_fields, SM_TABLE_NAME, condition,func)
        lemon_moisture_query_db(cnx, query, context_dict, "%s_%s_"%(plab,flab))


cnx.close()



template = env.get_template('latest.html')


print( template.render(context_dict))
