def classify_intent (question):
    '''
    Method that uses an NER model to classify the intent of a question
    If confidence level is below a certain threshold it will re-classify to NOT_RECOGNIZED intent

    Args:
        question: refers to the question inputted by the user 
    TODO: 
        add elif for other intents, text preprocessing, embedding intent classification model
    '''
    if ("How is DOXYCYCLINE supplied?" 
        or "How is DOXIN supplied?" 
        or "What dosage forms are available for the generic antibiotic DOXYCYCLINE and the brand-name antibiotic DYNADOXY ?"):
        return "GET_ANTIBIOTIC_INFO"
    elif ("hotdog"):
        return "COMPARE_BRANDS"
    elif ("hotdog2"):
        return "GET_USES_INDICATIONS"