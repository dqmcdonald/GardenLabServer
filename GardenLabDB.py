# Database module for GardenLab server/database
# Intended to be imported from the server script but can also be run to
# perform some database utilities such as creating the database.
# Run "GardenLab.py -c" to create the database


import argparse
import mysql.connector
import time
import smtplib
import pickle
import os
import datetime

DATABASE_NAME="GardenLab"
TABLE_NAME="GardenLabData"
SM_TABLE_NAME="SoilMoistureData"
LR_TABLE_NAME="LoRatData"
ST_TABLE_NAME="SkyTemperatureData"

# Read the password and username from an external file:

with open("/home/pi/GardenLabServer/private.data") as private_data:
	lines = private_data.readlines()

pd = lines[0].split(" ")
USER_NAME=pd[0].strip()
PASSWD=pd[1].strip()

pd = lines[1].split(" ")
GMAIL_USER=pd[0].strip()
GMAIL_PASSWORD=pd[1].strip()

LAST_EMAIL_DATA_FILE = '/home/pi/GardenLabServer/last_email.data'
LAST_UPDATE_DATA_FILE = '/home/pi/GardenLabServer/last_update.data'

LEMON_ADDRESS = ['dqmcdonald@gmail.com','beatrice.cheer@gmail.com']
VEGE_ADDRESS = ['dqmcdonald@gmail.com' ]
EIGHTYA_ADDRESS = ['dqmcdonald@gmail.com' ]
SKYTEMP_ADDRESS = ['dqmcdonald@gmail.com' ]

NO_UPDATE_ADDRESS = ['dqmcdonald@gmail.com' ]

VEGE_KEY =    'MOIS01'
LEMON_KEY =   'MOIS02'
EIGHTYA_KEY = 'MOIS03'
SKYTEMP_KEY = 'SKYTMP'

# Time threshold in seconds
TIME_THRESHOLD = 60*60*3  # 3 hours



# arbitrary default date for starting point, only needs to be some time
# in the past.
default_date = datetime.date(2020,1,27)

# Stores the date when the last email was sent. Pickled to a file and used
# to only send a single email per-day
last_emails = { LEMON_KEY:default_date,
                VEGE_KEY:default_date,
                EIGHTYA_KEY:default_date,
                SKYTEMP_KEY:default_date }

default_datetime = datetime.datetime(2022,1,27,9,21,0)
last_updates = { LEMON_KEY:default_datetime,
                VEGE_KEY:default_datetime,
                EIGHTYA_KEY:default_datetime,
                SKYTEMP_KEY:default_datetime }


# Descriptive names used to send email:
MOISTURE_EMAIL_NAMES = { 
                LEMON_KEY:   "lemon tree",
                VEGE_KEY:    "vegetable garden",
                EIGHTYA_KEY: "80A section" ,
                SKYTEMP_KEY: "Sky Temperature sensor" }


# Thresholds - 
MOISTURE_EMAIL_THRESHOLDS = { 
                LEMON_KEY:   780,
                VEGE_KEY:    780,
                EIGHTYA_KEY: 200 }

# Email addresses to be used for each moisture sensor:
MOISTURE_EMAIL_ADDRESSES = { 
                LEMON_KEY:LEMON_ADDRESS,
                VEGE_KEY:VEGE_ADDRESS,
                EIGHTYA_KEY:EIGHTYA_ADDRESS,
                SKYTEMP_KEY:SKYTEMP_ADDRESS}

# if the pickled file with email dates exists then read it now:
if os.path.exists(LAST_EMAIL_DATA_FILE):
    last_emails = pickle.load(open(LAST_EMAIL_DATA_FILE, "rb"))

# read the last updates if appropriate:
if os.path.exists(LAST_UPDATE_DATA_FILE):
    last_updates = pickle.load(open(LAST_UPDATE_DATA_FILE, "rb"))


# Data table Schema:
DATA_TABLE_DEF = {}
DATA_TABLE_DEF[TABLE_NAME] = ("CREATE TABLE `{0}` ("
                              " `id` int(11) NOT NULL AUTO_INCREMENT,"
                              " `ts` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
                              " `dt` DATE  NOT NULL,"
                              " `temperature` float NOT NULL, "
                              " `humidity` float not NULL, "
                              " `int_temp` float not NULL, "
                              " `pressure` float not NULL, "
                              " `load_current` float not NULL, "
                              " `battery_voltage` float not NULL, "
                              " `wind_speed` float not NULL, "
                              " `wind_direction` float not NULL, "
                              " `rainfall` float not NULL,"
                              " `panel_current` float not NULL,"
                              " PRIMARY KEY (`id`) )".format(TABLE_NAME) )
                

