from lxml import html
import requests
import threading
from user import Verto
from messages import Messages

def getRequest(session, base_url):
    homeData = session.get(base_url)
    homeData = html.fromstring(homeData.content)
    return homeData


def postRequest(session, base_url, post_payload=None, meta_stream=None):
    tree1 = session.post(base_url, data=post_payload, files=meta_stream)
    tree = html.fromstring(tree1.content)
    return tree


def attrGetter(page_data, name, payload):
    items = page_data.xpath('//input[@name="' + name +
                            '" and @type="hidden"]/@value')
    for item in items:
        try:
            if payload[name] != item:
                payload[name] = item
                return True
            else:
                raise ValueError("Token Values are SAME! - Try Again")
        except ValueError as error:
            print('Error: ' + error)
            return None
    return None


def tokenGetter(page_data, token_list, payload):
    for item in token_list:
        threads = threading.Thread(
            target=attrGetter, args=(page_data, item, payload))
        threads.start()
    threads.join()
    return None


def homePage(reg_number1,ums_pass):
    sess = requests.session()
    user = Verto(reg_number1,ums_pass, sess)
    homeData = getRequest(sess, user.baseUrl)
    tokenGetter(homeData, user.log1Token, user.logPayload)
    user.tokenSetter(1)
    homeData = postRequest(sess, user.baseUrl, user.logPayload)
    tokenGetter(homeData, user.log1Token, user.logPayload)
    user.tokenSetter(2)
    homeData = postRequest(sess, user.baseUrl, user.logPayload)
    return homeData

def mesgData(page_data):
    userMsg = Messages(page_data)
    return userMsg.mesgList
    
h = homePage('11704266','Allofusare1@')
p = mesgData(h)
print(str(p))