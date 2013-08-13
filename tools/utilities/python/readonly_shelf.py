import shelve

def open(filename, writeback=True):
    return DbfilenameReadonlyShelf(filename, writeback=writeback)
    

class DbfilenameReadonlyShelf(shelve.Shelf):
    """
    Shelf implementation using the "anydbm" generic dbm interface,
    read only.  Gets rid of annoying error message on shutdown when it
    tries to write back.
    """
    
    def __init__(self, filename, writeback):
 	import anydbm
 	shelve.Shelf.__init__(self, anydbm.open(filename, flag='r'), protocol=2, writeback=writeback)

    def __del__(self):
        self.dict.close()
    

    
        
        
