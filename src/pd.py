# -*- coding: utf-8 -*-
"""

@author: Ravichandran
"""

# Benchmark various ways of reading a csv file
# Code works in Python2 and Python3
 
import sys, time, os, csv, timeit

try:
    import unicodecsv
except: 
    unicodecsv = None
try:
    import pandas
except:
    pandas = None
 
#fn = sys.argv[1]
fn =  './insight_testsuite/tests/test_1/input/actual.txt'
s = time.time()
 
df = pandas.read_csv(fn, encoding='utf-8', sep='|', header=None,)
df.columns = ['time','stock','price']
df.dropna 
min_time = df['time'].iloc[0]
last_row = df.shape[0]
max_time = df['time'].iloc[last_row-1]
e = time.time()
t = e - s



print('%.2fs %s' % (t, 'pandasCsv'))