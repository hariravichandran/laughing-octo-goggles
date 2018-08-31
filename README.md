# Program Design

## O(n) Run-time and O(n) Storage
In order to match the actual values with the predicted values, a dictionary was created to store both the actual and predicted values. This dictionary can be created in linear time, and searched in linear time.
The order of complexity of the program is O(N), and the order of storage requirement is O(N). 

## Program Flow
The program reads input files and checks for valid values to create cumulative count and totals. 
The absolute deviations of the predicted values from the actual values are calculated and stored for every hour in two dictionaries. This avoids recalculation of the values across time windows. 

## Input Validation
Input lines that contain empty values and invalid values are dropped. 

## Program Output
The program writes the average error over time periods. It also provides informational messages on dropped input lines and number of lines processed. Optional logging can be enabled to debug the program as needed using the 'loglevel' variable. The program can be further enhanced using Python's 'logging' module.