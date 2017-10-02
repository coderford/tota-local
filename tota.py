from lxml import html
import requests
import threading
from user import Verto
from messages import Messages

def getRequest(session, base_url):
    '''
    It will return an html tree `obj:lxml.html` parsed by `class:lxml.html`.
    Http requests are made in `class:requests.session`.

    Args::

    session (`class:requests.session`): Represents an pre intialized instance of session object in which all the requests are made.
    base_url (`class:str`): Url to get fetched.

    '''
    homeData = session.get(base_url)
    homeData = html.fromstring(homeData.content)
    return homeData


def postRequest(session, base_url, payload=None, meta_stream=None):
    '''
    It will return an html tree `obj:lxml.html` parsed by `class:lxml.html`.
    Http requests are made in `class:requests.session`.

    Args::

    session (`class:requests.session`): Represents an pre intialized instance of session object in which all the requests are made.
    base_url (`class:str`): Url to get fetched.
    payload (`class:dict`): Essential data to use in request payload or request body.
    meta_stream ('class:tuple): Essential data to use in upload stream of a request.

    Raises:

    ValueError: If something wrong with base_url or payload.
    '''
    try:
        tree = session.post(base_url, data=payload, files=meta_stream)
        if tree.status_code == 200:
            tree = html.fromstring(tree.content)
            return tree
        else: 
            raise ValueError("Something wrong with base_url or payload.")
            return None
    except ValueError as e:
        print('Method: postRequest | Error: {}'.format(e))
    


def attrGetter(page_data, name, payload):
    '''
    It will find values of specific html element with specific attributes and 
    assings these values to corresponding payload `obj:dict` variables.

    Args::

    page_data (`class:lxml.html`): Represents an pre intialized instance of html tree object.
    name (`class:str`): Value of `name` attribute of a specific html element.
    payload (`class:dict`): Essential data to use in request payload or request body.

    Raises:

    ValueError: If payload values are same already.
    '''
    try:
        if page_data is not None:
            items = page_data.xpath('//input[@name="' + name +
                            '" and @type="hidden"]/@value')
            for item in items:
                try:
                    if payload[name] != item:
                        payload[name] = item
                        return
                    else:
                        raise ValueError("Attribute {} Value is SAME!".format(name))
                except ValueError as error:
                    print('Error: ' + error)
        else:
            raise ValueError("page_data is NoneType")
    except ValueError as e:
        print("Method: attrGetter | Error: {}".format(e))


def tokenGetter(page_data, token_list, payload):
    '''
    It will extract value of a specific html element from html tree `obj:lxml.html` and assign it to corresponding
    payload variable.

    Args::

    page_data (`class:lxml.html`): Represents an pre intialized instance of html tree object.
    token_list (`class:list`): List of specific element name attribute `class:str` which are gonna be extracted. 
    payload (`class:dict`): Essential data to use in request payload or request body.
    '''
    for item in token_list:
        t = threading.Thread(
        target=attrGetter,args=(page_data, item, payload))
        t.start()
        t.join()
    
    return


def homePage(reg_num,ums_pass):
    '''
    It will return UMS Homepage Account Data as an html tree `obj:lxml.html` 
    by creating instance of `class:verto`.

    Attributes::
    reg_num (`obj:str`): Registration Number of UMS.
    ums_pass (`obj:str`): Password of UMS.
    sess (`class:requests.session`): Represents an  instance of session object in which all the requests are made.
    baseUrl (`obj:str`): Url of UMS.
    log1Token (`obj:dict`): Containes esseential variables to simulate login-first page request.
    logPayload (`obj:dict`): Containes those variable whose values are need to get extracted from UMS page itself.
    
    '''
    sess = requests.session()
    user = Verto(reg_num,ums_pass, sess)
    homeData = getRequest(sess, user.baseUrl)
    tokenGetter(homeData, user.log1Token, user.logPayload)
    user.tokenSetter(1)
    homeData = postRequest(sess, user.baseUrl, user.logPayload)
    tokenGetter(homeData, user.log1Token, user.logPayload)
    user.tokenSetter(2)
    try:
        homeData = postRequest(sess, user.baseUrl, user.logPayload)
        titleElem = (homeData.xpath("//head[@id='ctl00_Head1']/title/text()"))
        titleElem = ('').join(titleElem)
        titleElem = titleElem.strip("\r\n")
        titleElem = titleElem.strip()
        if titleElem == 'UMS - Home':
            return homeData
        else:
            raise ValueError("Error in retrieving UMS Homepage Data.")
    except ValueError as e:
        print('Method: homePage | {}'.format(e))
        return None

        

def mesgData(page_data):
    '''
    This Method will instantiate a Messages instance and fetch the messages in a `obj:list` list.
    
    Args::

    page_data (`class:lxml.html`): Represents an pre intialized instance of html tree object.
    '''
    userMsg = Messages(page_data)
    return userMsg.mesgList
    
