'''
Created on Apr 23, 2011

@author: alok
'''

import urllib2, cookielib, urllib, os
from BeautifulSoup import BeautifulSoup
import sys
import csv
import re

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

COOKIE_JAR = cookielib.CookieJar()
URL_OPENER = urllib2.build_opener(urllib2.HTTPCookieProcessor(COOKIE_JAR))
WAY_TO_SMS_ENTRY_URL='http://site3.way2sms.com/entry.jsp'
WAY_TO_SMS_AUTH_URL='http://site3.way2sms.com/auth.cl'
WAY_TO_SMS_SEND_SMS_ENTRY_URL='http://site3.way2sms.com/jsp/InstantSMS.jsp'
WAY_TO_SMS_MAIN_URL='http://site3.way2sms.com/jsp/Main.jsp'
WAY_TO_SMS_SEND_SMS_POST_URL='http://site3.way2sms.com/FirstServletsms'
MAX_CHUNK_SIZE = 135

def open_entry_url():
    fp = URL_OPENER.open(WAY_TO_SMS_ENTRY_URL)
#    print 'Some html obtained from: ' + WAY_TO_SMS_ENTRY_URL

def login_to_way2sms(username, password):
    post_props = {'username':username,
                  'password':password,
                  'Submit':'Sign+in'}
    post_data = urllib.urlencode(post_props)
    fp = URL_OPENER.open(WAY_TO_SMS_AUTH_URL, post_data)
    resp = fp.read()
    print 'Login Done!'


class SessionExpired(Exception):
    pass

def open_send_sms_url():
    fp = URL_OPENER.open(WAY_TO_SMS_SEND_SMS_ENTRY_URL)
    resp = fp.read()
    soup = BeautifulSoup(resp)
#    forms = soup.findAll('form')
# For now this itself must work.. THere's only one form in istantSms.jsp's response
    form = soup.find('form')
    if form is None:
        print 'Session Expired?, Relogging..'
        raise SessionExpired
    inputTags = form.findAll('input', attrs={'type':'hidden'})
    post_props = {}
    for inputTag in inputTags:
#        print 'Name:' + inputTag['name']
#        print 'value:' + inputTag['value']
        post_props[inputTag['name']]=inputTag['value']
    return post_props
    
def send_sms(toMobileNo, textMsg):
    URL_OPENER.open(WAY_TO_SMS_MAIN_URL)
    post_props = open_send_sms_url()
    post_props['chkall'] = 'on'
    post_props['MobNo'] = toMobileNo
    post_props['textArea'] = textMsg
    post_props['guid'] = 'username'
    post_props['gpwd'] = '*******'
    post_props['yuid'] = 'username'
    post_props['ypwd'] =  '*******'
    post_data = urllib.urlencode(post_props)
    URL_OPENER.open(WAY_TO_SMS_SEND_SMS_POST_URL,post_data)
    print '\tSMS chunk sent!'

def print_usage():
    print '\n  Usage: ' + (sys.argv[0]).split('\\')[-1] + ' "cell_no/start_of_first_name_or_last_name_of_contact"\n'
    print '    "Each sent message of yours can be any length, '
    print '    your message will be broken down to '+ str(MAX_CHUNK_SIZE) + ' chars each SMS\'es)"' 
    print_command_line_args()

def print_command_line_args():
    print '\tIf the Cell No is specified it must be 10 digits'
    print '\telse the string is matched for first name and last name in the contacts csv file mentioned in send_sms.properties file'

def get_way2sms_creds_from_properties_file():
    if not os.path.exists('send_sms.properties'):
        print 'Enter way2sms creds way2sms.username and way2sms.password in send_sms.properties file'
        sys.exit()
    else:
        fp = open('send_sms.properties')
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
    first_name = ''
    last_name = ''
    phone_no = ''
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
        is_contact_confirmed_by_user(contact)

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
                    send_sms(contact_no, msg_chunks)
                else:
                    send_sms(contact_no, append_footer_to_msg(chunk, chunk_no, len(msg_chunks)))
                is_sent_flag = True
            except SessionExpired:
                creds = get_way2sms_creds_from_properties_file()
                open_entry_url()
                login_to_way2sms(creds[0], creds[1])

def send_sms_to_contacts(to_send_contacts, message):
    for contact in to_send_contacts:
        print 'Sending Sms to: ' + contact.get_first_name() + ' ' + contact.get_last_name() + '(' + contact.get_phone_no()[-10:]+')'
        send_sms_to_contact_no(contact.get_phone_no()[-10:], message)

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
    fp.write('\nFirst name:	' + first_name + '\nLast name:	'+ \
             last_name + '\nGeneral phone:	'+ cell_no+ '\n') 

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
        return None

def get_all_rows_from_csv(csv_file_name):
    fp = open(csv_file_name, 'rb')
    csvR = csv.reader(fp)
    rows = []
    for row in csvR:
        rows.append(row)
    return rows

def get_contacts_list_from_csv(csv_file_name):
    fp = open(csv_file_name, 'rb')
    csvR = csv.reader(fp)
    contacts = []
    for row in csvR:
        contact = PhoneContact(row[0], row[1], row[2])
        contacts.append(contact)

    return contacts

def get_message_from_user(to_send_contacts):
    names = []
    for name in to_send_contacts:
        names.append(name.get_first_name() + ' ' + \
                     name.get_last_name())

    to_quit_help = ' To Quit Chat press only <ENTER> without any text after > '
    print ((80-len(to_quit_help))/2)*'*' + to_quit_help + ((80-len(to_quit_help))/2)*'*'+ '\n'
    to_send_help = ' To Send Msg via SMS, Type the Message and Press <ENTER>: ' 
    print ((80-len(to_send_help))/2)*'*' + to_send_help + ((80-len(to_send_help))/2)*'*' + '\n'

    message = raw_input('Next SMS Contents to: "' + ','.join(names) + '"> ')
    if len(message.strip()) != 0:
        return message
    else:
        return None

if __name__ == '__main__':
    if len(sys.argv) == 2:
        creds = get_way2sms_creds_from_properties_file()
        csv_file_path = creds[2]
        argv1 = sys.argv[1]
        matched_contacts = []
        #Check for a 10 digit int in the argv1
        if re.match('\d{10}',argv1) != None:
            cell_no = argv1
            print 'Number detected!'
            ret = ask_and_add_to_contacts(cell_no, csv_file_path)
            if ret:
                matched_contacts.append(PhoneContact(ret[0], ret[1], cell_no))
            else:
                matched_contacts.append(PhoneContact('', '', cell_no))
        else:
            name_to_be_matched = sys.argv[1]
            contacts = get_contacts_list_from_csv(csv_file_path)
            matched_contacts = get_contacts_which_match(contacts, name_to_be_matched)
        if len(matched_contacts) == 0:
            print 'No Matches found!!'
            print_command_line_args()
        else:
            to_send_contacts = get_user_confirmed_contacts(matched_contacts)
            if len(to_send_contacts) == 0:
                print 'No Contacts to send, Exiting.. '
                sys.exit()
            open_entry_url()
            login_to_way2sms(creds[0], creds[1])
            message = get_message_from_user(to_send_contacts)
            while message != None:
                send_sms_to_contacts(to_send_contacts, message)
                message = get_message_from_user(to_send_contacts)
    else:
        print_usage()
