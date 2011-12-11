'''
Created on 11-Dec-2011

@author: alok
'''
import cookielib
import urllib2
import urllib
from BeautifulSoup import BeautifulSoup

_DEBUG = False

COOKIE_JAR = cookielib.CookieJar()
URL_OPENER = urllib2.build_opener(urllib2.HTTPCookieProcessor(COOKIE_JAR))
WAY_TO_SMS_BASE_URL=''
#WAY_TO_SMS_ENTRY_URL=WAY_TO_SMS_BASE_URL+'/content/index.html'
WAY_TO_SMS_ENTRY_URL='http://way2sms.com'
WAY_TO_SMS_AUTH_URL='Login1.action'
WAY_TO_SMS_SEND_SMS_ENTRY_URL='jsp/InstantSMS.jsp'
WAY_TO_SMS_MAIN_URL='Main.action'
WAY_TO_SMS_SEND_SMS_POST_URL='quicksms.action'
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
    WAY_TO_SMS_SEND_SMS_ENTRY_URL=WAY_TO_SMS_BASE_URL+'jsp/InstantSMS.jsp'
    WAY_TO_SMS_MAIN_URL=WAY_TO_SMS_BASE_URL+'Main.action'
    WAY_TO_SMS_SEND_SMS_POST_URL=WAY_TO_SMS_BASE_URL+'quicksms.action'
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

def open_send_sms_url():
    fp = URL_OPENER.open(WAY_TO_SMS_SEND_SMS_ENTRY_URL)
    resp = fp.read()
    soup = BeautifulSoup(resp)
    if (_DEBUG == True):
        print soup.prettify()
#    forms = soup.findAll('form')
# For now this itself must work.. THere's only one form in istantSms.jsp's response
    form = soup.find('form')
    if form is None:
        print 'Session Expired?, Relogging..'
        raise SessionExpired
    inputTags = form.findAll('input', attrs={'type':'hidden'})
    post_props = {}
    for inputTag in inputTags:
        if (_DEBUG == True):
            print 'Name:' + inputTag['name']
            print 'value:' + inputTag['value']
        post_props[inputTag['name']]=inputTag['value']
    return post_props
    
def send_sms(toMobileNo, textMsg):
    fp = URL_OPENER.open(WAY_TO_SMS_MAIN_URL)
    if (_DEBUG == True):
        soup=BeautifulSoup(fp.read())
        print soup.prettify()
    post_props = open_send_sms_url()
    post_props['chkall'] = 'on'
    post_props['MobNo'] = toMobileNo
    post_props['textArea'] = textMsg
    post_props['guid'] = 'username'
    post_props['gpwd'] = '*******'
    post_props['yuid'] = 'username'
    post_props['ypwd'] =  '*******'
    post_data = urllib.urlencode(post_props)
    fp = URL_OPENER.open(WAY_TO_SMS_SEND_SMS_POST_URL,post_data)
    if (_DEBUG == True):
        soup=BeautifulSoup(fp.read())
        print soup.prettify()
    print '\tSMS chunk sent!'
