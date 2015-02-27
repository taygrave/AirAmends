import model
import re
from geopy.distance import great_circle

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

def find_itinerary(list_airfinds):
    """Takes list of all legit airport codes found in a message and returns a likely itinirary list of tuples that represent legs of a trip."""
    #HARDFIX: this ignores last items of any odd itemed list, which works for United emails containing notes about an unrelated airports - but may not give you the results you are looking for if a non-airport code slips into anywhere but the last position of the list_airfinds
    list_tupes = zip(list_airfinds[0::2], list_airfinds[1::2])
    list_itin = []

    for item in list_tupes:
        if item not in list_itin:
            list_itin.append(item)

    return list_itin

def find_andseed_airports():
    """Pulls email bodies (strings) from msg objs (list) and parses them to determine a trip itneraries per message and adds each itinerary's flight legs to the db."""
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
        # print CO2_results(itinerary)
        
        #now to begin adding to the db!
        user_id = msg_obj.user_id
        trip_id = msg_obj.id
        date = msg_obj.date #currently the date of the email, not the flight 

        for tupe in itinerary:
            depart, arrive = tupe
            entry = model.Flight(user_id=user_id, trip_id=trip_id, date=date, depart=depart, arrive=arrive)
            s.add(entry)
    s.commit()
    return s.query(model.Flight).all()

def calc_carbon((depart, arrive)):
    s = model.connect()
    d_airport = s.query(model.Airport).filter_by(id = depart).one()
    a_airport = s.query(model.Airport).filter_by(id = arrive).one()

    depart_city = (d_airport.latitude, d_airport.longitude)
    arrive_city = (a_airport.latitude, a_airport.longitude)

    #Conversion and Other Factors 
    mt = 0.001 #kgs to metric tons
    rf = 1.9 # DEFRA's recommended Radiative Forcing factor
    uf = 1.09 #IPCC uplift factor

    #calculate Some use only the great circle distance (the shortest distance between two points on the globe) between two airports * accounting for take-off, circling, non-direct routes
    distance = great_circle(depart_city, arrive_city).miles * uf

    ##EF & CO2E equation below source: http://www.epa.gov/climateleadership/documents/resources/commute_travel_product.pdf
    flight_dict = {
        #keys are tupes of lower and higher bound miles traveled
        #values are CO2 Emissions factors in kg CO2 / passenger-mile
        (0.00, 300.00) : 0.277, #Short-haul flight
        (301.00, 700.00) : 0.229, #Medium-haul flight
        (700.00, 15000.00) : 0.185} #Long-haul flights

    for low, high in flight_dict.keys():
        if distance > low and distance < high:
            em_per_pass = flight_dict[(low, high)]

    #Emissions of CO2E using distance, emissions factors by haul as provided by source (comment above dict) convertered into metric tons and with a radiative forcing applied
    CO2e = distance * (em_per_pass + 0.0104 * 0.021 + 0.0085 * 0.310) * mt * rf

    return CO2e

def CO2_results(list_pairs):

    for pair in list_pairs:
        results = calc_carbon(pair)

        print "RESULTS FOR %s --> %s" %(pair[0], pair[1])
        print "EPA: %.2f" % results
        print "*" * 20














