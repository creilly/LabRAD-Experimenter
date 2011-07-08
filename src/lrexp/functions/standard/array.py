'''
Array operations.
'''
def index( collection, beginning, end = None ):
    """
    Gets a subset of a collection.  Gets a single index if end is None or not specified.
    """
    return collection[beginning] if end is None else collection[beginning:end]

def copyAppend( collection, toAppend ):
    """
    Appends the second argument to a copy of the first and returns the appended list.
    This uses a shallow copy operation.
    """
    copy = list( collection )
    copy.append( toAppend )
    return copy

def group( *arguments ):
    """
    Creates a list of the arguments
    """
    return list( arguments )

def append( collection, toAppend ):
    """
    Appends an item toAppend to collection
    """
    collection.append( toAppend )

def clearList( collection ):
    """
    Empty a list
    """
    while collection:
        collection.pop()

def extend( toExtend, extendedBy ):
    """
    Extend a list by another list
    """
    toExtend.extend( extendedBy )

def summation( *summands ):
    """
    Performs successive addition operations on each element in the list.
    Elements can be strings, lists, numbers, or anything with defined behavior for the '+' operator.
    Returns the element if only one element and zero for no elements.
    """
    if len( summands ) < 2:
        return summands[0] if len( summands ) else 0
    return reduce( lambda x, y: x + y, summands )
