import os
import httplib2
import oauth2client
from apiclient import discovery
from oauth2client import client
from oauth2client import tools


def getCredentials(scopes):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,'admin-directory_v1-python-quickstart.json')
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, scopes)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def initializeService(scopes):
    credentials = getCredentials(scopes)
    http = credentials.authorize(httplib2.Http())
    return discovery.build('admin', 'directory_v1', http=http)