DATA_TABLE_DEF[SM_TABLE_NAME] = ("CREATE TABLE `{0}` ("
                              " `id` int(11) NOT NULL AUTO_INCREMENT,"
                              " `ts` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
                              " `dt` DATE  NOT NULL,"
                              " `moisture` float NOT NULL, "
                              " `soil_temperature` float not NULL, "
                              " `has_temperature` integer not NULL, "
                              " `station` char(6) NOT NULL, "
                              " PRIMARY KEY (`id`) )".format(SM_TABLE_NAME) )

DATA_TABLE_DEF[ST_TABLE_NAME] = ("CREATE TABLE `{0}` ("
                              " `id` int(11) NOT NULL AUTO_INCREMENT,"
                              " `ts` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
                              " `dt` DATE  NOT NULL,"
                              " `sky_temperature` float not NULL, "
                              " `station` char(6) NOT NULL, "
                              " PRIMARY KEY (`id`) )".format(ST_TABLE_NAME) )


DATA_TABLE_DEF[LR_TABLE_NAME] = ("CREATE TABLE `{0}` ("
                              " `id` int(11) NOT NULL AUTO_INCREMENT,"
                              " `ts` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
                              " `dt` DATE  NOT NULL,"
                              " `station` char(8) NOT NULL, "
                              " PRIMARY KEY (`id`) )".format(LR_TABLE_NAME) )


INSERT_DEF = ("INSERT into GardenLabData "
              "(dt, temperature, humidity, int_temp, pressure, load_current,"
              " battery_voltage, wind_speed, wind_direction, rainfall, panel_current ) "
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")


SM_INSERT_DEF = ("INSERT into SoilMoistureData "
              "(dt, moisture, soil_temperature, has_temperature, station ) "
              "VALUES (%s, %s, %s, %s, %s )")

ST_INSERT_DEF = ("INSERT into SkyTemperatureData "
              "(dt, sky_temperature, station ) "
              "VALUES (%s, %s, %s )")

LR_INSERT_DEF = ("INSERT into LoRatData "
              "(dt, station ) "
              "VALUES (%s, %s )")


LATEST_QUERY_SQL = ("SELECT ts,{0} FROM GardenLabData WHERE ts > DATE_SUB("
             "NOW(),  INTERVAL 24 HOUR)" )


TEMPERATURE_KEY = 'TEMP'
HUMIDITY_KEY = 'HUMI'
INTERNAL_TEMP_KEY = 'ITMP'
PRESSURE_KEY = 'PRES'
LOAD_CURRENT_KEY = 'LCUR'
BATTERY_VOLTAGE_KEY = 'BATV'
WIND_SPEED_KEY = 'WSPD'
WIND_DIRECTION_KEY = 'WDIR'
WIND_SPEED_KEY = 'WSPD'
RAINFALL_KEY = 'RAIN'
PANEL_CURRENT_KEY = 'PCUR'
SOIL_TEMPERATURE_KEY = 'SOILTEMP'
STATION_KEY = 'STATION'
MOISTURE_KEY = 'MOISTURE'
SKY_TEMPERATURE_KEY = 'SKYTEMP'
LORAT_KEY = 'LORAT'



def getopts():
    description = 'GardenLabDB.py - GardenLab Database Module'
    epilog = ' '
    rawd = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=rawd,
                                     description=description,
                                     epilog=epilog)
    parser.add_argument('-c','--create',
                        action='store_true',
                        help='Create database')

    parser.add_argument('-s','--sm_create',
                        action='store_true',
                        help='Create SM database')

    parser.add_argument('-r','--lr_create',
                        action='store_true',
                        help='Create LoRat database')

    parser.add_argument('-k','--st_create',
                        action='store_true',
                        help='Create Sky Temp database')

    parser.add_argument('-l','--list',
                        action='store_true',
                        help='List last record ')

    parser.add_argument('-t','--tdata',
                        action='store_true',
                        help='Add a test record')

    opts = parser.parse_args()

    opts = parser.parse_args()
    return opts
    

