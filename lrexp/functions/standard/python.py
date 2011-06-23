'''
Mainly to interface with builtin python features  
'''
def call( function, *args, **kwargs ):
    """
    Call a function with the specified arguments and keyword arguments.
    
    Use this to access builtin python functions (map, filter, any, all, etc.)
    """
    return function( *args, **kwargs )
