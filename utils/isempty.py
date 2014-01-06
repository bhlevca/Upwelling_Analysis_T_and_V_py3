def isempty(obj):
    '''
    Checks if the object is empty
    '''
    if isinstance(obj, int):
        if obj == 0:
            return True
        else:
            return False
    elif isinstance(obj, list):
        if len(obj) == 0:
            return True
        else:
            return False
