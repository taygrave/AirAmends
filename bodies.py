import model
import re


s = model.connect()


# Making a list of airport codes for reference (so can remove any regex findings that are not airports)
all_airports = s.query(model.Airport).all()
list_codes = []

for airport in all_airports:
    list_codes.append(airport.id)


#get a list of the email objects
msg_list = s.query(model.Email).all()

airport_code = r"\(([A-Z]{3})\)"

#TODO set variable for confirmation code numbers 
#TODO in initial quickstart, don't return any emails where i am not the passenger, or delete them from here if you can identify which these are

for msg in msg_list:
    result1 = re.findall(airport_code, msg.body_raw)

    print "pre code removal"
    print result1 

    cleaned_list = [item for item in result1 if item in list_codes]

    # for code in result1:
    #     if code not in list_codes:
    #         result1.remove(code)


    print "message id: %d" %msg.id
    print cleaned_list




#ideas on how to narrow search:
    # write out possible combinations (with a smaller sample) and find the pattern to identify distinct flights
    # look at who from (domain matching airline) - or better yet, look at who to, then see if user's name appears elsewhere in the email (like as the ticketed passenger) and if not, may not be their flight
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



