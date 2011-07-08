'''
Mathematical operations
'''
def summation( *summands ):
    """
    Sums the arguments
    """
    return sum( summands )

def subtract( plus, minus ):
    """
    Subtract the second argument from the first
    """
    return plus - minus

def multiply( *factors ):
    """
    Multiplies the arguments together
    """
    return reduce( lambda x, y: x * y, factors )

def divXY( x, y ):
    """
    Divides the first argument by the second, returns the result
    """
    return x / y

def average( *terms ):
    """
    Averages the arguments
    """
    return sum( terms ) / float( len( terms ) )

def absValue( number ):
    """
    Returns the absolute value
    """
    return abs( number )

