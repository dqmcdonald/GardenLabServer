# Database module for GardenLab server/database
# Intended to be imported from the server script but can also be run to
# perform some database utilities such as creating the database.
# Run "GardenLab.py -c" to create the database


import argparse
import mysql.connector
import time

DATABASE_NAME="GardenLab"
TABLE_NAME="GardenLabData"

# Read the password and username from an external file:
pd= open("private.data").read().strip()
pd = pd.split(" ")
USER_NAME=pd[0]
PASSWD=pd[1]
    

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
                              " PRIMARY KEY (`id`) )".format(TABLE_NAME) )
                


INSERT_DEF = ("INSERT into GardenLabData "
              "(dt, temperature, humidity, int_temp, pressure, load_current,"
              " battery_voltage, wind_speed, wind_direction, rainfall ) "
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s )")



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

    parser.add_argument('-l','--list',
                        action='store_true',
                        help='List last record ')

    opts = parser.parse_args()
    return opts
    

def create_table():
    """
    Create the database table and define the fields
    """
    cnx = mysql.connector.connect(user=USER_NAME, password=PASSWD,
                                 database=DATABASE_NAME )
    
    cursor = cnx.cursor()
    print "Deleting table"
    try:
        cursor.execute("DROP TABLE `{0}`".format(TABLE_NAME))
    except:
        pass
    print "Creating data with SQL expression"
    print DATA_TABLE_DEF[TABLE_NAME]
    cursor.execute(DATA_TABLE_DEF[TABLE_NAME])
    cnx.close()

    test_data()               

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

    cnx = mysql.connector.connect(user=USER_NAME, password=PASSWD,
                                 database=DATABASE_NAME )
    
    cursor = cnx.cursor()
    data = (time.strftime("%Y-%m-%d"), temp,humi,itmp,pres,lcur,batv,wspeed,wdir,rain)
    print data
    cursor.execute(INSERT_DEF, data)
    cnx.commit()

    query = ("SELECT ts, temperature FROM GardenLabData")
    cursor.execute(query)
    for( ts, temperature) in cursor:
        print ts, temperature
    
    cursor.close()
    cnx.close()


def list_last_record():
    """
    List the last record added to the DB
    """
   
    cnx = mysql.connector.connect(user=USER_NAME, password=PASSWD,
                                 database=DATABASE_NAME )
    
    cursor = cnx.cursor()

    query = ("SELECT ts, temperature FROM GardenLabData ORDER BY 'id' DESC LIMIT 1")
    cursor.execute(query)
    for( ts, temperature) in cursor:
        print ts, temperature
    
    cursor.close()
    cnx.close()

def insert_data_from_dict( post_args ):
    """
    Insert values into DB table from the args dictionary
    """

    temp = float(post_args[TEMPERATURE_KEY][0])
    humi = float(post_args[HUMIDITY_KEY][0])
    itmp = float(post_args[INTERNAL_TEMP_KEY][0])
    pres = float(post_args[PRESSURE_KEY][0])
    lcur = float(post_args[LOAD_CURRENT_KEY][0])
    batv = float(post_args[BATTERY_VOLTAGE_KEY][0])
    wspeed = float(post_args[WIND_SPEED_KEY][0])
    wdir = float(post_args[WIND_DIR_KEY][0])
    rain = float(post_args[RAIN_FALL_KEY][0])

    cnx = mysql.connector.connect(user=USER_NAME, password=PASSWD,
                                 database=DATABASE_NAME )
    
    cursor = cnx.cursor()
    cursor.execute(INSERT_DEF,(temp,humi,itmp,pres,lcur,batv,wspeed,wdir,rain))
    cnx.commit()
    cursor.close()
    cnx.close()

   
    

def main():
      opts = getopts()
      if opts.create:
          create_table()
      if opts.list:
          list_last_record()
          


if __name__ == "__main__":
    main()
