## Import all the packages
import sys, csv, datetime
#import argparse
#import pandas as pd
#import numpy as np
#import logging
#import os
# TO-DO Implement logging standard outpout for systemd
#logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
#log = logging.getLogger("my-logger")
#log.info("Hello, world")

# set up Decimal with high precision
import decimal
from decimal import *

getcontext().prec = 28 
# Set the precision.
#getcontext().prec = 3

## Read Input Parameters
test = 2
if test == 0:
    wfile = sys.argv[1] 
    infile_actual = sys.argv[2]
    infile_pred = sys.argv[3]
    outfile = sys.argv[4]
# python3 ./src/prediction-validation.py ./input/window.txt ./input/actual.txt ./input/predicted.txt ./output/comparison.txt

if test == 1: 
    wfile = './input/window.txt'
    infile_actual = './input/actual.txt'
    infile_pred = './input/predicted.txt' 
    outfile = './output/comparison.txt'
if test == 2:
    wfile = './insight_testsuite/tests/test_1/input/window.txt'
    infile_actual = './insight_testsuite/tests/test_1/input/actual.txt'
    infile_pred = './insight_testsuite/tests/test_1/input/predicted.txt' 
    outfile = './insight_testsuite/tests/test_1/output/comparison.txt'

# test_NA_invalid  
if test == 3:
    wfile =         './insight_testsuite/tests/test_NA_invalid/input/window.txt'
    infile_actual = './insight_testsuite/tests/test_NA_invalid/input/actual.txt'
    infile_pred =  './insight_testsuite/tests/test_NA_invalid/input/predicted.txt' 
    outfile =      './insight_testsuite/tests/test_NA_invalid/output/comparison.txt' 
# 'loglevel' controls output for debugging purposes
loglevel = 0  #sys.argv[4]

if loglevel >= 1: print(sys.argv)

valid_records = 0
rows_written = 0

## Create Dictionaries

#Input
actual_tsp = {} #Time & Stock -> Price
pred_tsp = {}  #Time & Stock -> Count

#Output
count_actual_pred = {}
total_actual_pred = {}
average_error = {} #Begin + End Hour -> Average Error

## Track Performance
now = datetime.datetime.now()
start_time = now
if loglevel >= 0: print('Begin Time: %s' % (start_time))

def printf(format, *args):
    sys.stdout.write(format % args)

# Read Window Value
with open(wfile, 'rb') as window_file:
    first_line = window_file.readline()
    try:
        window = int(first_line)
        if window < 1:
            print('Error: Window value should be a positive integer, input value is: %s' % (window))
            sys.exit()
    except ValueError:
        print('Error: Window value should be a positive integer, input value is: %s' % (first_line))
        sys.exit()

if loglevel >= 1: print('window: %d' % (window) )

def validate(time, stock, price, infile, line_num):
    drop = False  
    #Drop Invalid Records
    invalid_column = ''
    invalid_reason = ''
    time = time.strip()
    stock = stock.strip()
    price  = price.strip()
    if len(time) == 0:
        drop, invalid_column, invalid_reason = True, 'time', 'time is empty'
    elif len(stock) == 0:
        drop, invalid_column, invalid_reason = True, 'stock', 'Stock symbol is empty'
    elif len(price) == 0:
        drop, invalid_column, invalid_reason = True, 'price', 'Stock price is empty'
    else:
        try:
            timeInt = int(time) # timeInt is not used, used for validateion, need  as string for concatenated key
            good_time = True
        except ValueError:
            good_time = False
        
        if good_time == False:
            drop, invalid_column, invalid_reason = True, 'time', 'Time  is not integer'  
 
        try:
            priceFloat = float(price)  # priceFloat is not used, later converted to cents
            good_price = True
        except ValueError:
            good_price = False
            
        if good_price == False:
            drop, invalid_column, invalid_reason = True, 'price', 'Price is not a decimal'  
        
#    if invalid_column_count.has_key(invalid_column): #Create a dictionary
#        invalid_column_count[invalid_column] += 1
#    else:
#        invalid_column_count[invalid_column] = 1
    
    if drop == True:
        print("Dropped line " + str(line_num)  + " from " + infile + " due to invalid " +  invalid_column + ": " + invalid_reason)
        print("     Input line values: " + time + "|" + stock + "|" + price)
    
    return drop, time, stock, price  # return trimmed validated values of time, stock and price



