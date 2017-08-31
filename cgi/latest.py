#!/usr/bin/env python
from jinja2 import Environment, FileSystemLoader
import mysql.connector
import datetime


fields = ["id", "ts", "temperature", "humidity", "pressure", "battery_voltage",
          "panel_current", "wind_speed", "rainfall", "wind_direction"]

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







env = Environment(
   loader=FileSystemLoader('/home/pi/GardenLab/cgi')
   ) 

import cgitb

print "Content-Type: text/html;charset=utf-8"
print

DATABASE_NAME="GardenLab"
TABLE_NAME="GardenLabData"

DAY_COND = " where ts > DATE_SUB( NOW(), INTERVAL 1 DAY )"
WEEK_COND = " where ts > DATE_SUB( NOW(), INTERVAL 1 WEEK )"
MONTH_COND = " where ts > DATE_SUB( NOW(), INTERVAL 1 MONTH )"
YEAR_COND = " where ts > DATE_SUB( NOW(), INTERVAL 1 YEAR )"


context_dict = {}


# Read the password and username from an external file:
pd= open("private.data").read().strip()
pd = pd.split(" ")
USER_NAME=pd[0]
PASSWD=pd[1]
    
cnx = mysql.connector.connect(user=USER_NAME, password=PASSWD,
                                 database=DATABASE_NAME )




# Get the latest record in the database:
latest_query = build_query( fields, TABLE_NAME, " ORDER BY id DESC LIMIT 1")

query_db(cnx, latest_query, context_dict)

# Get the min, max and average for the last 24 hours:

min_24_query = build_query( fields, TABLE_NAME, DAY_COND, "MIN")
query_db(cnx, min_24_query, context_dict, "day_min_")

max_24_query = build_query( fields, TABLE_NAME, DAY_COND, "MAX")
query_db(cnx, max_24_query, context_dict, "day_max_")

avg_24_query = build_query( fields, TABLE_NAME, DAY_COND, "AVG")
query_db(cnx, avg_24_query, context_dict, "day_avg_")


min_week_query = build_query( fields, TABLE_NAME, WEEK_COND, "MIN")
query_db(cnx, min_week_query, context_dict, "week_min_")

max_week_query = build_query( fields, TABLE_NAME, WEEK_COND, "MAX")
query_db(cnx, max_week_query, context_dict, "week_max_")

avg_week_query = build_query( fields, TABLE_NAME, WEEK_COND, "AVG")
query_db(cnx, avg_week_query, context_dict, "week_avg_")

min_month_query = build_query( fields, TABLE_NAME, MONTH_COND, "MIN")
query_db(cnx, min_month_query, context_dict, "month_min_")

max_month_query = build_query( fields, TABLE_NAME, MONTH_COND, "MAX")
query_db(cnx, max_month_query, context_dict, "month_max_")

avg_month_query = build_query( fields, TABLE_NAME, MONTH_COND, "AVG")
query_db(cnx, avg_month_query, context_dict, "month_avg_")


min_year_query = build_query( fields, TABLE_NAME, YEAR_COND, "MIN")
query_db(cnx, min_year_query, context_dict, "year_min_")

max_year_query = build_query( fields, TABLE_NAME, YEAR_COND, "MAX")
query_db(cnx, max_year_query, context_dict, "year_max_")

avg_year_query = build_query( fields, TABLE_NAME, YEAR_COND, "AVG")
query_db(cnx, avg_year_query, context_dict, "year_avg_")
cnx.close()









template = env.get_template('latest.html')


print template.render(context_dict)
