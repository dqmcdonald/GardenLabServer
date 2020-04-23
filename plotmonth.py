#
# Plot temperature,humidity,pressure for a specified month over all years
#
# Call as "python3 plotmonth.py <Month>"
#
# Plots are created in directory monthlyplots/
#

import sys
import mysql.connector
import time
import statistics

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, FormatStrFormatter
from matplotlib.dates import DayLocator, DateFormatter
import datetime
import math


DATABASE_NAME="GardenLab"
TABLE_NAME="GardenLabData"

COLORS = [ "#05d005","#d05050","#0505d0","#d0d005","#d0d0d0","#00f000" ]

# Read the password and username from an external file:
pd= open("/home/pi/GardenLabServer/private.data").read().strip()
pd = pd.split(" ")
USER_NAME=pd[0]
PASSWD=pd[1]




def generate_month_plot( month_name, dates, data , data_name, ylabel):
	"""
	Generate a plot which shows a comparison plot for each year
	"""

	min_year = int(min(dates.keys()))


	fig,ax = plt.subplots(figsize=cm2inch(24,12))

	for year in dates.keys():
		col_index = year % min_year
		# normalise all dates to the same year
		mod_dates = []
		for d in dates[year]:
			new_d = d.replace(year=min_year)
			mod_dates.append(new_d)


		median = statistics.median(data[year])
		mean = statistics.mean(data[year])
		sd = statistics.stdev(data[year])
		

		ax.plot_date(mod_dates,data[year],"-",
		 label='{} median={:03.1f} {}={:03.1f} {}= {:3.1f}'
			.format(year,median, r'$\mu$',mean, r'$\sigma$',sd),
			color=COLORS[col_index],lw=1.0)

	days = DayLocator()
	days_fmt = DateFormatter("%d")
	ax.xaxis.set_major_locator(days)
	ax.xaxis.set_major_formatter(days_fmt)
	ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))

	for tick in ax.xaxis.get_major_ticks():
		tick.label.set_fontsize(4)

	for tick in ax.yaxis.get_major_ticks():
		tick.label.set_fontsize(4)

	ax.autoscale_view()

	ax.set_xlabel("Day")
	ax.set_ylabel(ylabel)

	plt.show()

	plt.title("{} Data for {}".format(data_name, month_name))
	plt.legend(loc='best', prop={'size': 6})	
	fig.savefig("monthlyplots/{0}_{1}.png".format(
        	month_name,data_name), dpi=150)


	plt.close()



def fetch_data( month ):
	"""
	Get data for for the specified month. Returns a tuple of dicts,
	each indexed by years and containing dates,temps,pressure,humidity
	"""

	temps = {}
	pressure = {}
	humidity = {}
	dates = {}

	cnx = mysql.connector.connect(user=USER_NAME, password=PASSWD,
                                 database=DATABASE_NAME )

	cursor = cnx.cursor()

	query = ("""
		select ts, temperature,pressure,humidity from 
			GardenLabData where monthname(dt) 
		= '{}'""".format(month))
	cursor.execute(query)
	for(rec) in cursor:
		year = rec[0].year
		if year not in dates:
			dates[year] = []
			temps[year] = []
			pressure[year] = []
			humidity[year] = []
		dates[year].append(rec[0])
		temps[year].append(rec[1])
		pressure[year].append(rec[2])
		humidity[year].append(rec[3])
	
		
	return (dates,temps, pressure, humidity)

def cm2inch(*tupl):
    inch = 2.54
    if isinstance(tupl[0], tuple):
        return tuple(i/inch for i in tupl[0])
    else:
        return tuple(i/inch for i in tupl)



def main():
	if len(sys.argv) < 2 :
		print("Specify month name")	
		sys.exit(-1)

	(dates,temps,pressure,humidity) = fetch_data(sys.argv[1])
	generate_month_plot( sys.argv[1], dates, temps, "Temperature",
	 "Temperature ($^\circ$C)")
	generate_month_plot( sys.argv[1], dates, humidity, "Humidity",
	 "Humidity (%)")
	generate_month_plot( sys.argv[1], dates, pressure, "Pressure",
	 "Pressure (hPa)")


if __name__ == "__main__":
	main()

