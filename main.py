# encoding=utf8
import sys
import string
import md5
import argparse
import google_admin_api
import full_name_transliterator
from constants import *


parser = argparse.ArgumentParser(description='Creates user in {0} domain, add him to specified groups.'.format(DOMAIN))
parser.add_argument('user_names', metavar='NAME1 NAME2', type=str, nargs='+', help='Usernames to create, in format: "Name Surname", will be transliterated and email will be automaticly made from translit')
parser.add_argument('--groups', dest='groups', default=['all', 'changes', 'exchange'], metavar='GROUP1 GROUP2', type=str, nargs='+', help='Groups')
parser.add_argument('--office', dest='office', default=MOSCOW, type=str, help='Office the new worker will work, default Moscow')

args = parser.parse_args()

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
    service = google_admin_api.initializeService(SCOPES)
    for userName in args.user_names:
        translitiratedUserName = confirmUsername(full_name_transliterator.transliterateFullName(userName))
        givenName, familyName = translitiratedUserName.strip().split(' ')
        userParams = {'name': {'familyName': familyName, 'givenName': givenName }, 'changePasswordAtNextLogin': True, 'password': generatePass(translitiratedUserName), 'primaryEmail': generateDomainEmail(givenName, familyName) }
        print(userParams)
        userResult = createdUser(service, userParams)
        print(userResult)
        createGroupsMembership(service, userResult.get('primaryEmail'))


if __name__ == '__main__':
    main()
