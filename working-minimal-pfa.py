import numpy as np
import matplotlib.pyplot as plt

from astropy.io.votable import parse
from astropy.io import ascii
from astropy.time import Time

import timeit

# Take MJD 54192 as the beginning of the transit (BoT):
BoT_mjd = 54192

# Path of this file
folder = 'C:/Users/Jemandes/Documents/Dropbox/J1407_eigen/Paper/github/mentel-et-al-2018/'# provide the directory of this file

# For the actual period folding, we will take the beginning of the 2007 transit as the beginning of the phase
# Thus, the beginning of the first window, BoT_mjd, is taken as the phase phi = 0

# First, define beginning and end of the three windows corresponding to the three major dimming events
# These params has been deduced from the SuperWASP-data on the 2007 transit (see Mamajek et. al., 2012)
t0 = 0 # First Dimming: 0-4 days since beginning of transit
t1 = 4 

t2 = 12 # Big, central Dimming: 12-42 days
t3 = 42

t4 = 48 # Third Dimming: 48-52 days
t5 = 52

# The heart of the PFA
# "counting_points" takes the data as "Light" and a test period "Period"
#  and, after folding "Light" into the period "Period, gives out the number of observations
#  that are laocated in any of the three windows
# Input: Light is array with data: col 0 = MJD of observation, col 1 = free
def counting_points(Light, Period):
    for i, Entry in enumerate(Light): # For every observation ...
        Light[i,1] = np.remainder(Entry[0]-(BoT_mjd), Period*365.25) # Calc phase...

    Count = sum(1 for j in Light if (t0<j[1]<t1) | (t2<j[1]<t3) | (t4<j[1]<t5)) # Calc Number of obs' in any of the threee windows
    return (Count) # return the number of observations in those windows

### Read in data
# PFA only works when column "0" = MJD, column "1" should be free

# For demonstrative purposes, we only use the AAVSO data

file = folder + 'photometry/SuperWASP/1SWASP_J140747.93-394542.6_lc.txt' # Place the data file here
body = open(file, 'r').readlines()[22:] # Skip header
lc_A = np.zeros((len(body), 2))

# Make lightcurve of AAVSO
for (i, entry) in enumerate(body):
    words = entry.split()
    t = Time(float(words[0]), format='jd', scale='utc')
    lc_A[i,0] = t.mjd

print ("Data from AAVSO : " + str(len(lc_A)))

### Actual Period Search
# Warning: This will take some time depending on "s" and length of data!
# With the entire photometry on J1407 and 10k steps per year, runtime is about 11.5 hours

start_time = timeit.default_timer() # For calc runtime
p0 = 300.      # Start period
del_p = 15000.  # tested range

# Step size in decimal years. Uncomment desired
#s = 0.01     # 0.1k steps per year (fastest)
s = 10.   # 10k steps (most precise)

# Calc number of observations in the original transit,
#  since the PFA also counts the observations of the transit on 2007.
# Not really necessary with only plate or AAVSO data

# "source" is the used lightcurve
source = lc_A
count_transit = counting_points(source, 2000*365.24)
#print (original) # For Sanity Check

# Define array for result of PF
#  col "0" = test period, col "1" = counted number of ob's in windows
num_of_obs = np.zeros((del_p/s,2))

# Run actual PFA
for i in range(int(del_p/s)):
    # For all test periods ...
    p = p0 + s*i
    num_of_obs[i,0] = p
    # ... Calc number of ob's in any of these three windows minus transit ob's:
    num_of_obs[i,1] = counting_points(source, p) - count_transit

runtime = timeit.default_timer() - start_time
print("Runtime of PFA:  %s seconds " % (runtime))

# "possible" is list with all the possible periods,
#  i.e. all test periods where not a single observation is present in any of the three windows
possible = num_of_obs[num_of_obs[:,1]<1.][:,0]
# print (possible)

### For Documentation:
# Print "possible" and expected time of next transit

file_name = "new_periods.txt"
file = open(folder + file_name, 'w')
file.write('Possible periods | Expected beginning of next transit' + '\n')
for period in possible:
    ingress = Time(period + BoT_decyear, format='decimalyear', scale='utc').decimalyear
    file.write(str(period) + ', ' + str(ingress) + '\n')

### Plot the results
# For probability histogram
plt.hist(possible, bins=[365.25*x for x in range(15)], normed=1)
plt.xlabel("Orbital Period [Year]")
plt.ylabel("Probability of possible periods per year")
plt.show()
plt.close()