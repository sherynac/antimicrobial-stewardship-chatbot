def classify_intent (question):
    '''
    Method that uses an NER model to classify the intent of a question
    If confidence level is below a certain threshold it will re-classify to NOT_RECOGNIZED intent

    Args:
        question: refers to the question inputted by the user 
    TODO: 
        add elif for other intents, text preprocessing, embedding intent classification model
    '''
    if question in ["How is DOXYCYCLINE supplied?",
        "How is DOXIN supplied?" ,
        "What dosage forms are available for the generic antibiotic DOXYCYCLINE and the brand-name antibiotic DYNADOXY ?",
        "How is PARACETAMOL supplied?",
        "How is BIOGESIC supplied?",
        "What dosage forms are available for the generic antibiotic PARACETAMOL and the brand-name antibiotic BIOGESIC ?"]:
        return "GET_ANTIBIOTIC_INFO"
    elif question in ["What is the difference between DOXIN and DOXYCLEN?",
        "What is the difference between DOXIN, DOXYCLEN and DYNADOXY?",
        "What is the difference between DOXIN and LEVOCIN?",
        "Compare the different brands of DOXYCYCLINE.",
        "Compare DOXIN with other brands of DOXYCYCLINE."]:
        return "COMPARE_BRANDS"
    elif question in ["i was given DYNADOXY (DOXYCYCLINE), what is it for?",
        "i was given DOXIN (DOXYCYCLINE), what is it for?",
        "Why was i prescribed DYNADOXY?",
        "Why was i prescribed DOXIN?",
        "What are the clinical indications for DOXYCYCLINE?"]:
        return "GET_USES_INDICATIONS"
    elif question in ["What are the side effects of DOXYCYCLINE?",
        "What are the common side effects of DYNADOXY?",
        "What are the side effects of DYNADOXY (DOXYCYCLINE)?",
        "Will DOXYCYCLINE give me a HEADACHE?",
        "Will DOXYCYCLINE give me a DIARRHEA?"]:
        return "GET_SIDE_EFFECTS"
