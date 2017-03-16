from collections import defaultdict
import csv

total_count = 0

def print_rows(rows,keys):
    global total_count
    total_count += len(rows)
    print("==== keys: {} count: {} ====".format(" ".join([str(x) for x in sorted(keys)]),len(rows)))
    for row in rows:
        print(row)
    print("\n")

def choose_all_subkeys(keys):
    "@keys are a frozenset of keys. Return a list of all permutations of n-1 keys "
    assert type(keys) is frozenset
    return [keys-frozenset([key]) for key in keys]


def elements_for_keys(row,keys):
    "Return the elements in row[] indicated by keys"
    import operator
    operator.itemgetter(row,keys)

def find_singletons(all_rows,rows,keys):
    """@data is list of rows. Return all for which the 'keys' elements are unique.
    @keys are the keys that are considered.
    """

    if not keys: return []      # 

    # http://stackoverflow.com/questions/18272160/access-multiple-elements-of-list-knowing-their-index
    import operator
    from collections import Counter

    # Make a function that extracts the key columns and makes a tuple
    print("keys={}".format(keys))
    kfun = operator.itemgetter(*keys)

    # extract all of the keys from the rows that were passed in 
    data_keys   = [kfun(row) for row in rows]

    # Find those that are unique
    unique_keys = [key_count[0] for key_count in Counter(data_keys).most_common() if key_count[1]==1]
    
    # Get the rows that have their keys in unique_keys
    ret = [row for row in rows if (kfun(row) in unique_keys)]

    # Argh! We need to scan against all_rows to see if each ret matches an existing 
    # one with the same keys, but which has a different ID
    def purge(candidate):
        for row in all_rows:
            if ((candidate[0] != row[0]) and 
                kfun(candidate) == kfun(row)):
                print("Purge {}".format(candidate))
                return True
        return False

    # return ret
    # Now filter out those that should be purged
    return [row for row in ret if not purge(row)]


# checked_lists is the lists of sets that we have checked.
# at the beginning, we have checked the empty list.
checked_keys = set()
def checks_rows_with_keys(all_rows,rows,keys):
    # Note that we have now checked this permutation of keys
    # Must do this at the beginning because of recursive call
    print("check_row_with_keys({},{},{})".format(len(all_rows),len(rows),keys))

    checked_keys.add(keys)

    # Print the unique rows for these keys
    singleton_rows = find_singletons(all_rows,rows,keys)
    if rows:
        print_rows(singleton_rows,keys)

        # Now process all of the sub lists
        for sub_keys in choose_all_subkeys(keys):
            if sub_keys not in checked_keys:
                checks_rows_with_keys(all_rows,singleton_rows,sub_keys)

if __name__=="__main__":
    rows = []
    with open("data.tsv","r") as f:
        for line in csv.reader(f,delimiter=' '):
            rows.append(tuple(line)) # use tuples so they will be hashable
    print("here is the dataset:")
    for row in rows:
        print(row)
    
    keys = frozenset(range(1,len(rows[0])))
    print("Keys that we will consider: {}".format(keys))

    print("Here are the uniques for each set of keys:")
    checks_rows_with_keys(rows,rows,keys)
    print("Total of all uniques {}".format(total_count))
