import model
import re


s = model.connect()


#get a list of the email objects
msg_list = s.query(model.Email).all()

airport_code = r"\(([A-Z]{3})\)"

#set variable for confirmation code numbers 

for msg in msg_list:
    result1 = re.findall(airport_code, msg.body_raw)

    print "message id: %d" %msg.id
    print result1




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



