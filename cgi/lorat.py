#!/usr/bin/python3
##!/usr/bin/env python3
from jinja2 import Environment, FileSystemLoader
import mysql.connector
import datetime
import cgi
import cgitb
cgitb.enable()


def query_db( cnx, cutoff_date, cd ):
    """
    Perform a query of the database and put the HTML table in the 
    context_dict "cd".
    """

    if cutoff_date == None:
        where_clause = ""
    else:
        where_clause = "WHERE dt >= '{}'".format(cutoff_date)

    query = "SELECT * from {} {} ORDER BY ts DESC ".format(LR_TABLE_NAME,
        where_clause) 

    cursor = cnx.cursor()
    cursor.execute(query)

    items = []
    for( id, ts, dt, st ) in cursor:
        an_item = dict( date=ts.strftime("%d %B %Y  %H:%M:%S"), station=st)
        items.append(an_item)
    cursor.close()


    cd["items"] = items
env = Environment(
   loader=FileSystemLoader('/home/pi/GardenLabServer/cgi')
   ) 


print( "Content-Type: text/html;charset=utf-8")
print("")

form = cgi.FieldStorage()
if "date" in form:
   cutoff_date =  form["date"].value
else:
   cutoff_date = (datetime.datetime.today() -
    datetime.timedelta(days=5)).strftime('%Y-%m-%d')



DATABASE_NAME="GardenLab"
LR_TABLE_NAME="LoRatData"

context_dict = {}

# Read the password and username from an external file:
with open("/home/pi/GardenLabServer/private.data") as private_data:
        lines = private_data.readlines()

pd = lines[0].split(" ")
USER_NAME=pd[0].strip()
PASSWD=pd[1].strip()



    
cnx = mysql.connector.connect(user=USER_NAME, password=PASSWD,
                                 database=DATABASE_NAME )




query_db(cnx, cutoff_date, context_dict)


cnx.close()



template = env.get_template('lorat.html')


if cutoff_date:
    context_dict["default_cutoff"] = cutoff_date


print( template.render(context_dict))
