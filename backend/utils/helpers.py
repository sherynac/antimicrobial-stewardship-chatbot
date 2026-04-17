def array_to_string (array):
    '''
    Method for transforming an array to a string
    [hotdog, rocket, phone] = hotdog, rocket and phone

    args:
        array: refers to the array to be transformed to a string
    
    Returns:
        result: string format of passed array making use of ',' and "and" 
    '''
    result = ""
    for i, element in enumerate(array):
        result += add_space_to_pascal_case(element.name)
        
        if i == len(array) - 1:
            pass
        elif i == len(array) - 2:
            result += " and "
        else:
            result += ", "

    return result

def is_yes_or_no (boolean):
    '''
    Method for transforming boolean to a "Yes" or "No" string

    args:
        boolean: boolean to be transformed to string

    '''
    if boolean:
        return "Yes"
    return "No"

def add_space_to_pascal_case (string):
    '''
    Adds spaces for words written in Pascal case

    args:
        string: string that is in Pascal case
    '''
    result = []

    for i, char in enumerate(string):
        if char.isupper() and i>0:
            result.append(' ')
        result.append(char)
    return ''.join(result)
