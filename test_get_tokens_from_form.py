import BeautifulSoup, re, way2sms



def test_get_token_param():
    fp = open('sendSmsForm.html')
    formHtml = fp.read()
    formSoup = BeautifulSoup.BeautifulSoup(formHtml)
    print way2sms.get_token_param(formSoup)

if __name__ == '__main__':
    test_get_token_param()