def create_table():
    """
    Create the database table and define the fields
    """
    cnx = open_database()
    
    cursor = cnx.cursor()
    print("Deleting table")
    try:
        cursor.execute("DROP TABLE `{0}`".format(TABLE_NAME))
    except:
        pass
    print("Creating data with SQL expression")
    print(DATA_TABLE_DEF[TABLE_NAME])
    cursor.execute(DATA_TABLE_DEF[TABLE_NAME])
    cnx.close()

def create_sm_table():
    """
    Create the soil moisture database table and define the fields
    """
    cnx = open_database()
    
    cursor = cnx.cursor()
    print("Deleting table")
    try:
        cursor.execute("DROP TABLE `{0}`".format(SM_TABLE_NAME))
    except:
        pass
    print("Creating data with SQL expression")
    print(DATA_TABLE_DEF[SM_TABLE_NAME])
    cursor.execute(DATA_TABLE_DEF[SM_TABLE_NAME])
    cnx.close()

def create_st_table():
    """
    Create the sky tempertuare database table and define the fields
    """
    cnx = open_database()
    
    cursor = cnx.cursor()
    print("Deleting table")
    try:
        cursor.execute("DROP TABLE `{0}`".format(ST_TABLE_NAME))
    except:
        pass
    print("Creating data with SQL expression")
    print(DATA_TABLE_DEF[ST_TABLE_NAME])
    cursor.execute(DATA_TABLE_DEF[ST_TABLE_NAME])
    cnx.close()

def create_lr_table():
    """
    Create the LoRat database table and define the fields
    """
    cnx = open_database()
    
    cursor = cnx.cursor()
    print("Deleting table")
    try:
        cursor.execute("DROP TABLE `{0}`".format(LR_TABLE_NAME))
    except:
        pass
    print("Creating data with SQL expression")
    print(DATA_TABLE_DEF[LR_TABLE_NAME])
    cursor.execute(DATA_TABLE_DEF[LR_TABLE_NAME])
    cnx.close()



def test_data():
    """
    Inserts some test data into the DB
    """
    
    temp = 22.0
    humi = 76.9
    itmp = 21.9
    pres = 1016
    lcur = 0.2
    batv = 13.0
    wspeed = 0.0
    wdir = 180.0
    rain = 0.0
    pcur = 0.51

    cnx = open_database()
    
    cursor = cnx.cursor()
    data = (time.strftime("%Y-%m-%d"), temp,humi,itmp,pres,lcur,batv,wspeed,wdir,rain,pcur)
    print(data)
    cursor.execute(INSERT_DEF, data)
    cnx.commit()

    query = ("SELECT ts, temperature FROM GardenLabData")
    cursor.execute(query)
    for( ts, temperature) in cursor:
        print( ts, temperature)
    
    cursor.close()
    cnx.close()



def list_last_record():
    """
    List the last record added to the DB
    """
   
    cnx = open_database()
    
    cursor = cnx.cursor()

    query = ("SELECT ts, temperature FROM GardenLabData ORDER BY id DESC LIMIT 1")
    cursor.execute(query)
    for( ts, temperature) in cursor:
        print( ts, temperature)
    
    cursor.close()
    cnx.close()


def send_lora_email( station ):
    """
    Send email to notifiy of rat trap being set off
    """


    sent_from = GMAIL_USER
    to = ['dqmcdonald@gmail.com']
    subject = 'Rat Trap Triggered'

    email_text = """\
From: %s
To: %s
Subject: %s

Trap triggered: %s
""" % (sent_from, to, subject, station)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(sent_from, to, email_text)
        server.close()

        print( 'Email sent!')
    except:
        print( 'Something went wrong...')


def insert_sky_temperature_data( post_args ):
    """
    Insert values into SkyTemperature DB table from the args dictionary
    """
    sky_temperature = 0.0
    sky_temperature = float(post_args[SKY_TEMPERATURE_KEY][0])
    sky_temperature = sky_temperature/1000.0  # Was stored as integer

    station = (post_args[STATION_KEY][0]).decode("utf-8") 

    cnx = mysql.connector.connect(user=USER_NAME, password=PASSWD,
                                 database=DATABASE_NAME )
    
    cursor = cnx.cursor()
    cursor.execute(ST_INSERT_DEF,(time.strftime("%Y-%m-%d"),
       sky_temperature, station ))
    cnx.commit()
    cursor.close()
    cnx.close()

    # Update the datetime when new data is inserted into the database
    last_updates[station] = datetime.datetime.now()
    pickle.dump(last_updates, open(LAST_UPDATE_DATA_FILE, "wb"))



