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
            index[intent][condition] = response 

    print(index)
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

def build_header_response(response):
    '''
    Builds JSON format for headers (in bold)

    args:
        response: built response from response template and querying
    
    Returns:
        data: JSON format of a header
    '''
    data = {
        "type": "header",
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

def build_bulleted_response(responses):
    '''
    Builds the JSON format of a bulleted response

    args:
        response: array containing the responses to be placed in bullet form
    '''

    data = {
        "type" : "bulleted",
        "bullets": responses
    }
    return data

def build_bullet (main_text="", description=""):
    '''
    Build the JSON format of a bullet

    args:
        main_text: main text/point of a bullet usually in bold
        description: details for expounding main text of the bullet
    '''
    data = {
        "type" : "bullet",
        "main_text" : main_text,
        "description" : description,
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

    # Checking of payload
    with open('debug_payload.json', 'w') as file:
        json.dump(data, file, indent=4)

    return data         

def build_reference(id, title, url):
    '''
    Builds JSON format of a single reference

    args:
        id: refers to the id of the reference
        title: refers to the title of the reference
        url: refers to the exact url reference was retrieved from
    
    Return:
        data: built JSON format of a reference
    '''
    data = {
        "type": "reference",
        "id": id,
        "title": title,
        "url":url
    }
    return data

def build_reference_list(references):
    '''
    Builds JSON format of a reference list

    args:
        references: refers to the list of references
    
    Returns:
        data: built JSON format of a reference list
    '''
    data = {
        "type": "reference_list",
        "sources": references
    }

    return data
    