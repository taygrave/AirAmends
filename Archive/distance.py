import model
from geopy.distance import great_circle

### results from web calcs for comparison
#LHR - JFK : (.92), .53, .64, (1.73), .36
#SEA - PDX: (.07), .04 , .04 (.10), .04
#DEN - FLL: (.50), .29, .32, (.86), .23
### results in parens include rf

## EPA dict was the winner



def calc_carbon((depart, arrive)):
    s = model.connect()

    d_airport = s.query(model.Airport).filter_by(id = depart).one()
    a_airport = s.query(model.Airport).filter_by(id = arrive).one()

    depart_city = (d_airport.latitude, d_airport.longitude)
    arrive_city = (a_airport.latitude, a_airport.longitude)

    #calculate Some use only the great circle distance (the shortest distance between two points on the globe) between two airports.
    #could add an extra amount to end since an aircrafts route is normally not an exact great circle due to flight path routing, detours around weather and delays due to traffic
    distance = great_circle(depart_city, arrive_city).kilometers

    #next need to calc fuel burn - some calcs us fuel burn rates by distance buckets since shorter distances have a greater proportion of their time in high burn activities like takeoff and landing than long distance flights

    #kgs to metric tons
    mt = 0.001
    # DEFRA's recommended Radiative Forcing factor
    rf = 1.9
    #DEFRA/IPCC uplift factor to account for take-off, circling, non-direct routes =
    uf = 1.09
    #km to mils
    mls = 0.621371

    print int(distance), "kms"
    print int(distance * mls), "miles"

    # 1
    # http://www.firmgreen.com/faq_calculate.htm - kg CO2 per mile from the GHG Protocol Mobile Combustion Tool
    flight_dict = {
        (0.00, 727.45) : 0.2897, #Short-haul flight
        (727.46, 2575.04) : 0.2028, #Medium-haul flight
        (2575.05, 15000.00) : 0.1770 } #Long-haul flights

    for low, high in flight_dict.keys():
        if (distance*mls) > low and (distance*mls) < high:
            em_per_pass = flight_dict[(low, high)]

    CO2 = (distance*mls) * em_per_pass * mt * uf * rf

    # 2
    ##http://www.epa.gov/climateleadership/documents/resources/commute_travel_product.pdf
    flight_dict2 = {
        #keys are tupes of lower and higher bound miles traveled
        #values are CO2 Emissions factors in kg CO2 / passenger-mile
        (0.00, 300.00) : 0.277, #Short-haul flight
        (301.00, 700.00) : 0.229, #Medium-haul flight
        (700.00, 15000.00) : 0.185} #Long-haul flights


    for low, high in flight_dict2.keys():
        if (distance*mls) > low and (distance*mls) < high:
            em_per_pass2 = flight_dict2[(low, high)]

    CO2E = (distance*mls) * (em_per_pass2 + 0.0104 * 0.021 + 0.0085 * 0.310) * mt * uf * rf

    #3
    #http://www.carbonplanet.com/downloads/Flight_Calculator_Information_v9.2.pdf
    flight_dict3 = {
        #keys are tupes of lower and higher bound KILOMETERS traveled
        #values are CO2 Emissions factors in kg CO2E/passenger-km
        (0.00, 400.00) : 0.26, #Turboprop flight
        (401.00, 1000.00) : 0.36, #Short-haul flight
        (1001.00, 3700.00) : 0.20, #Medium-haul flight
        (3701.00, 30000.00) : 0.23} #Long-haul flights


    for low, high in flight_dict3.keys():
        if distance > low and distance < high:
            em_per_pass3 = flight_dict3[(low, high)]

    CO23 = distance * em_per_pass3 * mt * uf

    return (CO2, CO2E, CO23)

#for testing diff length hauls
pairs = [("LHR", "JFK"), ("SEA", "PDX"), ("DEN", "FLL")]

def CO2_results(list_pairs):
    
    for pair in list_pairs:
        results = calc_carbon(pair)

        print "RESULTS FOR %s --> %s" %(pair[0], pair[1])

        print "FirmGreen: ", results[0]
        #2
        print "EPA: ", results[1]
        #3
        print "carbonplanet: ", results[2]
        print "*" * 20


CO2_results(pairs)
