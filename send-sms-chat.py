'''
Created on Apr 23, 2011

@author: alok
'''

import sys
import csv
import re
import urllib2, cookielib, urllib, os
from BeautifulSoup import BeautifulSoup

PROPERTIES_FILE_NAME='send_sms.properties'

_DEBUG = False

class PhoneContact():
    def __init__(self, first_name = None, last_name = None, phone_no = None):
        if (first_name == None):
            self._first_name = u''
        else:
            self._first_name = first_name

        if (last_name == None):
            self._last_name = u''
        else:
            self._last_name = last_name
        if (phone_no == None):
            self._phone_no = u''
        else:
            self._phone_no = phone_no

    def get_first_name(self):
        return self._first_name

    def get_last_name(self):
        return self._last_name

    def get_phone_no(self):
        return self._phone_no
    
    def set_first_name(self, first_name):
        self._first_name = first_name

    def set_last_name(self, last_name):
        self._last_name = last_name

    def set_phone_no(self, phone_no):
        self._phone_no = phone_no

    def print_to_std_out(self):
        print '\t\tFirst Name: '+ self.get_first_name()
        print '\t\tLast Name: '+ self.get_last_name()
        print '\t\tPhone Number: ' + self.get_phone_no()


class NoPropertyFileError(Exception):
    def __init__(self, value=None):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ConfigProps():
    def __init__(self, config_file_path = None):
        if (config_file_path == None):
            raise NoPropertyFileError
        else:
            self._config_file_path = config_file_path

        if not os.path.exists(config_file_path):
            print 'Enter way2sms creds way2sms.username and way2sms.password and contacts.file name in '+ PROPERTIES_FILE_NAME + ' file in same directory'
            raise NoPropertyFileError(config_file_path)
        else:
            fp = open(config_file_path)
            props = {}
            for line in fp:
                if line.strip().startswith('#'): continue
                nameVal = line.strip().split('=')
                props[nameVal[0]]=nameVal[1]
        
        for key in props:
            if (key == 'way2sms.username'): self._username = props[key]
            elif (key == 'way2sms.password'): self._password = props[key]
            elif (key == 'contacts.file'): self._contacts_csv = props[key]

    def get_way2sms_username(self):
        return self._username

    def get_way2sms_password(self):
        return self._password

    def get_contacts_csv_file_path(self):
        return self._contacts_csv


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

def print_usage():
    print '\n  Usage: ' + (sys.argv[0]).split('\\')[-1] + ' "cell_no/start_of_first_name_or_last_name_of_contact"\n'
    print '    "Each sent message of yours can be any length, '
    print '    your message will be broken down to '+ str(MAX_CHUNK_SIZE) + ' chars each SMS\'es)"' 
    print_command_line_args()

def print_command_line_args():
    print '\tIf the Cell No is specified it must be 10 digits'
    print '\tElse the string is matched for first name and last name in the contacts csv file mentioned in '+ PROPERTIES_FILE_NAME 

def get_way2sms_creds_from_properties_file():
    if not os.path.exists(PROPERTIES_FILE_NAME):
        print 'Enter way2sms creds way2sms.username and way2sms.password in '+ PROPERTIES_FILE_NAME 
        sys.exit()
    else:
        fp = open(PROPERTIES_FILE_NAME)
        props = {}
        for line in fp:
            if line.strip().startswith('#'): continue
            nameVal = line.strip().split('=')
            props[nameVal[0]]=nameVal[1]
        
        for key in props:
            if (key == 'way2sms.username'): username = props[key]
            elif (key == 'way2sms.password'): password = props[key]
            elif (key == 'contacts.file'): contacts_csv = props[key]
        
        return (username, password, contacts_csv)

def break_msg_into_chunks(message):
    msg_chunks = []
    msg_len = len(message)
    no_of_msgs = msg_len/MAX_CHUNK_SIZE + 1
    start_index = 0
    last_index = MAX_CHUNK_SIZE -1
    for msg_no in range(no_of_msgs):
        if msg_no == no_of_msgs -1:
            msg_chunks.append(message[start_index: start_index + msg_len%MAX_CHUNK_SIZE +1])
            continue
        msg_chunks.append(message[start_index: last_index])
        start_index = (msg_no+1)*MAX_CHUNK_SIZE -1
        last_index = start_index + MAX_CHUNK_SIZE
    return msg_chunks

