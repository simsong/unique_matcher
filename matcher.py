from collections import defaultdict
import csv

def print_rows(rows,keys):
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

def find_singletons(rows,keys):
    "@data is list of rows. Return all for which the 'keys' elements are unique"
    # http://stackoverflow.com/questions/18272160/access-multiple-elements-of-list-knowing-their-index
    import operator
    from collections import Counter

    # extract all of the keys from the rows 
    data_keys   = [operator.itemgetter(*keys)(row) for row in rows]

    # Find those that are unique
    unique_keys = [key_count[0] for key_count in Counter(data_keys).most_common() if key_count[1]==1]
    
    # Return the rows that have their keys in unique_keys
    return [row for row in rows if (operator.itemgetter(*keys)(row) in unique_keys)]


# checked_lists is the lists of sets that we have checked.
# at the beginning, we have checked the empty list.
checked_keys = set()
def check_keys(keys,rows):
    # Note that we have now checked this permutation of keys
    # Must do this at the beginning because of recursive call
    checked_keys.add(keys)

    # Print the unique rows for these keys
    singleton_rows = find_singletons(rows,keys)
    if rows:
        print_rows(singleton_rows,keys)

        # Now process all of the sub lists
        for sub_keys in choose_all_subkeys(keys):
            if sub_keys not in checked_keys:
                check_keys(sub_keys,singleton_rows)

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
    check_keys(keys,rows)
