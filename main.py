# encoding=utf8
from __future__ import print_function
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import httplib2
import os
import datetime
import transliterate
import md5
import re
import string

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
import argparse

MOSCOW='mos'
DOMAIN=os.environ['GOOGLE_DOMAIN']
# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/admin-directory_v1-python-quickstart.json
PASS_SALT = os.environ['GOOGLE_PASS_SALT']
SCOPES = ['https://www.googleapis.com/auth/admin.directory.group', 'https://www.googleapis.com/auth/admin.directory.user']
CLIENT_SECRET_FILE = '~/.google-sdk/client_secret.json'
APPLICATION_NAME = 'Directory API Python Quickstart'
DOMAIN_GROUPS={
    u'all': u'03q5sasy2czjgc1',
    u'changes': u'03dy6vkm2gil8vq',
    u'exchange': u'030j0zll2uylwyv',
    u'idk': u'030j0zll0iuxg1g',
    u'it-weekly-plans': u'00z337ya2zhacva',
    u'middle_math': u'03bj1y383ychcp0',
    u'middle_math_plans': u'02w5ecyt14klej3',
    u'mos': u'03cqmetx21004ob',
    u'pedagogy': u'00haapch48horjf',
    u'release': u'030j0zll202atf5',
    u'sch': u'04iylrwe28poeg8',
    u'schools': u'00rjefff106axpy',
    u'sys': u'01opuj5n16j6lhr',
    u'ul': u'02250f4o2una4y6'
}
parser = argparse.ArgumentParser(description='Creates user in uchi.ru domain, add him to specified groups.')
parser.add_argument('user_names', metavar='NAME1 NAME2', type=str, nargs='+', help='Usernames to create, in format: "Name Surname", will be transliterated and email will be automaticly made from translit')
parser.add_argument('--groups', dest='groups', default=['all', 'changes', 'exchange'], metavar='GROUP1 GROUP2', type=str, nargs='+', help='Groups')
parser.add_argument('--office', dest='office', default=MOSCOW, type=str, help='Office the new worker will work, default Moscow')

args = parser.parse_args()

def get_credentials(scopes):
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
    credentials = get_credentials(scopes)
    http = credentials.authorize(httplib2.Http())
    return discovery.build('admin', 'directory_v1', http=http)

def translitirate(string):
    text = unicode(string, 'utf-8')
    regex = r"[^\w\s]"
    pat = re.compile( regex )
    return pat.sub('', transliterate.translit(text, reversed=True))

def getUsers(service):
    print('Getting the first 10 users in the domain')
    results = service.users().list(customer='my_customer', maxResults=10, orderBy='email').execute()

    users = results.get('users', [])

    if not users:
        print('No users in the domain.')
    else:
        print('Users:')
        for user in users:
            print('{0} ({1})'.format(user['primaryEmail'],
                user['name']['fullName']))

def createdUser(service, userParams):
    result = service.users().insert(body=userParams).execute()
    return result

def createMembership(service, groupKey, email):
    result = service.members().insert(groupKey=groupKey, body={ 'email': email, "role": "MEMBER"  }).execute()
    return result

def generatePass(string):
    m = md5.new()
    m.update(string + PASS_SALT)
    return m.hexdigest()

def generateDomainEmail(name, surname):
    return "{0}.{1}@{2}".format(name.lower(), surname.lower(), DOMAIN)

def confirmUsername(transliteratedUserName):
    while True:
        sys.stdout.write("Will create user with username: {0}, ok? [yes/no]\n".format(transliteratedUserName))
        choice = raw_input().lower()
        if choice == 'yes':
            return transliteratedUserName
        elif choice == 'no':
           sys.stdout.write("Input desired username:\n")
           transliteratedUserName = raw_input()
        else:
            sys.stdout.write("Please respond with 'yes' or 'no'\n")

def createGroupsMembership(service, email):
    print("Adding user {0} to groups: {1}".format(email, string.join(args.groups), ','))
    for groupName in args.groups:
        print(createMembership(service, DOMAIN_GROUPS.get(groupName), email))
    print("Adding user {0} to city group: {1}".format(email, args.office))
    print(createMembership(service, DOMAIN_GROUPS.get(args.office), email))

def main():
    """Creates users with supplied creditinals
    """
    service = initializeService(SCOPES)
    for userName in args.user_names:
        translitiratedUserName = confirmUsername(translitirate(userName))
        givenName, familyName = translitiratedUserName.strip().split(' ')
        userParams = {'name': {'familyName': familyName, 'givenName': givenName }, 'changePasswordAtNextLogin': True, 'password': generatePass(translitiratedUserName), 'primaryEmail': generateDomainEmail(givenName, familyName) }
        print(userParams)
        userResult = createdUser(service, userParams)
        print(userResult)
        createGroupsMembership(service, userResult.get('primaryEmail'))


if __name__ == '__main__':
    main()
