# Database module for GardenLab server/database
# Intended to be imported from the server script but can also be run to
# perform some database utilities such as creating the database.
# Run "GardenLab.py -c" to create the database


import argparse
from pydblite.sqlite import Database,Table

DATABASE_FILE="gardenlab.sqlite"
TABLE_NAME="data"

TEMPERATURE_KEY = 'TEMP'
HUMIDITY_KEY = 'HUMI'
INTERNAL_TEMP_KEY = 'ITMP'
PRESSURE_KEY = 'PRES'
LOAD_CURRENT_KEY = 'LCUR'
BATTERY_VOLTAGE_KEY = 'BATV'

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
    

def create_database():
    """
    Create the database and define the fields
    """
    db = Database(DATABASE_FILE)
    table = db.create(TABLE_NAME, ('date','BLOB DEFAULT CURRENT_DATE'),
                      ('time','BLOB DEFAULT CURRENT_TIME'),
                      ('temperature','REAL'),
                      ('humidity','REAL'),
                      ('inside_temp','REAL'),
                      ('pressure','REAL'),
                      ('load_current','REAL'),
                      ('battery_voltage','REAL'))
    db.commit()
                      
                      
def open_database():
    """
    Open the database and return the table file
    """
    db = Database(DATABASE_FILE)
    table = db[TABLE_NAME]
    table.is_date('date')
    table.is_time('time')
    return table


def list_last_record():
    """
    List the last record added to the DB
    """
    table = open_database()
    r = table()
    print r[-1]


def insert_data_from_dict( table, post_args ):
    """
    Insert values into DB table from the args dictionary
    """

    temp = float(post_args[TEMPERATURE_KEY][0])
    humi = float(post_args[HUMIDITY_KEY][0])
    itmp = float(post_args[INTERNAL_TEMP_KEY][0])
    pres = float(post_args[PRESSURE_KEY][0])
    lcur = float(post_args[LOAD_CURRENT_KEY][0])
    batv = float(post_args[BATTERY_VOLTAGE_KEY][0])
    
    table.insert(temperature=temp, humidity=humi,
                 inside_temp=itmp, pressure=pres,
                 load_current=lcur, battery_voltage=batv )
    table.commit()
    

def main():
      opts = getopts()
      if opts.create:
          create_database()
      if opts.list:
          list_last_record()
          


if __name__ == "__main__":
    main()
