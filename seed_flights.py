import model
import re
from datetime import datetime

def print_to_file():
    """Queries the database for the body of the messages and prints out content into txt files so we can examine them ourselves """
    #TODO: DELETE this function once you're done!
    s = model.connect()
    msg_list = s.query(model.Email).all()

    for msg in msg_list:
        body = msg.body.encode('utf-8')
        filename = "body/" + str(msg.id) + ".txt"
        f = open(filename, 'w')
        print >> f, body
        f.close

def find_airports():
    """Pulls email bodies (strings) from msg objs (list) and parses them to return a list of airport codes per message"""
    s = model.connect()
    all_airports = s.query(model.Airport).all()
    list_aircodes = [airport.id for airport in all_airports]

    p = re.compile(r"\(([A-Z]{3})(\)| )|\>([A-Z]{3})\<|;([A-Z]{3})\&")

    msg_list = s.query(model.Email).all()
    for msg_obj in msg_list:
        list_results = p.findall(msg_obj.body)
        list_refinds = []

        for tupe3 in list_results:
            str_match = [m for m in tupe3 if m != '']
            list_refinds.extend(str_match)

        # list comprehension to ensure three letter findings are airport codes
        list_airfinds = [m for m in list_refinds if m in list_aircodes]

        #final list of tuples representing legs of single trip per message
        itinerary = find_itinerary(list_airfinds)
        
        #now to begin adding to the db!

        user_id = msg_obj.user_id
        trip_id = msg_obj.id
        date = msg_obj.date #currently the date of the email, not the flight 

        for tupe in itinerary:
            depart, arrive = tupe
            entry = model.Flight(user_id=user_id, trip_id=trip_id, date=date, depart=depart, arrive=arrive)
            s.add(entry)

    s.commit()


def find_itinerary(list_airfinds):
    """Takes list of all legit airport codes found in a message and returns a likely itinirary list of tuples that represent legs of a trip."""
    #HARDFIX: this ignores last items of any odd itemed list, which works for United emails containing notes about an unrelated airports - but may not give you the results you are looking for if a non-airport code slips into anywhere but the last position of the list_airfinds
    list_tupes = zip(list_airfinds[0::2], list_airfinds[1::2])
    list_itin = []

    for item in list_tupes:
        if item not in list_itin:
            list_itin.append(item)

    return list_itin



# print_to_file()
find_airports()
