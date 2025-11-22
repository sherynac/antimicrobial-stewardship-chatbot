def analyze_query(text):
    """
    TODO: Load NLP model here later.
    For now, just return dummy data.
    """
    # Placeholder logic
    print(f"Skeleton NLP received: {text}")
    
    return {
        "intent": "general_query",
        "entities": [text] # Just pretend the whole text is the entity
    }