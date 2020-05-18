#!/usr/bin/python3
##!/usr/bin/env python3
from jinja2 import Environment, FileSystemLoader
import mysql.connector
import datetime


fields = ["id", "ts", "temperature", "humidity", "pressure", "battery_voltage",
          "panel_current", "wind_speed", "rainfall", "wind_direction"]

vege_moisture_fields = ["moisture"]
vege_temperature_fields = ["soil_temperature"]

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
    


def query_db( cnx, query, cd, prefix = "" ):
    """
    Perform a query of the database and update dictionary "cd" with the
    results
    """

    cursor = cnx.cursor()
    cursor.execute(query)

    for( id, ts, tmp,h,p, v, pc, ws, rf, wd ) in cursor:
        if prefix == "":
            cd["time_stamp"]=ts.strftime("%H:%M:%S  %d %B %Y")
        else:
            cd[prefix+"time_stamp"] = ts
        cd[prefix+"temperature"] = "%3.1f"%tmp
        cd[prefix+"humidity"]="%3.1f"%h
        cd[prefix+"pressure"]=int(p)
        cd[prefix+"battery_voltage"] = "%5.2f"%v
        cd[prefix+"panel_current"] = "%5.3f"%pc
        cd[prefix+"wind_speed"] = "%3.1f"%ws
        cd[prefix+"rainfall"]= "%3.1f"%rf
        cd[prefix+"wind_direction"] = wd

    cursor.close()


def vege_moisture_query_db( cnx, query, cd, prefix = "" ):
    """
    Perform a query of the database and update dictionary "cd" with the
    results for the vege garden moisture sensor
    """

    cursor = cnx.cursor()
    cursor.execute(query)

    for( moisture ) in cursor:
        cd[prefix+"vege_moisture"] = "%3d"%moisture

    cursor.close()

def vege_temperature_query_db( cnx, query, cd, prefix = "" ):
    """
    Perform a query of the database and update dictionary "cd" with the
    results for the vege garden temp sensor
    """

    cursor = cnx.cursor()
    cursor.execute(query)

    for( soil_temperature ) in cursor:
        cd[prefix+"vege_soil_temperature"] = "%3.1f"%soil_temperature

    cursor.close()


env = Environment(
   loader=FileSystemLoader('/home/pi/GardenLabServer/cgi')
   ) 

import cgitb

print( "Content-Type: text/html;charset=utf-8")
print("")

DATABASE_NAME="GardenLab"
TABLE_NAME="GardenLabData"
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
pd= open("/home/pi/GardenLabServer/private.data").read().strip()
pd = pd.split(" ")
USER_NAME=pd[0]
PASSWD=pd[1]
    
cnx = mysql.connector.connect(user=USER_NAME, password=PASSWD,
                                 database=DATABASE_NAME )




# Get the latest record in the database:
latest_query = build_query( fields, TABLE_NAME, " ORDER BY id DESC LIMIT 1")
query_db(cnx, latest_query, context_dict)

vege_latest_query = build_query( vege_moisture_fields, SM_TABLE_NAME, 
 " WHERE station='MOIS01' AND has_temperature=0 ORDER BY id DESC LIMIT 1")
vege_moisture_query_db(cnx, vege_latest_query, context_dict)

vege_latest_query = build_query( vege_temperature_fields, SM_TABLE_NAME, 
 " WHERE station='MOIS01' AND has_temperature=1 ORDER BY id DESC LIMIT 1")
vege_temperature_query_db(cnx, vege_latest_query, context_dict)

# Get the min, max and average for the last 24 hours:

for (plab,period) in PERIODS:
    for ( flab, func) in FUNCS:
        query = build_query(fields, TABLE_NAME, period,func)
        query_db(cnx, query, context_dict, "%s_%s_"%(plab,flab))

        condition = "{} {}".format(period, "AND station='MOIS01' AND has_temperature=0")
        query = build_query(vege_moisture_fields, SM_TABLE_NAME, condition,func)
        vege_moisture_query_db(cnx, query, context_dict, "%s_%s_"%(plab,flab))

        condition = "{} {}".format(period, "AND station='MOIS01' AND has_temperature=1")
        query = build_query(vege_temperature_fields, SM_TABLE_NAME, 
		condition,func)
        vege_temperature_query_db(cnx, query, context_dict, "%s_%s_"%(plab,flab))



cnx.close()



template = env.get_template('latest.html')


print( template.render(context_dict))
