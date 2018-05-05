import csv

# write to a redirected output

isbn = []

with open('TableE.csv', 'r') as csvfile:
    line = csv.reader(csvfile, delimiter=',')
    for row in line:
        if row[2] in isbn:
            continue
        print(','.join(row))
        isbn.append(row[2])

