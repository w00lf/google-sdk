# encoding=utf8
import os
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
parser.add_argument('--debug', dest='debug', default=False, type=bool, help='Print debug messages')

args = parser.parse_args()
DEBUG = args.debug

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
    if DEBUG:
        print("Adding user {0} to groups: {1}".format(email, string.join(args.groups), ','))
    for groupName in args.groups:
        result = createMembership(service, DOMAIN_GROUPS.get(groupName), email)
        if DEBUG:
            print(result)
    if DEBUG:
        print("Adding user {0} to city group: {1}".format(email, args.office))
    result = createMembership(service, DOMAIN_GROUPS.get(args.office), email)
    if DEBUG:
        print(result)

def printInstructions(email, emailPassword, cmsPassword):
    template = unicode(open(INSTRUCTIONS_FILE_NAME, 'r').read(), 'utf8')
    print template.format(email=email, emailPassword=emailPassword, cmsPassword=cmsPassword)

def usage():
    print "Create File '{0}' with variables 'email', 'emailPassword' and 'cmsPassword' to continue".format(INSTRUCTIONS_FILE_NAME)

def meetAllPrerequirments():
    return os.path.isfile(INSTRUCTIONS_FILE_NAME)

def main():
    """Creates users with supplied creditinals
    """
    if(not meetAllPrerequirments()):
        usage()
        exit()

    service = google_admin_api.initializeService(SCOPES)

    for userName in args.user_names:
        translitiratedUserName = confirmUsername(full_name_transliterator.transliterateFullName(userName))
        givenName, familyName = translitiratedUserName.strip().split(' ')

        emailPassword = generatePass(translitiratedUserName)[:8]
        email = generateDomainEmail(givenName, familyName)

        userParams = {'name': {'familyName': familyName, 'givenName': givenName }, 'changePasswordAtNextLogin': True, 'password': emailPassword, 'primaryEmail': email }
        if DEBUG:
            print(userParams)
        userResult = createdUser(service, userParams)
        if DEBUG:
            print(userResult)
        createGroupsMembership(service, userResult.get('primaryEmail'))
        printInstructions(email=email, emailPassword=emailPassword, cmsPassword=generatePass('cms' + translitiratedUserName)[:8])


if __name__ == '__main__':
    main()
