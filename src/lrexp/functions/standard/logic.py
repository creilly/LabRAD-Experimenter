'''
Logical operations
'''
def ifThenElse( condition, ifTrue, ifFalse ):
    return ifTrue if condition else ifFalse

def greaterThan( x, y ):
    return x > y

def negate( toNegate ):
    return not toNegate

def orAll( *arguments ):
    return any( arguments )

def andAll( *arguments ):
    return all( arguments )