def insert_soil_moisture_data( post_args ):
    """
    Insert values into SoilMoisture DB table from the args dictionary
    """
    moisture = 0.0
    try:
        moisture = float(post_args[MOISTURE_KEY][0])
    except:
        moisture = 0.0

    soil_temperature = 0.0
    try:
        soil_temperature = float(post_args[SOIL_TEMPERATURE_KEY][0])
        soil_temperature = soil_temperature/100.0  # Was stored as integer
        has_temperature = 1
    except:
        has_temperature = 0

    station = (post_args[STATION_KEY][0]).decode("utf-8") 

    cnx = mysql.connector.connect(user=USER_NAME, password=PASSWD,
                                 database=DATABASE_NAME )
    
    cursor = cnx.cursor()
    cursor.execute(SM_INSERT_DEF,(time.strftime("%Y-%m-%d"),moisture, 
       soil_temperature, has_temperature, station ))
    cnx.commit()
    cursor.close()
    cnx.close()

    if not has_temperature:
        # only for moisture data:
        if int(moisture) < MOISTURE_EMAIL_THRESHOLDS[station]:
            send_moisture_email( MOISTURE_EMAIL_ADDRESSES[station], 
                            MOISTURE_EMAIL_NAMES[station],  
                            MOISTURE_EMAIL_THRESHOLDS[station],  
                            int(moisture), station )
        
        # Update the datetime when new data is inserted into the database
        last_updates[station] = datetime.datetime.now()
        pickle.dump(last_updates, open(LAST_UPDATE_DATA_FILE, "wb"))



def insert_lorat_data( post_args ):
    """
    Insert values into LoRat DB table from the args dictionary
    """

    station = (post_args[LORAT_KEY][0]).decode("utf-8") 

    cnx = mysql.connector.connect(user=USER_NAME, password=PASSWD,
                                 database=DATABASE_NAME )
    
    cursor = cnx.cursor()
    cursor.execute(LR_INSERT_DEF,(time.strftime("%Y-%m-%d"), station ))
    cnx.commit()
    cursor.close()
    cnx.close()

    send_lora_email( station )


def insert_gardenlab_data( post_args ):
    """
    Insert values into GardenLab DB table from the args dictionary
    """
    temp = float(post_args[TEMPERATURE_KEY][0])
    humi = float(post_args[HUMIDITY_KEY][0])
    itmp = float(post_args[INTERNAL_TEMP_KEY][0])
    pres = float(post_args[PRESSURE_KEY][0])/100.0;  # Convert to HPa
    lcur = float(post_args[LOAD_CURRENT_KEY][0])
    batv = float(post_args[BATTERY_VOLTAGE_KEY][0])
    wspeed = float(post_args[WIND_SPEED_KEY][0])
    wdir = float(post_args[WIND_DIRECTION_KEY][0])
    rain = float(post_args[RAINFALL_KEY][0])
    if rain > 2.0:  # More than 2mm in 5min is spurious (shaking etc)
       rain = 0.0
    try:
       pcur = float(post_args[PANEL_CURRENT_KEY][0])
    except:
       pcur = 0.0

    cnx = mysql.connector.connect(user=USER_NAME, password=PASSWD,
                                 database=DATABASE_NAME )
    
    cursor = cnx.cursor()
    cursor.execute(INSERT_DEF,(time.strftime("%Y-%m-%d"),temp,humi,itmp,pres,lcur,batv,wspeed,wdir,rain, pcur))
    cnx.commit()
    cursor.close()
    cnx.close()



def insert_data_from_dict( post_args ):
    """
    Insert values into DB table from the args dictionary
    """

    if MOISTURE_KEY in post_args or SOIL_TEMPERATURE_KEY in post_args:
        insert_soil_moisture_data( post_args )
    elif SKY_TEMPERATURE_KEY in post_args:
        insert_sky_temperature_data( post_args )
    elif LORAT_KEY in post_args:
        insert_lorat_data( post_args )
    else:
        insert_gardenlab_data( post_args )

    # Check the updates for the moisture sensors and see if there
    # has been an updated within the time threshold:
    now = datetime.datetime.now()
    for key in last_updates:
        delta = now - last_updates[key] 
        if delta.seconds > TIME_THRESHOLD:
            send_no_update_email(NO_UPDATE_ADDRESS , key)
            
    


