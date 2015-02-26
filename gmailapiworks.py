import httplib2
import base64
import model
import email

from apiclient.discovery import build
from apiclient import errors
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run

#exmaple provided by: https://developers.google.com/gmail/api/quickstart/quickstart-python
CLIENT_SECRET_FILE = 'client_secret.json' # Path to the client_secret.json file downloaded from the Developer Console
OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.readonly'
STORAGE = Storage('gmail.storage') #Location of the current user's credentials storage file

# Start the OAuth flow to retrieve credentials
flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=OAUTH_SCOPE)
http = httplib2.Http()

# Try to retrieve credentials from storage or run the flow to generate them
credentials = STORAGE.get()
if credentials is None or credentials.invalid:
  credentials = run(flow, STORAGE, http=http)

# Authorize the httplib2.Http object with our credentials
http = credentials.authorize(http)

# Build the Gmail service from discovery - this is the part that takes very long
gmail_service = build('gmail', 'v1', http=http)
print "completed: service build"

def query_messages(service, user_id, query):
  """Returns list of ids of all user's messages matching a query string (using authorized gmail api instance and specific userId / "me")."""
  list_msg_ids = [] #will stay empty if no messages match the query

  try:
    response = service.users().messages().list(userId=user_id, q=query).execute()
    
    if 'messages' in response:
      list_msg_ids.extend(response['messages'])
    
    while 'nextPageToken' in response: #this part allows you to get complete results, basically gets EVERYTHING matching query (usually not reached, needs >60 finds)
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
      list_msg_ids.extend(response['messages'])

    print "completed: got query msg list"
    return list_msg_ids
  
  except errors.HttpError, error:
    print 'An error occurred: %s' % error

def get_message(service, user_id, msg_id):
  """Get a Message with given msgID (for a specific user / "me" using authorized gmail api instance) and return it as a decoded string."""
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id, format="raw").execute()
    str_raw_msg = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
    return str_raw_msg

  except errors.HttpError, error:
    print 'An error occurred: %s' % error

def add_msgs_to_db():
  """Sets query and adds unique, parsed, and extra decoded if necessary, message components to the db """

  query1 = "itinerary, confirmation, flight, number, departure, taxes from:-me subject:-fwd subject:-re subject:-fw subject:-check"
  msg_list = query_messages(gmail_service,"me", query1)
  s = model.connect()

  #check if message is unique, parse, perhaps decode, and add to db
  for item in msg_list:
    #only take those where msg_id = thread_id to ensure its the root email
      if item['id'] == item['threadId']: 
        #pull actual message from gmail api using its id
        str_raw_msg = get_message(gmail_service,'me', item['id'])
        msg_body = str_raw_msg
        #and turn it into an email object to begin parsing
        email_msg = email.message_from_string(str_raw_msg)
        msg_date = email_msg['Date']
        msg_sender = email_msg['From']
        msg_subject = email_msg['Subject']
        
        #checks if msg body is still encoded and decodes if necessary
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

