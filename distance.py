import model
from geopy.distance import great_circle

depart = "PDX"
arrive = "DEN"

s = model.connect()

d_airport = s.query(model.Airport).filter_by(id = depart).one()
a_airport = s.query(model.Airport).filter_by(id = arrive).one()

depart_city = (d_airport.latitude, d_airport.longitude)
arrive_city = (a_airport.latitude, a_airport.longitude)

#calculate Some use only the great circle distance (the shortest distance between two points on the globe) between two airports.
#could add an extra amount to end since an aircrafts route is normally not an exact great circle due to flight path routing, detours around weather and delays due to traffic
distance = great_circle(depart_city, arrive_city).miles

#next need to calc fuel burn - some calcs us fuel burn rates by distance buckets since shorter distances have a greater proportion of their time in high burn activities like takeoff and landing than long distance flights

#lbs to kilgrams
kg = 0.453592
#lbs to metric tons
mt = 0.00045359237
# DEFRA's recommended Radiative Forcing factor
rf = 1.9


#distance must be greater than distance value to qualify for key
# http://www.firmgreen.com/faq_calculate.htm
flight_dict = {
    (0.00, 727.45) : 0.6386784139, #Short-haul flight
    (727.46, 2575.04) : 0.447096936, #Medium-haul flight
    (2575.05, 15000.00) : 0.390217739} #Long-haul flights

CO2 = distance * em_per_pass * kg

##http://www.epa.gov/climateleadership/documents/resources/commute_travel_product.pdf
# flight_dict = {
#     #keys are tupes of lower and higher bound miles traveled
#     #values are CO2 Emissions factors in kg CO2 / passenger-mile
#     (0.00, 300.00) : 0.277, #Short-haul flight
#     (301.00, 700.00) : 0.229, #Medium-haul flight
#     (700.00, 15000.00) : 0.185} #Long-haul flights

print distance

for low, high in flight_dict.keys():
    if distance > low and distance < high:
        em_per_pass = flight_dict[(low, high)]

CO2E = distance * (em_per_pass + 0.0104 * 0.021 + 0.0085 * 0.310) * cv1



print CO2E

