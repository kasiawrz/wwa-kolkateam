import json
from faker import Faker

fake = Faker()

answers_to_fake = dict()

for i in range(0, 500):
    key = 'room ' + str(i)
    room_values = []
    for p in range(0, 100):

        keyss = fake.name()
        vals = fake.paragraph(nb_sentences=3, variable_nb_sentences=True)
        room_values.append({"keyword": keyss, "text": vals})
    answers_to_fake[key] = room_values


with open('answers_in_rooms.json', 'w') as fp:
    json.dump(answers_to_fake, fp)