from lxml import html
import requests



class Verto:
    '''
    This class contains essential data to instantiate User's UMS Homepage Data Object.

    Attributes::

    baseUrl (`obj:str`): Url of UMS
    logPayload (`obj:dict`): Containes those variable whose values are need to get extracted from UMS page itself.
    log1Token (`obj:dict`): Containes esseential variables to simulate login-first page request.
    log2TokenDict (`obj:dict`): Containes esseential variables to simulate login-final page request.
    session (`class:requests.session`): Represents an session object in which all the requests are made.
    regNum (`obj:str`): Registration Number of UMS.
    umsPass (`obj:str`): Password of UMS.

    Args::

    reg_num (`obj:str`): Registration Number of UMS.
    ums_pass (`obj:str`): Password of UMS.
    session (`class:requests.session`): Represents an pre intialized instance of session object in which all the requests are made.
    page_num: (`obj:str`): Keep trace of pages requested. Login-first is 1 and Login-second is 2.

    Raises:
        ValueError: If page_num is not an acceptable int.
    '''
    baseUrl = 'https://ums.lpu.in/lpuums/' 
    
    def __init__(self, reg_num, ums_pass,session):

        self.regNum = reg_num
        self.umsPass = ums_pass

        self.logPayload = {'__LASTFOCUS': '','__EVENTTARGET': 'txtU',
            '__EVENTARGUMENT': '','__VIEWSTATE': '',
            '__VIEWSTATEGENERATOR': 'DD46A77E',
            '__SCROLLPOSITIONX': '0','__SCROLLPOSITIONY': '0',
            '__VIEWSTATEENCRYPTED': '','__EVENTVALIDATION': '',
            'txtU':	'','Txtpw': '','DropDownList1': '1'
            }

        self.log1Token = ['__VIEWSTATE','__EVENTVALIDATION']
        self.log2TokenDict = {'ddlStartWith': 'default3.aspx','iBtnLogins.x':	'0','iBtnLogins.y':	'0', }
        self.session = requests.session()
    
    def tokenSetter(self, page_num):
        '''
        This method will set the essential variables according to specific page.
        '''
        try:
            if page_num == 1:
                    self.logPayload['txtU'] = self.regNum
            elif page_num == 2:
                self.logPayload['txtU'] = self.regNum
                self.logPayload['__EVENTTARGET'] = ''
                self.logPayload['Txtpw'] = self.umsPass
                self.logPayload.update(self.log2TokenDict)
            else:
                raise ValueError("`arg:page_num` is not a acceptable int")
        except ValueError as e:
            print("Error: {}".format(e))
        return
        

