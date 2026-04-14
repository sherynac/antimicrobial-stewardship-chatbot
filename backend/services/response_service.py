import json
import os

def build_response_index():
    '''
    Reads JSON vetted response bank and builds a nested dictionary for retrieving responses/templates
    With nested dictionary (similar to multi-dimensional array) but makes use of string keys
    
    Sample: 
        ["GET_ANTIBIOTIC_INFO"]["generic_only"]= "this is the response for getting antibiotic info with generic only"
    
    Returns:
        index: nested dictionary for response templates
    '''

    with open('./backend/data/vetted_response.json', 'r') as file:
        response_bank = json.load(file)
        print("Loaded JSON vetted response bank")

    index = {}

    for intent_obj in response_bank["IntentDefinitions"]:
        intent = intent_obj["intent"]

        index[intent] = {}

        for response in intent_obj["responses"]:
            condition = response["condition"]
            index[intent][condition] = response["responseText"]

    return index

def get_response_template(intent, condition, response_index):
    '''
    Retrieves corresponding response template given intent and condition

    args:
        intent: classified intent
        condition: depends on recognized entities from initial question
        response_index: loaded nested dictionary

    Returns:
        response template based on the intent and condition
    '''
    return response_index.get(intent, {}).get(condition)

def build_text_response(response):
    '''
    Builds JSON format for plain text responses

    args:
        response: built response from response template and querying
    
    Returns:
        data: JSON format of a plain text response
    '''
    data = {
        "type": "text",
        "response": response
    }
    return data


def build_table_response(columns, rows):
    '''
    Builds JSON format for table responses 

    args:
        columns: column headers
        rows: refers to the data to be displayed in a row
    
    Returns:
        data: JSON format of a table response
    '''
    data = {
        "type" : "table",
        "columns": columns,
        "rows": rows
    }
    return data

def build_composite_response(responses):
    '''
    Builds composite response (combination of response types)

    args:
        responses: array of built responses which have different types 
    
    Returns:
        data: built JSON format from combining different response types
    '''
    data = {
        "type" : "composite",
        "responses": responses
    }
    return data         