def read_tsp_file(infile, tsp):
    column_names = ['TIME', 'STOCK', 'PRICE']
    min_read = False
    with open(infile, 'r') as input_file:
        reader = csv.DictReader(input_file, delimiter = '|', fieldnames = column_names)
        try:
            for row in reader:
                time = row['TIME']
                stock = row['STOCK']
                price = row['PRICE']
                if time is None or stock is None or price is None: 
                    print("Dropped line " + str(reader.line_num) +  " due to missing values")
                    continue
                if loglevel >= 1: print('Time %s, Stock %s, Price %s' % (time, stock, price))
                drop, time, stock, price = validate(time,stock,price,infile, reader.line_num)
                if drop == False:
                    priceDollar, priceCents = price.split('.')
                    priceInCents = int(priceDollar) * 100 + int(priceCents)
     
                    time_stock = time + ' ' + stock
                    #tsp[time_stock] = Decimal(price)
                    tsp[time_stock] = priceInCents
                    if min_read == False: # Set Minimum Time from First Line
                        min_time = int(time)
                        min_read = True
    
            max_time = int(time)  # time is sorted in ascending order in input
        except csv.Error as err:
            print('Filename: %s , Line Number: %d, Error: %s' % (infile, reader.line_num, err))
        else:
            print('Filename: %s , Lines Processed: %d' % (infile, reader.line_num))
    return min_time, max_time

def find_error(actual, predicted):
    for key in actual:
        t,s = key.split(' ')
        if loglevel >= 1: print('Key: %s, %s' % (t,s))
        if t not in count_actual_pred: count_actual_pred[t] = 0
        if t not in total_actual_pred: total_actual_pred[t] = int(0)
        if key in predicted:
            diff = abs(actual[key] - predicted[key])
            count_actual_pred[t] += 1
            total_actual_pred[t] += diff

def write_average_error():
    rows_written = 0
    with open(outfile, 'w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter = '|')
        
        if loglevel >= 1: print('\nCalculating Average Error:')
        if loglevel >= 1: print('window: %d' % (window) )
        low = min_actual_time
        high = max_actual_time
        wm1 = window - 1 
    
        if loglevel>= 1: print('low: %d high: %d' % (low, high) )
        for i in range(low, high - wm1 + 1):
            #cum_count = Decimal(0.0)
            #cum_total = Decimal(0.0)
            cum_count = int(0)
            cum_total = int(0)
            j = i + wm1
            if loglevel>= 1: print('i: %i, j: %i' % (i, j))  
            if loglevel>= 1: print(' Find average for time periods:')
            for k in range (i, j+1): 
                if loglevel>= 1: print(k)
                strK = str(k)
                # chedk if any actual stock prices exist for period k
                if strK in count_actual_pred:  
                    if strK in count_actual_pred:
                        cum_count += count_actual_pred[strK]
                    #else:
                    #    count_actual_pred[strK] = 0 
                    if strK in total_actual_pred:
                        cum_total += total_actual_pred[strK]
                    #else:
                    #    total_actual_pred[strK] = 0 
            if cum_count == 0:
                avg = 'NA'
            else:
                #avgDecimal = Decimal(cum_total/cum_count)
                #avg = '{0:.2f}'.format(avgDecimal)
                avgDecimal = Decimal(cum_total/cum_count)
                avgDecimalinDollars = avgDecimal/100 
                avgRound = round(avgDecimalinDollars, 2)
                avg = str(avgRound)
                #avg = '{0:.2f}'.format(avgRound)
            if loglevel>= 1: print('%i|%d|%s' % (i, j, avg))
            writer.writerow([i,j,avg])
            rows_written += 1
    if loglevel>= 0: print('Rows written: %i' % (rows_written))
                    

min_actual_time, max_actual_time = read_tsp_file(infile_actual, actual_tsp)
if loglevel >= 1: print(actual_tsp)
if loglevel >= 1: print('Max Actual Time: %i' % max_actual_time)

min_pred_time, max_pred_time = read_tsp_file(infile_pred, pred_tsp)
if loglevel >= 1: print(pred_tsp)
if loglevel >= 1: print('Max Predicted Time: %i' % max_pred_time)

find_error(actual_tsp, pred_tsp)
if loglevel >= 1: print(count_actual_pred)
if loglevel >= 1: print(total_actual_pred)

write_average_error()

end_time = datetime.datetime.now()
if loglevel >= 0: print('End Time: %s' % (end_time))

elapsed_time = end_time - start_time
if loglevel >= 0: print('Elapsed Time: %s' % (elapsed_time))
