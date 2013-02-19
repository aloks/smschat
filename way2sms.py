'''
Created on 11-Dec-2011

@author: alok
'''
import cookielib
import urllib2
import urllib
import sys,re
from BeautifulSoup import BeautifulSoup

_DEBUG = False

COOKIE_JAR = cookielib.CookieJar()
URL_OPENER = urllib2.build_opener(urllib2.HTTPCookieProcessor(COOKIE_JAR))
USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.22) Gecko/20110902 Firefox/3.6.22'
URL_OPENER.addheaders = [('User-agent',USER_AGENT)]
WAY_TO_SMS_BASE_URL=''
#WAY_TO_SMS_ENTRY_URL=WAY_TO_SMS_BASE_URL+'/content/index.html'
WAY_TO_SMS_ENTRY_URL='http://way2sms.com'
WAY_TO_SMS_AUTH_URL='Login1.action'
WAY_TO_SMS_SEND_SMS_ENTRY_URL='jsp/SingleSMS.jsp'
WAY_TO_SMS_MAIN_URL='Main.action'
WAY_TO_SMS_SEND_SMS_POST_URL='jsp/stp2p.action'
MAX_CHUNK_SIZE = 135

def open_entry_url():
    global WAY_TO_SMS_AUTH_URL
    global WAY_TO_SMS_SEND_SMS_ENTRY_URL
    global WAY_TO_SMS_MAIN_URL
    global WAY_TO_SMS_SEND_SMS_POST_URL
    global WAY_TO_SMS_BASE_URL
    fp = URL_OPENER.open(WAY_TO_SMS_ENTRY_URL)
    WAY_TO_SMS_BASE_URL=fp.geturl()
    WAY_TO_SMS_AUTH_URL=WAY_TO_SMS_BASE_URL+'Login1.action'
    WAY_TO_SMS_SEND_SMS_ENTRY_URL=WAY_TO_SMS_BASE_URL+'jsp/SingleSMS.jsp'
    WAY_TO_SMS_MAIN_URL=WAY_TO_SMS_BASE_URL+'Main.action'
    WAY_TO_SMS_SEND_SMS_POST_URL=WAY_TO_SMS_BASE_URL+'jsp/stp2p.action'
#    print 'Some html obtained from: ' + WAY_TO_SMS_ENTRY_URL

def login_to_way2sms(username, password):
    open_entry_url()
    post_props = {'username':username,
                  'password':password,
                  'button':'Login'}
    post_data = urllib.urlencode(post_props)
    fp = URL_OPENER.open(WAY_TO_SMS_AUTH_URL, post_data)
    #Debug stuff
    if (_DEBUG == True):
        resp = fp.read()
        soup = BeautifulSoup(resp)
        print soup.prettify()
    print 'Session with Way2SMS Created!\n'

class SessionExpired(Exception):
    pass

def open_send_sms_url(token):
    fp = URL_OPENER.open(WAY_TO_SMS_SEND_SMS_ENTRY_URL+'?Token='+token)
    resp = fp.read()
    soup = BeautifulSoup(resp)
    if (_DEBUG == True):
        print 'Opened URL:' + WAY_TO_SMS_SEND_SMS_ENTRY_URL+'?Token='+token
        print 'The send sms form follows'
        print soup.prettify()
#    forms = soup.findAll('form')
# For now this itself must work.. THere's only one form in istantSms.jsp's response
    form = soup.find('form')
    if form is None:
        print 'Session Expired?, Relogging..?'
        raise SessionExpired
    inputTags = form.findAll('input', attrs={'type':'hidden'})
    post_props = {}
    for inputTag in inputTags:
        if (_DEBUG == True):
            print 'Name:' + inputTag['name']
            print 'value:' + inputTag['value']
        post_props[inputTag['name']]=inputTag['value']
    return post_props, form

def open_main_and_get_token():
    fp = URL_OPENER.open(WAY_TO_SMS_MAIN_URL)
    soup=BeautifulSoup(fp.read())
    tokenElem = soup.find('input', attrs={'id':'Token'})
    if (_DEBUG == True):
        print tokenElem
        print tokenElem['value']
        print 'Opened: ' + WAY_TO_SMS_MAIN_URL
        print soup.prettify()

    if (tokenElem == None):
        print 'Session Expired?, Relogging..?'
        raise SessionExpired

    return tokenElem['value']
    
def get_mob_no_param(form):
    mob_no_param = form.find('input', attrs={'value': 'Mobile Number'})['name']
    if (_DEBUG == True):
        print mob_no_param
    return mob_no_param

def get_token_param(form):
    token_param = None
    scriptTags = form.findAll(name='script')
    for scriptTag in scriptTags:
        tokenScriptTag = scriptTag.find(text=re.compile('.*rqTok=.*'))
        if (tokenScriptTag!=None):
            for tokenScriptTagLine in tokenScriptTag.splitlines():
                r = re.search('.*rqTok="(.*)".*;.*', tokenScriptTagLine)
                if (r != None):
                    token_param = r.group(1)
    '''
    textAreasElems = form.findAll('textarea')
    for textAreasElem in textAreasElems:
        if (textAreasElem['name'] != 'textArea'):
            token_param = textAreasElem['name']
            break
            '''

    if (_DEBUG == True):
        print 'Token Param: ' + token_param

    return token_param

def send_sms(toMobileNo, textMsg):
    token = open_main_and_get_token()
    post_props, form = open_send_sms_url(token)

    mob_no_param = get_mob_no_param(form)
    token_param = get_token_param(form)

    post_props[mob_no_param] = toMobileNo
    post_props[token_param] = token
    post_props['textArea'] = textMsg
    post_props['nrc'] = 'nrc'
    post_props['wasup'] = 'push358'
    post_props['HiddenAction'] = 'instantsms'
    post_props['chkall'] = 'instantsms'

    post_data = urllib.urlencode(post_props)

    if (_DEBUG == True):
        print 'Generated Post Props:'
        print post_props
        print 'Generated Post_data:'
        print post_data

    fp = URL_OPENER.open(WAY_TO_SMS_SEND_SMS_POST_URL,post_data)
    if (_DEBUG == True):
        soup=BeautifulSoup(fp.read())
        print soup.prettify()
    print '\tSMS chunk sent!'


if __name__ == '__main__':

    if (len(sys.argv) != 5):
        print 'Usage: '+sys.argv[0] + ' login_cell_no password to_cell_no msg'
        sys.exit()

    login_cell_no = sys.argv[1]
    password = sys.argv[2]
    to_cell_no = sys.argv[3]
    msg = sys.argv[4]

    login_to_way2sms(login_cell_no, password)
    send_sms(to_cell_no, msg)