def count_records():
    """
    Return the number of records
    """
    cnx = mysql.connector.connect(user=USER_NAME, password=PASSWD,
                                 database=DATABASE_NAME )
    
    cursor = cnx.cursor()

    query = ("SELECT COUNT(*) FROM GardenLabData")
    cursor.execute(query)
    for(cnt) in cursor:
        count = cnt
    
    cursor.close()
    cnx.close()

    return count





def open_database():
    """
    Opens a connector to the database and returns it
    """
    cnx = mysql.connector.connect(user=USER_NAME, password=PASSWD,
                                 database=DATABASE_NAME )
    return cnx
    

def last_day_data( field ) :
    """
    Returns two arrays - the first is the times we have data over
    the last 24hrs, the second the data for the specified field
    """

    dates = []
    data = []

    cnx = open_database()
    cursor = cnx.cursor()


    # handle soil moisture and temperature differently:
    query = ""
    if field == 'vege_moisture':
          query = ("SELECT ts,moisture FROM SoilMoistureData WHERE ts > DATE_SUB( NOW(),  INTERVAL 24 HOUR) and has_temperature = 0 and station = 'MOIS01'" )

    elif field == 'vege_temperature':
          query = ("SELECT ts,soil_temperature FROM SoilMoistureData WHERE ts > DATE_SUB( NOW(),  INTERVAL 24 HOUR) and has_temperature = 1 and station = 'MOIS01'" )
    elif field == 'lemon_moisture':
          query = ("SELECT ts,moisture FROM SoilMoistureData WHERE ts > DATE_SUB( NOW(),  INTERVAL 24 HOUR) and has_temperature = 0 and station = 'MOIS02'" )
    elif field == '80A_moisture':
          query = ("SELECT ts,moisture FROM SoilMoistureData WHERE ts > DATE_SUB( NOW(),  INTERVAL 24 HOUR) and has_temperature = 0 and station = 'MOIS03'" )
    elif field == 'sky_temperature':
          query = ("SELECT ts,sky_temperature FROM SkyTemperatureData WHERE ts > DATE_SUB( NOW(),  INTERVAL 24 HOUR)" )
    else:
          query = LATEST_QUERY_SQL.format(field)
 
    cursor.execute( query )

    for( dt, val) in cursor:
        dates.append(dt)
        data.append(val)

    cursor.close()
    cnx.close()
    return (dates,data)


def send_moisture_email( address, station, threshold, value, key ):
    """
    Send email to notify that the soil moisture level has
    fallen below the threshold.
    """


    sent_from = GMAIL_USER
    to = address
    subject = 'Soil moisture warning - {}'.format( station )

    email_text = """\
From: {}
To: {}
Subject: {}

The moisture level for the {} has fallen to {:d} which is below the
threshold of {:d}. 

Please water this area soon!


""" .format(sent_from, to, subject, station, value, threshold )


    # Check the date and only send email if we haven't today:
    today = datetime.date.today()
    if last_emails[key] == today:
        print("Nothing to do")
        return


    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(sent_from, to, email_text)
        server.close()

        print( 'Email sent!')
        # Save the current date as that in which an email was sent so we
        # don't send another email today even if we are under the threshold.
        last_emails[key] = today
        pickle.dump(last_emails, open(LAST_EMAIL_DATA_FILE, "wb"))


    except:
        print( 'Something went wrong...')


def send_no_update_email( address, key):
    """
    Send email to notify that no update has been 
    made for some time.
    """

    station =  MOISTURE_EMAIL_NAMES[key]

    sent_from = GMAIL_USER
    to = address
    subject = 'Data update warning- {}'.format( station )

    email_text = """\
From: {}
To: {}
Subject: {}

No data has been received from {} for some time. Please check the battery
or the receiver. 


""" .format(sent_from, to, subject, station )


    # Check the date and only send email if we haven't today:
    today = datetime.date.today()
    if last_emails[key] == today:
        print("Nothing to do")
        return


    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(sent_from, to, email_text)
        server.close()

        print( 'Email sent!')
        # Save the current date as that in which an email was sent so we
        # don't send another email today even if we are under the threshold.
        last_emails[key] = today
        pickle.dump(last_emails, open(LAST_EMAIL_DATA_FILE, "wb"))


    except:
        print( 'Something went wrong...')




def main():
      opts = getopts()
      if opts.create:
          create_table()
      if opts.list:
          list_last_record()
      if opts.tdata:
          test_data()
      if opts.sm_create:
          create_sm_table()
      if opts.st_create:
          create_st_table()
      if opts.lr_create:
          create_lr_table()
          


if __name__ == "__main__":
    main()
