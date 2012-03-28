# -*- coding: utf8 -*-
# ONLY USED FOR "my format" of CSV. see "strokedistance.csv" for a sample.

import csv
import sys

def main():
    if len(sys.argv) != 2:
        print "Usage:", sys.argv[0], "filename"
        return

    filename = sys.argv[1]
    ifile  = open(filename, "rb")
    reader = csv.reader(ifile)
    colskip = 0
    datarow = 0
    headhash = {}
    heads = {}
    data = {}
    for row in reader:
        # Save header row.
        if len(heads) == 0:
            if not "#" in row[0]:
                skip = 1
                headidx = 0
                for col in row:
                    if skip == 1:
                        colskip = colskip + 1
                        if col == "###":
                            skip = 0
                    else:
                        heads[headidx] = col
                        headhash[col] = headidx
                        headidx = headidx + 1
                print heads

        else:
            x = data[datarow] = {}
            colnum = 0
            for col in row:
                if colnum >= colskip:
                    x[colnum-colskip] = int(col)
                colnum = colnum + 1
            datarow = datarow + 1
    ifile.close()
    datalist = []
    for i in xrange(datarow):
        for j in xrange(len(heads)):
            datalist.append(data[i][j])

    print datalist
    print "len is %d" % len(datalist)
    print headhash
if __name__ == "__main__":
    main()
