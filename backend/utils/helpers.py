import re

def to_camel_case(text):
    # Split on spaces/whitespace and capitalize each word, then join without spaces
    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return text.capitalize()
    return ''.join(word.capitalize() for word in words)

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

def is_name_match(user_string, db_string):
    """
    Checks if all words in the user's input exist in the database string,
    ignoring case and parentheses.
    """
    clean_db_string = db_string.lower().replace("(", " ").replace(")", " ").replace("_", " ")
    
    user_words = set(user_string.lower().split())
    db_words = set(clean_db_string.split())
    
    return user_words.issubset(db_words)

def split_commas(sentence):
    string = sentence[0]  # → "headache, dizziness, tiredness"
    return [s.strip() for s in string.split(',') if s.strip()]

def unwrap(value, default="Not specified"):
    """Returns first element if non-empty list, otherwise returns value or default."""
    if isinstance(value, list):
        return value[0] if len(value) > 0 else default
    return value if value else default

def sort_side_effects(side_effects):
    pattern_priority = {
        "serious": 1,

        "common": 2,
        "fairly frequent": 2,
        "dose-related": 2,

        "less common": 3,
        "occasional": 3,
        "uncommon": 3,

        "infrequent": 4,
        "rare": 4,

        "very rare": 5,

        "not specified": 6,
        None: 6
    }

    return sorted(
        side_effects,
        key=lambda se: (
            pattern_priority.get(
                str(se.get("pattern", "")).strip().lower(),
                6
            ),
            se.get("side_effect", "").lower()
        )
    )