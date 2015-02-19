import model
import re
from bs4 import BeautifulSoup


s = model.connect()


#get a list of the email objects
msg_list = s.query(model.Email).all()

airport_code = r"\(([A-Z]+)\)"
from_field = r'From:[\w]' #\<([\w]+)\>'

for msg in msg_list:
    result1 = re.findall(airport_code, msg.body_raw)
    result2 = re.findall(from_field, msg.body_raw)
    print "message id: %d" %msg.id
    print result1
    print result2



#ideas on how to narrow search:
    # write out possible combinations (with a smaller sample) and find the pattern to identify distinct flights
    # look at who from (domain matching airline) - or better yet, look at who to, then see if user's name appears elsewhere in the email (like as the ticketed passenger) and if not, may not be their flight
    # make sure airport code exists in the world and isn't a time zone abbrv
    # ideal: find flight date

#next steps - figure out the flight path from just the airport codes



# # this is to print out the bodies into txt files so we can examine them ourselves
# fnum = 1

# for msg in msg_list:
#     body = msg.body_raw
#     filename = "body/" + str(fnum) + ".txt"
#     f = open(filename, 'w')
#     print >> f, body
#     f.close
#     fnum = fnum + 1


# this was for back when i was only looking at southwest airlines and getting half of the flight info
# for msg in msg_list:
#     body = msg.body
#     soup = BeautifulSoup(body)
#     #import incase this is not your itinerary
#     passenger = soup.find('name')
#     date = soup.find('traveldate')
#     depart = soup.find('depart')
#     arrive = soup.find('arrive')

#     print msg.id, passenger, date, depart, arrive
#     print '*' * 10

