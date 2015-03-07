import base64
import re
from datetime import datetime
import model
import email
from apiclient import errors

def query_messages(service):
  """Returns list of ids of all user's messages matching a query string (using authorized gmail api instance and specific userId / "me")."""
  query = "itinerary, confirmation, flight, number, departure, taxes from:-me subject:-fwd subject:-re subject:-fw subject:-check"
  list_msg_ids = [] #will stay empty if no messages match the query

  try:
    response = service.users().messages().list(userId="me", q=query).execute()
    
    if 'messages' in response:
      list_msg_ids.extend(response['messages'])
    
    while 'nextPageToken' in response: #this part allows you to get complete results, basically gets EVERYTHING matching query (usually not reached, needs >60 finds)
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId="me", q=query, pageToken=page_token).execute()
      list_msg_ids.extend(response['messages'])

    print "completed: got query msg list"
    return list_msg_ids
  
  except errors.HttpError, error:
    print 'An error occurred: %s' % error

def get_message(service, msg_id):
  """Get a Message with given msgID (for a specific user / "me" using authorized gmail api instance) and return it as a decoded string."""
  try:
    message = service.users().messages().get(userId="me", id=msg_id, format="raw").execute()
    str_raw_msg = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
    return str_raw_msg

  except errors.HttpError, error:
    print 'An error occurred: %s' % error

def add_msgs_to_db(service, user_id):
  """Sets query and adds unique, parsed, and extra decoded if necessary, message components to the db """
  service = service
  msg_list = query_messages(service)

  s = model.connect()

  # check if message is unique, parse, perhaps decode, and add to db
  for item in msg_list:
    #only take those where msg_id = thread_id to ensure its the root email
      if item['id'] == item['threadId']: 
        #pull actual message from gmail api using its id
        str_raw_msg = get_message(service, item['id'])
        
        msg_body = str_raw_msg
        #and turn it into an email object to begin parsing
        email_msg = email.message_from_string(str_raw_msg)
        msg_date = convert_date(email_msg['Date'])
        msg_sender = email_msg['From']
        msg_subject = email_msg['Subject']
        
        # checks if msg body is still encoded and decodes if necessary
        for part in email_msg.walk():
          if (part.get_content_type() == 'text/html' or part.get_content_type() == 'text/plain') and part['Content-Transfer-Encoding'] == 'base64':
            decoded_str = base64.urlsafe_b64decode(part.get_payload().encode('UTF-8'))
            msg_body = decoded_str.decode('UTF-8')

        #ensures only unique itinerary confirmation email message info is added to the db
        exists = s.query(model.Email).filter(model.Email.sender == msg_sender, model.Email.subject == msg_subject).first()
        
        if exists == None:
          entry = model.Email(user_id=user_id, msg_id=item['id'], date=msg_date, sender=msg_sender, subject=msg_subject, body=msg_body)
          s.add(entry)
          s.commit()

  print "Successfully added emails to the db"

def convert_date(date_str):
  """Converts email obj date (string) into a datetime date object."""
  p = re.compile(r"[0-9]{1,2}\s[A-Z]{1}?[a-z]{2}\s\d{4}")
  msg_date = p.search(date_str).group()
  converted_date = datetime.strptime(msg_date, "%d %b %Y")
  return converted_date
