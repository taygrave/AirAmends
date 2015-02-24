import httplib2
import base64
import model
import email

from apiclient.discovery import build
from apiclient import errors
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run

#FIXME: clean this UP! 
#FIXME: this process takes so long, way to speed it up? 

#exmaple provided by: https://developers.google.com/gmail/api/quickstart/quickstart-python

# Path to the client_secret.json file downloaded from the Developer Console
CLIENT_SECRET_FILE = 'client_secret.json'

# Check https://developers.google.com/gmail/api/auth/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.readonly'

# Location of the current user's credentials storage file
# change this to keep in same place as the client_secret_file??
STORAGE = Storage('gmail.storage')

# Start the OAuth flow to retrieve credentials
# flow is likely an object 
flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=OAUTH_SCOPE)
http = httplib2.Http()

# Try to retrieve credentials from storage or run the flow to generate them
credentials = STORAGE.get()
if credentials is None or credentials.invalid:
  credentials = run(flow, STORAGE, http=http)

# Authorize the httplib2.Http object with our credentials
http = credentials.authorize(http)

# Build the Gmail service from discovery
gmail_service = build('gmail', 'v1', http=http)

def query_messages(service, user_id, query=''):
  """List all Messages of the user's mailbox matching the query.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    query: String used to filter messages returned.

  Returns:
    List of Messages that match the criteria of the query. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate ID to get the details of a Message.
  """
  try:
    response = service.users().messages().list(userId=user_id,
                                               q=query).execute()
    #TODO: rename variables accordingly
    messages = []

    #TODO Handle if there are no messages matching the query (somewhere) or just put in doc string
    if 'messages' in response:
      messages.extend(response['messages'])

    #this part allows you to get complete results, basically gets EVERYTHING matching query
    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id, q=query,
                                         pageToken=page_token).execute()
      messages.extend(response['messages'])

    return messages
  except errors.HttpError, error:
    print 'An error occurred: %s' % error

def get_message(service, user_id, msg_id):
  """Get a Message with given ID.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A Message, decoded.
  """
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id, format="raw").execute()

    #FIXME: United emails aren't being decoded for some reason
    str_raw_msg = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

    return str_raw_msg

  except errors.HttpError, error:
    print 'An error occurred: %s' % error

def add_msgs_to_db():

    query1 = "itinerary, confirmation, flight, number, departure, taxes from:-me subject:-fwd subject:-re subject:-fw subject:-check"
    msg_list = query_messages(gmail_service,"me", query1)
    s = model.connect()

    for item in msg_list:
        msg_id = item['id']
        #only take those where msg_id = thread_id to ensure its the root email
        msg_thrd_id = item['threadId'] 
        msg_str1 = get_message(gmail_service,'me', msg_id)

        # add to db the id and the text
        #FIXME: actually add the current user to the Users table (w/ all info) and input user_id as actual user_id
        entry = model.Email(user_id=1, msg_id=msg_id, thread_id=msg_thrd_id, body_raw=msg_str1, body_full=("notworking currenlty, but I think it returns the same thing anyway"))


        s.add(entry)

        s.commit() 

    print "Successfully added emails to the db"

# add_msgs_to_db()