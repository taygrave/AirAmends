import httplib2
import base64
import model
import email
import pdb

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
  """Returns list of ids of all user's messages matching a query.

  Args:
    service: Authorized Gmail API service (instance).
    user_id: User's email address / special value "me" for authenticated user (string).
    query: (string).
  """
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
  """Get a Message with given ID and return it as a decoded string.

  Args:
    service: Authorized Gmail API service (instance).
    user_id: User's email address / special value "me" for authenticated user (string).
    msg_id: ID of the Message to retrieve (string).
  """
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id, format="raw").execute()
    print "completed: retrieved message"

    str_raw_msg = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
    print "completed: decoded message"
    
    return str_raw_msg

  except errors.HttpError, error:
    print 'An error occurred: %s' % error

def add_msgs_to_db():
  #TODO = add docstring
    query1 = "itinerary, confirmation, flight, number, departure, taxes from:-me subject:-fwd subject:-re subject:-fw subject:-check"
    msg_list = query_messages(gmail_service,"me", query1)
    print "completed: query messages"
    s = model.connect()

    for item in msg_list:
        msg_id = item['id']
        msg_thrd_id = item['threadId'] 

        #only take those where msg_id = thread_id to ensure its the root email
        if msg_id == msg_thrd_id:

          str_raw_msg = get_message(gmail_service,'me', msg_id)
          email_msg = email.message_from_string(str_raw_msg)

          msg_date = email_msg['Date']
          msg_sender = email_msg['From']
          msg_subject = email_msg['Subject']
          msg_body = str_raw_msg
          # msg_encoding = email_msg['Content-Transfer-Encoding']
          
          #checks if msg body is still encoded and decodes if necessary (multipart messages don't return a content-transer-encoding)
          for part in email_msg.walk():
            if (part.get_content_type() == 'text/html' or part.get_content_type() == 'text/plain') and part['Content-Transfer-Encoding'] == 'base64':
              decoded_str = base64.urlsafe_b64decode(part.get_payload().encode('UTF-8'))
              msg_body = decoded_str.decode('utf-8')

          #checks if email with same sender & subject is in db already to prevent adding duplicates in case airline sent duplicates
          exists = s.query(model.Email).filter(model.Email.sender == msg_sender, model.Email.subject == msg_subject).first()

          #adds to db if is a unique itinerary confimation
          if exists == None:
            entry = model.Email(user_id=1, msg_id=msg_id, date=msg_date, sender=msg_sender, subject=msg_subject, body=msg_body)
            s.add(entry)
            s.commit() 

    print "Successfully added emails to the db"

add_msgs_to_db()