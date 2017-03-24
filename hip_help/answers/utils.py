import json



def open_answers():
    with open('answers_in_rooms.json') as data_file:
        data = json.load(data_file)
    return data

