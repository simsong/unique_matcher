#!/usr/bin/env python36

import csv
import operator
from collections import defaultdict


##
## Row management functions.
## Each row is read as a tuple so that it's hashable.
## Not sure if you can do this with pandas or numpy
##
def print_rows(rows,keys=frozenset()):
    from color import color
    print("==== keys: {} count: {} ====".format(strkeys(keys),len(rows)))
    for row in rows:
        print("( ",end="")
        for i in range(0,len(row)):
            if i>0: print(", ",end='')
            if not args.nocolor and i in keys : print(color.BOLD+color.RED,end='')
            print(row[i],end='')
            if not args.nocolor and i in keys: print(color.END,end='')
        print(") ")
    print("\n")


def read_rows(path, delimiter=','):
    rows = []
    with open(path, "r") as f:
        for line in csv.reader(f, delimiter=delimiter):
            rows.append(tuple(line))  # use tuples so they will be hashable
    return rows


##
## Key management functions.
## A "key" is a column number.
## "keys" is a frozenset of several column numbers.
## We use set because the order is irrevellant (better than sorting a list all the time)
## We make it frozen because it is going to be used for hashing.  (A set of sets; sets can only contain hashables)
##
def strkeys(keys):
    """Return a string for a keys frozenset"""
    assert type(keys) == frozenset
    return " ".join([str(x) for x in sorted(keys)])


def choose_all_subkeys(keys):
    "@keys are a frozenset of keys. Return a list of all permutations of n-1 keys "
    assert type(keys) is frozenset

    # Return empty list if length is 1, rather than list of empty sets
    if len(keys)==1:
        return []  
    return [keys-frozenset([key]) for key in keys]


###
### Core function: find_singletons
### Return the rows in @rows that are unique in rows and all_rows
### Only the columns specified by @keys are considered.
### Note: Every element in rows must be in all_rows, but this is never tested, so we only look for unique
### in @rows that are in @all_rows
###

def find_singletons(all_rows,rows,keys):
    """Find and return the singletons at the current level.
    @all_rows is the list of all rows in the original dataset. We always need to prune against that.
    @rows is the list of singletons from the previous level. It's what we are examining.
    @keys are the keys that are considered. With each recursive call, keys will be removed.
    """
    if args.debug:
        print("find_singletons(len(all_rows)={},len(rows)={},keys={}".format(len(all_rows),len(rows),keys))

    # http://stackoverflow.com/questions/18272160/access-multiple-elements-of-list-knowing-their-index
    # Make a function that extracts the key columns and makes a tuple
    # Note: I tried Memoizing this function, and the runtime increased by 5x. 
    kfun = operator.itemgetter(*keys)

    # For every row in rows, extract a tuple of the elements denoted by @keys.
    # Then, using that as the key of the dictionary, add a reference to each row that is identified by those keys.
    # If it is a singleton, there will be just one.
    rows_for_key_tuples = defaultdict(set)
    for row in rows:
        rows_for_key_tuples[kfun(row)].add(row)

    # Note that rows_kfuncs.keys() is a list of all the combinations of keys that we care about!

    # For every row in all_rows, extract the kfun and note all the rows with that kfun
    all_rows_for_key_tuples = defaultdict(set)
    for row in all_rows:
        all_rows_for_key_tuples[kfun(row)].add(row)
        
    def pick(s):
        """Return an element of set s wtihout modifying set s"""
        return next(iter(s))

    def distinct(v):
        """Returns True if v contains a single element"""
        return len(v)==1

    #
    # Now, return an array of ROWS for the ROWS that are distinct in @all_rows.
    # We do this by looping over the combines of indexes (rows_for_key_tuples.keys())
    # and returning the row in rows_for_key_tuples that are distinct in all_worws_for_key_tuples.
    #

    return [ pick(rows_for_key_tuples[kf]) for kf in rows_for_key_tuples if distinct(all_rows_for_key_tuples[kf]) ]



def find_missing_values(rows,keys):
    """Return an array of the rows that have a missing value ("") for any of the keys"""
    # We need to make a kfun that always returns a tuple, even for 1 value
    if len(keys)==1:
        kfun = lambda e : ( e[ next(iter(keys)) ] , )
    else:
        kfun = operator.itemgetter(*keys)
    return [row for row in rows if "" in kfun(row)]




# checked_lists is the lists of sets that we have checked.
# at the beginning, we have checked the empty list.
checked_keys = set()
def check_rows_with_keys(all_rows,rows,keys,alert):
    """@param all_rows --- all of the rows in the original dataset.
    @param rows --- The rows in which we are to look for unique keys.
    @param keys --- The specific keys we are to check.
    @return     --- Returns the number of distinct rows that are found.
    """
    if args.verbose:
        print("check_row_with_keys({},{},{})".format(len(all_rows),len(rows),keys),end='')

    # Note that we have now checked this permutation of keys
    # Must do this at the beginning because of recursive call
    checked_keys.add(keys)

    # Print the unique rows for these keys
    singleton_rows = find_singletons(all_rows,rows,keys)

    missing_value_rows = find_missing_values(rows,keys)
    if missing_value_rows:
        alert("missing_value_rows:",missing_value_rows)

    if singleton_rows + missing_value_rows:
        count = len(singleton_rows)
        if args.verbose:
            print_rows(singleton_rows,keys)

        # Now process all of the sub lists
        for sub_keys in choose_all_subkeys(keys):
            if sub_keys not in checked_keys:
                count += check_rows_with_keys(all_rows,singleton_rows + missing_value_rows,sub_keys, alert)
        return count
    return 0


#
# Run the matcher. 
# Currently, this uses our custom-built tool for reading delimited files.
# Eventually we should move this to parquet & pandas. 

if __name__=="__main__":
    import argparse, resource

    parser = argparse.ArgumentParser(description='Extract specified variables from AHS files.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--infile', type=str, default='test_data.csv', help='file to match')
    parser.add_argument('--delimiter', type=str, default=',', help='specify delimiter')
    parser.add_argument('--debug', action="store_true")
    parser.add_argument('--verbose', action="store_true", help='Print each set')
    parser.add_argument('--printdata',action='store_true',help='Print the initial dataset')
    parser.add_argument('--nocolor', action='store_true', help='Turns off color')
    parser.add_argument('--range', type=str, help="specify range of search",default="1-max")
    args = parser.parse_args()

    rows = read_rows(args.infile,delimiter=args.delimiter)

    if args.printdata or args.verbose:
        print("here is the dataset:")
        print_rows(rows)
    
    (rmin,rmax) = args.range.split("-")
    rmin = int(rmin)
    rmax = len(rows[0]) if rmax=="max" else int(rmax)

    keys = frozenset(range(rmin,rmax))
    print("Keys that we will consider: {}".format(strkeys(keys)))
    count = check_rows_with_keys(rows,rows,keys,print)
    print("Total of all uniques: {}".format(count))
    r = resource.getrusage(resource.RUSAGE_SELF)
    print("User CPU: {}   RSS:{}".format(r.ru_utime,r.ru_maxrss))

