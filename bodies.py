import model
import re
import base64
import email

def airport_codes():
    """Returns a list of all airport codes in db"""
    s = model.connect()
    all_airports = s.query(model.Airport).all()
    list_aircodes = []

    for airport in all_airports:
        list_aircodes.append(airport.id)

    return list_aircodes

#TODO set variable for confirmation code numbers 

def query_emails():
    """Connects to db and returns list of all email message objects"""
    s = model.connect()
    msg_list = s.query(model.Email).all()
    return msg_list

def find_airports():
    """Pulls email bodies (strings) from msg objs (list) and parses them to return a list of airport codes per message"""
    list_aircodes = airport_codes()
    msg_list = query_emails()
    #tried taking out parenthesis and it was a madhouse, need parenthesis.
    # aircode_str = r"\(([A-Z]{3})"

    aircode_str = r"[\(;>]([A-Z]{3})[\)&<]"

    # re1 = (A-Z
    # re2 = >A-Z<
    # re3 = ;A-Z&


    for msg_obj in msg_list:
        list_refinds = re.findall(aircode_str, msg_obj.body)

        #list comprehension to ensure three letter findings are airport codes
        list_airfinds = [item for item in list_refinds if item in list_aircodes]

        if list_airfinds == []:
            decoded_str = extra_decode(msg_obj)
            #could put a test or something here? is it possible that decoded_str could be None?
            list_refinds = re.findall(aircode_str, decoded_str)
            list_airfinds = [item for item in list_refinds if item in list_aircodes]
            
            # #re-writes the body files so that the coded illegible ones are replaced with decoded body
            # filename = "body/" + str(msg_obj.id) + ".txt"
            # f = open(filename, 'w')
            # print >> f, decoded_str
            # f.close   

        # print "*" * 20
        # print "message id: %d" %msg_obj.id
        # print msg_obj.date
        # print msg_obj.sender 
        # print msg_obj.subject
        print list_airfinds


def extra_decode(msg_obj):
    """Decodes message bodies from a message object from the database that is still encrypted and returns decoded string of body"""
    msg = email.message_from_string(msg_obj.body)
    for part in msg.walk():
        msg.get_payload()
        if part.get_content_type() == 'text/html' or part.get_content_type() == 'text/plain':
                decoded_str = base64.urlsafe_b64decode(part.get_payload().encode('UTF-8'))
                return decoded_str

def print_to_file():
    """Queries the database for the body of the messages and prints out content into txt files so we can examine them ourselves """
    msg_list = query_emails()

    for msg in msg_list:
        body = msg.body
        filename = "body/" + str(msg.id) + ".txt"
        f = open(filename, 'w')
        print >> f, body
        f.close



# print_to_file()
find_airports()