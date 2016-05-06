import os

MOSCOW='mos'
DOMAIN=os.environ['GOOGLE_DOMAIN']
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
