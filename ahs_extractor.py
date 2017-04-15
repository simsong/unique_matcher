#!/usr/bin/env python3m
#
# read the AHS files and output a signle new file with the specified variables.
# Replace all unknowns with "None"
# Creates both a JSON and a CSV file (In the future, a parquet file)

import csv
import json
import os
from collections import defaultdict

from orderedset import OrderedSet

DB='AHS 2013 National PUF v1.2 CSV'

ID='CONTROL'
ID_VARS= OrderedSet("REGION,DIVISION,SMSA,METRO3,NUNIT2,TENURE,WGT90GEO".split(","))
AHS_MISSING = frozenset(["-6","-7","-8","-9",""])
LINK_VARS="BSINK,TOILET,USELECT,FPLWK,GARAGE,INCP,AIRSYS,WFUEL,SEWDIS,WATER,TERM,UNITSF,BEDRMS,VALUE,AMMORT,AMMRT2,YRMOR,LPRICE,AMTX,ROOMS,BUILT"

def read_firstline(path):
    """Return the first line of a file."""
    with open(path,"rU") as f:
        for line in f:
            return line.rstrip()
        

def get_link_var_files(link_vars):
    """Read each file and return dictionary  of each identifier and the file it is in"""
    ret = {}
    for fname in os.listdir(DB):
        if fname.endswith(".csv"): 
            path = os.path.join(DB,fname)
            firstline = read_firstline(path)
            for field in firstline.split(","):
                if field in link_vars:
                    if field in ret:
                        print("{} is in both {} and {}".format(field,ret[field],path))
                        exit(-1)
                    ret[field] = path
    return ret
                

def ahs_clean(var):
    """Clean up the data according to AHS key"""
    if var[0] == var[-1] == "'":
        var = var[1:-1]
    return var if var not in AHS_MISSING else None


if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Extract specified variables from AHS files.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--outname', type=str, default='ahs_output', help='basename of output files')

    parser.add_argument('--link_vars', type=str, default=LINK_VARS, help="variables to link on")

    args = parser.parse_args()

    link_vars      = OrderedSet(args.link_vars.split(","))
    link_var_files = get_link_var_files(link_vars)

    if not link_var_files:
        print("No link_var_files found")
        exit(1)

    # Find the fields that have each variable we want
    file_vars = defaultdict(set)
    for var in link_vars:
        file_vars[link_var_files[var]].add(var)

    # Now build the dataset of the IDs and the files we want
    # Strip single quotes
    # ids[id][variable] = value
    ids = defaultdict(dict)
    for fname in file_vars:
        print("File: {}  reading: {}".format(fname,",".join(file_vars[fname])))
        count = 0
        with open(fname,"rU") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                for var in file_vars[fname]:
                    id = ahs_clean(row[ID])
                    ids[row[ID]][var] = ahs_clean(row[var])
                count += 1
            print("Read {} rows\n".format(count))

    # build the row with the titles
    row = [ID] + list(link_vars)

    rows = [row]
    # Now build the rows
        
    for id in ids:
        if id[0] == id[-1] == "'":
            pid = id[1:-1]
        else:
            pid = id
        row = [pid] + [ids[id].get(v, None) for v in link_vars]
        rows.append(row)

    # write the results
    with open(args.outname + ".csv","w") as out:
        writer = csv.writer(out)
        writer.writerows(rows)

    # write the json
    with open(args.outname + ".json","w") as out:
        json.dump(rows,out,separators=(',', ':'))
            
            
    
