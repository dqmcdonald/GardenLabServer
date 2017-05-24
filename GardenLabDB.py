# Database module for GardenLab server/database
# Intended to be imported from the server script but can also be run to
# perform some database utilities such as creating the database.
# Run "GardenLab.py -c" to create the database


import argparse
from pydblite.sqlite import Database,Table

DATABASE_FILE="gardenlab.db"


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

    opts = parser.parse_args()
    return opts
    

def createDatabase():
    print "Create DB"



def main():
      opts = getopts()
      if opts.create:
          createDatabase()


if __name__ == "__main__":
    main()
