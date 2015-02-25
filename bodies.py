import model
import re

def airport_codes():
    """Returns a list of all airport codes in db"""
    s = model.connect()
    all_airports = s.query(model.Airport).all()
    list_aircodes = []

    for airport in all_airports:
        list_aircodes.append(airport.id)

    return list_aircodes

def query_emails():
    """Connects to db and returns list of all email message objects"""
    s = model.connect()
    msg_list = s.query(model.Email).all()
    return msg_list

#TODO set variable for confirmation code numbers 

def find_airports():
    """Pulls email bodies (strings) from msg objs (list) and parses them to return a list of airport codes per message"""
    #FIXME: This funciton should receive just ONE well-defined input (an email body ready to search)
    list_aircodes = airport_codes()
    msg_list = query_emails()

    aircode_str = r"[\(;>]([A-Z]{3})[\)&<]"
    #tried taking out parenthesis and it was a madhouse, need parenthesis.
    # aircode_str = r"\(([A-Z]{3})"
    # aircode_str = r"\b[A-Z]{3}\b"
    # re1 = (A-Z
    # re2 = >A-Z<
    # re3 = ;A-Z&

    for msg_obj in msg_list:
        list_refinds = re.findall(aircode_str, msg_obj.body)

        #list comprehension to ensure three letter findings are airport codes
        list_airfinds = [item for item in list_refinds if item in list_aircodes]

        # print "*" * 20
        # print "message id: %d" %msg_obj.id
        # print msg_obj.date
        # print msg_obj.sender 
        # print msg_obj.subject
        print list_airfinds


def print_to_file():
    """Queries the database for the body of the messages and prints out content into txt files so we can examine them ourselves """
    #TODO: DELETE this function once you're done!
    msg_list = query_emails()
    for msg in msg_list:
        body = msg.body.encode('utf-8')
        filename = "body/" + str(msg.id) + ".txt"
        f = open(filename, 'w')
        print >> f, body
        f.close

# print_to_file()
find_airports()