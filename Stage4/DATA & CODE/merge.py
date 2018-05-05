import csv

# write to a redirected output

with open('Matched.csv', 'r') as csvfile:
    line = csv.reader(csvfile, delimiter=',')
    for row in line:
        if row[-1] == '1':  # if it is a match
            print(','.join(row[3:8]))   # keep columns 3-8, which only keeps A
            
            
