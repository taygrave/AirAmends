import httplib2
import base64
import re
from datetime import datetime
import model
import email

from apiclient.discovery import build
from apiclient import errors
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run

GMAIL_SERVICE = None 
print GMAIL_SERVICE

def authorize():
  """Builds the gmail api service so all other requests can be made"""
  #exmaple provided by: https://developers.google.com/gmail/api/quickstart/quickstart-python
  global GMAIL_SERVICE    

  CLIENT_SECRET_FILE = 'client_secret.json' # Path to the client_secret.json file downloaded from the Developer Console
  OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.readonly'
  STORAGE = Storage('gmail.storage') #Location of the current user's credentials storage file

  # Start the OAuth flow to retrieve credentials
  flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=OAUTH_SCOPE, redirect_uri="http://localhost:5000/")
  http = httplib2.Http()

  # Try to retrieve credentials from storage or run the flow to generate them
  credentials = STORAGE.get()
  if credentials is None or credentials.invalid:
    credentials = run(flow, STORAGE, http=http)

  # Authorize the httplib2.Http object with our credentials
  http = credentials.authorize(http)

  # Build the Gmail service from discovery - this is the part that takes very long
  GMAIL_SERVICE = build('gmail', 'v1', http=http)
  print "completed: service build", GMAIL_SERVICE
  return GMAIL_SERVICE

def get_user():
  """Returns the user's email address"""
  my_user = GMAIL_SERVICE.users().getProfile(userId="me").execute()
  email_addy = my_user['emailAddress']
  return email_addy

def query_messages():
  """Returns list of ids of all user's messages matching a query string (using authorized gmail api instance and specific userId / "me")."""
  global GMAIL_SERVICE  
  query = "itinerary, confirmation, flight, number, departure, taxes from:-me subject:-fwd subject:-re subject:-fw subject:-check"
  list_msg_ids = [] #will stay empty if no messages match the query

  try:
    response = GMAIL_SERVICE.users().messages().list(userId="me", q=query).execute()
    
    if 'messages' in response:
      list_msg_ids.extend(response['messages'])
    
    while 'nextPageToken' in response: #this part allows you to get complete results, basically gets EVERYTHING matching query (usually not reached, needs >60 finds)
      page_token = response['nextPageToken']
      response = GMAIL_SERVICE.users().messages().list(userId="me", q=query, pageToken=page_token).execute()
      list_msg_ids.extend(response['messages'])

    print "completed: got query msg list"
    return list_msg_ids
  
  except errors.HttpError, error:
    print 'An error occurred: %s' % error

def get_message(msg_id):
  """Get a Message with given msgID (for a specific user / "me" using authorized gmail api instance) and return it as a decoded string."""
  global GMAIL_SERVICE  
  try:
    message = GMAIL_SERVICE.users().messages().get(userId="me", id=msg_id, format="raw").execute()
    str_raw_msg = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
    return str_raw_msg

  except errors.HttpError, error:
    print 'An error occurred: %s' % error

def add_msgs_to_db():
  """Sets query and adds unique, parsed, and extra decoded if necessary, message components to the db """
  global GMAIL_SERVICE  
  msg_list = query_messages()

  s = model.connect()

  # check if message is unique, parse, perhaps decode, and add to db
  for item in msg_list:
    #only take those where msg_id = thread_id to ensure its the root email
      if item['id'] == item['threadId']: 
        #pull actual message from gmail api using its id
        str_raw_msg = get_message(item['id'])
        
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
          entry = model.Email(user_id=1, msg_id=item['id'], date=msg_date, sender=msg_sender, subject=msg_subject, body=msg_body)
          s.add(entry)
          s.commit()

  print "Successfully added emails to the db"

def convert_date(date_str):
  """Converts email obj date (string) into a datetime date object."""
  p = re.compile(r"[0-9]{1,2}\s[A-Z]{1}?[a-z]{2}\s\d{4}")
  msg_date = p.search(date_str).group()
  converted_date = datetime.strptime(msg_date, "%d %b %Y")
  return converted_date
