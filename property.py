'''
Created on 10-Dec-2011

@author: alok
'''

import sys
import os


class NoPropertyFileError(Exception):
    def __init__(self, value=None):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ExpectedPropertyNotFoundError(Exception):
    def __init__(self, value=None):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ConfigProps():

    def __init__(self, config_file_path = None, expected_prop_list = None):
        '''
        
        @param config_file_path: The path of the property file
        @param expected_prop_list: To get the objects of the properties to be looked for
                                    in the properties file pass a list of properties which 
                                    have to searched for in the properties file 
                                    If any of the expected property is not found in the property
                                    file then there would be a  ExpectedPropertyNotFoundError thrown
        '''
        if (config_file_path == None):
            raise NoPropertyFileError
        else:
            self._config_file_path = config_file_path

        if not os.path.exists(config_file_path):
            print 'Enter ePO and its db information in '+ config_file_path + ' file in same directory as mentioned in Readme'
            raise NoPropertyFileError(config_file_path)
        else:
            fp = open(config_file_path)
            props = {}
            for line in fp:
                if line.strip().startswith('#'): continue
                nameVal = line.strip().split('=')
                props[nameVal[0].strip()]=nameVal[1].strip()
                
        def get_get_method_for_attr(self, attr_name):
            return lambda : getattr(self, attr_name)
        
        propnamesToIsInitedMap = {}
        expectedPropList = expected_prop_list
        
        for key in props:
            for propName in expectedPropList:
                if (key == propName):
                    attrName = '_' + propName.replace('.','')
                    setattr(self, attrName, props[key])
                    propnamesToIsInitedMap[propName] = True
                    #Reflectively set the get_methods names too
                    methodName = 'get_' + propName.replace('.', '_')
                    setattr(self, methodName, get_get_method_for_attr(self, attrName))
            
        is_exit_reqd = False
        if expectedPropList != None:
            not_found_props = []
            for prop in expectedPropList:
                if prop not in propnamesToIsInitedMap:
                    is_exit_reqd = True
                    not_found_props.append(prop)
            
            not_found_str = ','.join(not_found_props)
            
            if is_exit_reqd == True:
                raise ExpectedPropertyNotFoundError('Properties: ' + not_found_str + ' not found in ' + config_file_path)

PROPERTIES_FILE='send_sms.properties.temp'

if __name__ == '__main__':
    
    #To get the objects of the properties to be looked for in the properties file add to the list below
    expectedPropList = [
                        'way2sms.username',
                        'way2sms.password',
                        'contacts.file'
                        ]
       
    configs = ConfigProps(PROPERTIES_FILE, expectedPropList)
    print configs.get_way2sms_username()
    print configs.get_way2sms_password()
    print configs.get_contacts_file()
#    print configs.get_email_to()
