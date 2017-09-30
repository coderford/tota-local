from lxml import html
import requests
import json, ast, threading, re, os, sys



class Verto:

    baseUrl = 'https://ums.lpu.in/lpuums/'
    
    def __init__(self, reg_num, ums_pass,session):

        varToken = {'__LASTFOCUS': '','__EVENTTARGET': 'txtU',
            '__EVENTARGUMENT': '','__VIEWSTATE': '',
            '__VIEWSTATEGENERATOR': 'DD46A77E',
            '__SCROLLPOSITIONX': '0','__SCROLLPOSITIONY': '0',
            '__VIEWSTATEENCRYPTED': '','__EVENTVALIDATION': '',
            'txtU':	'','Txtpw': '','DropDownList1': '1'
            }

        self.regNum = reg_num
        self.umsPass = ums_pass
        self.logPayload = varToken
        self.log1Token = ['__VIEWSTATE','__EVENTVALIDATION']
        self.log2TokenDict = {'ddlStartWith': 'default3.aspx','iBtnLogins.x':	'0','iBtnLogins.y':	'0', }
        self.session = requests.session()
    
    def tokenSetter(self, page_num):
        if page_num == 1:
                self.logPayload['txtU'] = self.regNum
        elif page_num == 2:
            self.logPayload['txtU'] = self.regNum
            self.logPayload['__EVENTTARGET'] = ''
            self.logPayload['Txtpw'] = self.umsPass
            self.logPayload.update(self.log2TokenDict)
        return
        