def append_footer_to_msg(msg_chunk, chunk_no, total_chunks):
    return msg_chunk + ' ' + str(chunk_no + 1) + '/' + str(total_chunks)

def set_contact_attr_from_name_val(contact, name, val):
    if (name == u'First name'):
        contact.set_first_name(val)
    elif (name == u'Last name'):
        contact.set_last_name(val)
    elif (name == u'General phone'):
        contact.set_phone_no(val)

def get_name_vals(splits):  
    name = splits[0].strip()
    val = splits[1].strip()
    return (name, val)

import codecs

def get_contacts_list_from_file(file_path):
    fp = codecs.open(file_path, 'r', 'utf-16')
    contacts = []
    contact = PhoneContact()
    for line in fp:
        splits = line.split(u':')
        if len(splits) == 2:
            (name, val) = get_name_vals(splits)
            set_contact_attr_from_name_val(contact, name, val)
        else:
            contacts.append(contact)
            contact = PhoneContact()
    contacts.append(contact)
    return contacts

def get_contacts_which_match(contacts, match_str):
    matched_contacts = []
    for contact in contacts:
        if contact.get_first_name().lower().find(match_str.lower()) == 0 or contact.get_last_name().lower().find(match_str.lower()) == 0:
            matched_contacts.append(contact)
    return matched_contacts

def is_contact_confirmed_by_user(contact):
    contact.print_to_std_out()
    user_choice=raw_input('Send SMS to this contact? ([y/Y/Yes/yes]/[n/N/No/no]):')
    user_choice=user_choice.strip()
    if user_choice.lower() == 'y' or user_choice.lower() == 'yes':
        return True
    elif user_choice.lower() == 'n' or user_choice.lower() == 'no': return False
    else:
        print 'Invalid option specified! Re-enter choice!!'
        return is_contact_confirmed_by_user(contact)

def get_user_confirmed_contacts(matched_contacts):
    user_confirmed_contacts = []
    print 'Choose the contacts to whom SMS has to be sent:'
    for i, contact in enumerate(matched_contacts):
        print '\t'+ str(i+1) + ') Matched Contact details:'
        is_user_confirmed = is_contact_confirmed_by_user(contact)
        if is_user_confirmed:
            user_confirmed_contacts.append(contact)

    return user_confirmed_contacts

def send_sms_to_contact_no(contact_no, full_msg):
    msg_chunks = break_msg_into_chunks(full_msg)
    for chunk_no, chunk in enumerate(msg_chunks):
        print '\tSending SMS Chunk Number: ' + str(chunk_no+1) + ' ...'
        is_sent_flag = False
        while is_sent_flag == False:
            try:
                if len(msg_chunks) == 1:
                    send_sms(contact_no, chunk)
                else:
                    send_sms(contact_no, append_footer_to_msg(chunk, chunk_no, len(msg_chunks)))
                is_sent_flag = True
            except SessionExpired:
                props = ConfigProps(PROPERTIES_FILE_NAME)
                open_entry_url()
                login_to_way2sms(props.get_way2sms_username(), props.get_way2sms_password())

class NotATenDigitNo(Exception):
    def __init__(self, digit_str):
        self.digit_str = digit_str
    def __str__(self):
        return repr(self.digit_str)

def send_sms_to_contacts(to_send_contacts, message):
    for contact in to_send_contacts:
        ten_digit_no = contact.get_phone_no()[-10:]
        if not is_ten_digit_number(ten_digit_no):
            raise NotATenDigitNo(ten_digit_no)

        print 'Sending Sms to: ' + contact.get_first_name() + ' ' + contact.get_last_name() + '(' + ten_digit_no +')'
        send_sms_to_contact_no(ten_digit_no, message)

