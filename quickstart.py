import httplib2
import pdb
import inspect
import base64
import model

from apiclient.discovery import build
from apiclient import errors
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run

#exmaple provided by: https://developers.google.com/gmail/api/quickstart/quickstart-python

# Path to the client_secret.json file downloaded from the Developer Console
CLIENT_SECRET_FILE = 'client_secret.json'

# Check https://developers.google.com/gmail/api/auth/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.readonly'

# Location of the credentials storage file
STORAGE = Storage('gmail.storage')

# Start the OAuth flow to retrieve credentials
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
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

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
    msg_string = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

    return msg_string

  except errors.HttpError, error:
    print 'An error occurred: %s' % error

def add_msgs_to_db():
    #added 'southwest' to query to start with managable list of results
    query1 = "itinerary, confirmation, flight, number, departure, taxes, southwest"
    msg_list = query_messages(gmail_service,"me", query1)
    s = model.connect()

    for i in range(len(msg_list)):
        msg_id = msg_list[i]['id']
        msg_thrd_id = msg_list[i]['threadId'] #often same as msg_id, may not need, uncertain
        msg_str = get_message(gmail_service,'me', msg_id)

        # add to db the id and the text
        #FIXME: actually add the current user to the Users table (w/ all info) and input user_id as actual user_id
        entry = model.Email(user_id=1, msg_id=msg_id, thread_id=msg_thrd_id, body=msg_str)
        s.add(entry)

    s.commit() 

    print "Successfully added emails to the db"

