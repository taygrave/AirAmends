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
    aircode_str = r"\(([A-Z]{3})\)"

    # #this works for the one jetblue email where airport codes are not in parenthesis, but on nothing else, so maybe not worth it... but noting
    # aircode_str2 = r"\>([A-Z]{3})\<"

    #need another one for parenthesis that look like this: eg. &=2340;SFO&=2341 (JetBlue Flight and SW)


    for msg_obj in msg_list:
        list_refinds = re.findall(aircode_str, msg_obj.body_raw)

        msg = email.message_from_string(msg_obj.body_raw)
        From = msg['From']
        Date = msg['Date']
        Subject = msg['Subject']

        #list comprehension to ensure three letter findings are airport codes
        list_airfinds = [item for item in list_refinds if item in list_aircodes]

        if list_airfinds == []:
            for part in msg.walk():
                msg.get_payload()
                if part.get_content_type() == 'text/html' or part.get_content_type() == 'text/plain':
                    decoded = base64.urlsafe_b64decode(part.get_payload().encode('UTF-8'))
                    list_refinds = re.findall(aircode_str, decoded)

                    list_airfinds = [item for item in list_refinds if item in list_aircodes]

        print "*" * 20
        print "message id: %d" %msg_obj.id
        print From
        print Date 
        print Subject
        print list_airfinds

        #TODO: Break this out into a couple different functions that can be called if and only if the returned list with the easiest thing is empty, then calling alternate functions increasing in complexity only if.


def print_to_file():
    """Queries the database for the body of the messages and prints out content into txt files so we can examine them ourselves """
    msg_list = query_emails()

    fnum = 1

    for msg in msg_list:
        body = msg.body_raw
        filename = "body/" + str(fnum) + ".txt"
        f = open(filename, 'w')
        print >> f, body
        f.close
        fnum = fnum + 1


# print_to_file()
find_airports()