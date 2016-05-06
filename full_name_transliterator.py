import re
import transliterate
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def transliterateFullName(string):
  text = unicode(string, 'utf-8')
  regex = r"[^\w\s]"
  pat = re.compile( regex )
  return pat.sub('', transliterate.translit(text, reversed=True))