def is_add_to_contacts_requested(cell_no):
    user_choice=raw_input('Do you want to add ' + cell_no + ' contact for future use? ([y|Y|yes|yEs]/[n|N|nO|NO|No|no]):')
    user_choice=user_choice.strip()
    if user_choice.lower() == 'y' or user_choice.lower() == 'yes': return True
    elif user_choice.lower() == 'n' or user_choice.lower() == 'no': return False
    else:
        print 'Invalid option specified! Re-enter choice!!'
        return is_add_to_contacts_requested(cell_no)

def get_first_last_name_from_user(cell_no):
    first_name = raw_input('Please enter First Name for contact with phone no: ' + cell_no + ' : ')
    last_name = raw_input('Please enter Last Name for contact with phone no: ' + cell_no + ' : ')
    return (first_name, last_name)

def add_contact_to_file(first_name, last_name, cell_no, contact_file_path):
    print "TODO: add_contact_to_file introduces the UTF-16 BOM?? at the end of the file where appending starts which is why things aren't clean in this approact"
    return
    fp = codecs.open(contact_file_path, 'a+', 'utf-16')
    fp.write('\nFirst name:    ' + first_name + '\nLast name:    '+ \
             last_name + '\nGeneral phone:    '+ cell_no+ '\n') 

def add_contact_to_csv(first_name, last_name, cell_no, csv_file_path):
    rows = get_all_rows_from_csv(csv_file_path)
    fp = open(csv_file_path, 'wb')
    csvW = csv.writer(fp)
    row = []
    row.append(first_name)
    row.append(last_name)
    row.append(cell_no)
    rows.append(row)
    csvW.writerows(rows)

def ask_and_add_to_contacts(cell_no, csv_file_path):
    is_adding_reqd = is_add_to_contacts_requested(cell_no)
    if is_adding_reqd:
        (first_name, last_name) = get_first_last_name_from_user(cell_no)
        add_contact_to_csv(first_name, last_name, cell_no, csv_file_path)
        return (first_name, last_name)
    else:
        return ('','')

def create_empty_file(csv_file_name):
    fp = open(csv_file_name, 'wb')

def get_all_rows_from_csv(csv_file_name):
    try:
        fp = open(csv_file_name, 'rb')
    except IOError:
        create_empty_file(csv_file_name)
        fp = open(csv_file_name, 'rb')
    csvR = csv.reader(fp)
    rows = []
    for row in csvR:
        rows.append(row)
    return rows

def get_contacts_list_from_csv(csv_file_name):
    try:
        fp = open(csv_file_name, 'rb')
    except IOError:
        create_empty_file(csv_file_name)
        fp = open(csv_file_name, 'rb')
    csvR = csv.reader(fp)
    contacts = []
    for row in csvR:
        contact = PhoneContact(row[0], row[1], row[2])
        contacts.append(contact)
    return contacts

def starrify_print(str):
    return ((80-len(str))/2)*'*' + str + ((80-len(str))/2)*'*'

def print_messaging_options():
    menu_title = ' Menu '
    print starrify_print(menu_title)
    to_quit_help = ' To Quit Chat press only <ENTER> without any text after > '
    to_send_help = ' To Send Msg via SMS, Type the Message and Press <ENTER> ' 
    to_add_help = ' To Add contacts to send sms to, Type "a|A" and Press <ENTER> '
    to_del_help = ' To Remove contacts to send sms to, Type "d|D" and Press <ENTER> '
    print '\to' + to_send_help
    print '\to' + to_add_help
    print '\to' + to_del_help
    print '\to' + to_quit_help + '\n'

def get_message_from_user(to_send_contacts):
    names = []
    for name in to_send_contacts:
        names.append(name.get_first_name() + ' ' + \
                     name.get_last_name())

    print_messaging_options()

    message = raw_input('Next SMS Contents to: "' + ','.join(names) + '"> ')
    if len(message.strip()) != 0:
        return message
    else:
        return None

def is_ten_digit_number(str = None):
    if str!= None and re.match('\d{10}', str) != None:
        return True
    else:
        return False

