import csv

        

def get_rows_from_csv(source):
    """ An atlas is an array whose elements each represent a row in the query of data.
        Each row is a dictionary, and all dictionary keys match each other.
        Essentially this is not unlike a SQL resultset.
        """
    i = 0
    j = 1
    atlas = {}
    for i,row in enumerate(csv.reader(source)):
        if not row:
            continue
        if i == 0:
            keys = row
        else:        
            atlas[i] = {}
            j = 0
            for key in keys:
                try:
                    atlas[i][key] = row[j]
                except:
                    pass
                j += 1
    return atlas