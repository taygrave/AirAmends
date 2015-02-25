import model
import re

def find_airports():
    """Pulls email bodies (strings) from msg objs (list) and parses them to return a list of airport codes per message"""
    s = model.connect()
    all_airports = s.query(model.Airport).all()
    list_aircodes = [airport.id for airport in all_airports]

#>>> # r"(a|b|c)"
    aircode_str = r"[\(;>]([A-Z]{3})[\)&<]"

    # aircode_str = r"(SFO|DEN)"  
    # aircode_str = r"\(([A-Z]{3}) | \>([A-Z]{3})\<"
    # |;([A-Z]{3})\&"
    # aircode_str = r"\>([A-Z]{3})\<"
    # p = re.compile(r"\(([A-Z]{3}) | \>([A-Z]{3})\<")
    # p = re.compile(r"((SFO)?|(JFK)?)")
    #tried taking out parenthesis and it was a madhouse, need parenthesis.
    # aircode_str = r"\(([A-Z]{3})"
    # re1 = (A-Z
    # re2 = >A-Z<
    # re3 = ;A-Z&
    
    msg_list = s.query(model.Email).all()
    for msg_obj in msg_list:
        list_refinds = p.findall(msg_obj.body)

        #list comprehension to ensure three letter findings are airport codes
        list_airfinds = [item for item in list_refinds if item in list_aircodes]

        # print "*" * 20
        # print "message id: %d" %msg_obj.id
        # print msg_obj.date
        # print msg_obj.sender 
        # print msg_obj.subject
        print len(list_airfinds), ":", list_airfinds


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

# print_to_file()
find_airports()
