import string

def recognize_entities(question):
    '''
    Method for recognizing entities

    NOTE:
        for simulating, add entities as capital letters

    Args:
        question: the question inputted by a user

    TODO:
        embed trained NER model
    '''
    words = question.split()
    entities = []

    for word in words:
        clean_word = word.strip(string.punctuation)
        if clean_word.isupper():
            pascal_word = clean_word.capitalize()
            entities.append(pascal_word)
    
    return entities