def ask_if_confirm_exit():
    user_choice=raw_input('Really exit sms chat program ([y|Y|yes|yEs]/[n|N|nO|NO|No|no]):')
    user_choice=user_choice.strip()
    if user_choice.lower() == 'y' or user_choice.lower() == 'yes': return True
    elif user_choice.lower() == 'n' or user_choice.lower() == 'no': return False
    else:
        print 'Invalid option specified! Re-enter choice!!'
        return ask_if_confirm_exit()

def ask_contact_has_to_be_removed(contact):
    contact.print_to_std_out()
    user_choice=raw_input('Do you want to remove the above contact for next sms chats ([y|Y|yes|yEs]/[n|N|nO|NO|No|no]):')
    user_choice=user_choice.strip()
    if user_choice.lower() == 'y' or user_choice.lower() == 'yes': return True
    elif user_choice.lower() == 'n' or user_choice.lower() == 'no': return False
    else:
        print 'Invalid option specified! Re-enter choice!!'
        return ask_contact_has_to_be_removed(contact)

def remove_some_from_to_send(to_send_contacts):
    new_to_send = []
    for contact in to_send_contacts:
        is_contact_to_be_removed = ask_contact_has_to_be_removed(contact)
        if is_contact_to_be_removed == True: continue
        else: new_to_send.append(contact)
    return new_to_send

def get_matched_contacts_from_user(to_match_name_or_no):
    props = ConfigProps(PROPERTIES_FILE_NAME)
    matched_contacts = []
    if is_ten_digit_number(to_match_name_or_no):
        cell_no = to_match_name_or_no
        print 'Number detected!'
        (first_name, last_name) = ask_and_add_to_contacts(cell_no, props.get_contacts_csv_file_path())
        matched_contacts.append(PhoneContact(first_name, last_name, cell_no))
    else:
        name_to_be_matched = to_match_name_or_no
        contacts = get_contacts_list_from_csv(props.get_contacts_csv_file_path())
        matched_contacts = get_contacts_which_match(contacts, name_to_be_matched)
        if len(matched_contacts) == 0:
            print 'No matches of ' + name_to_be_matched + ' found in ' + props.get_contacts_csv_file_path()

    to_send_contacts = get_user_confirmed_contacts(matched_contacts)

    return to_send_contacts


def add_some_more_to_send(to_send_contacts):
    new_to_send = []
    for contact in to_send_contacts:
        new_to_send.append(contact)
    to_add_contact_name = raw_input('Enter the name of the contact or the cell no you want to add to the sender\'s list:')
    if len(to_add_contact_name) != 0:
        to_send_matched_contacts = get_matched_contacts_from_user(to_add_contact_name)
        for matched_contact in to_send_matched_contacts:
            new_to_send.append(matched_contact)
    else:
        print 'Empty string contact name search not allowed!!'
    return new_to_send

if __name__ == '__main__':
    if len(sys.argv) == 2:
        props = ConfigProps(PROPERTIES_FILE_NAME)
        argv1 = sys.argv[1]
        to_send_contacts = get_matched_contacts_from_user(argv1)
        if len(to_send_contacts) == 0:
            print 'No Contacts to send, Exiting.. '
            sys.exit()
        open_entry_url()
        login_to_way2sms(props.get_way2sms_username(), props.get_way2sms_password())
        while 1:
            if len(to_send_contacts) == 0:
                print 'No Contacts to send, Exiting.. '
                sys.exit()
            message = get_message_from_user(to_send_contacts)
            if message == None:
                if (ask_if_confirm_exit() == True):
                    break
                else:
                    continue
            elif message.lower() == 'd':
                to_send_contacts = remove_some_from_to_send(to_send_contacts)
                if (len(to_send_contacts) == 0):
                    if (ask_if_confirm_exit() == False):
                        to_send_contacts = add_some_more_to_send(to_send_contacts)
    
            elif message.lower() == 'a':
                to_send_contacts = add_some_more_to_send(to_send_contacts)
            else:
                send_sms_to_contacts(to_send_contacts, message)
    else:
        print_usage()


