-- Import crawled end dates from csv
LOAD DATA INFILE '../output/output-end.csv' 
INTO TABLE end_corrected
FIELDS TERMINATED BY ','
IGNORE 1 LINES;

-- Import crawled start dates from csv
LOAD DATA INFILE '../output/output-start.csv' 
INTO TABLE end_corrected
FIELDS TERMINATED BY ','
IGNORE 1 LINES;