import requests
import threading
from lxml import html
from abc import ABCMeta,abstractmethod

class Base(object):
    '''
    Base Object for providing various essential methods.

    Args::

    session (`class:requests.session`): Represents an session object in which all the requests are made.
    base_url (`obj:str`): Url of UMS
    payload (`obj:dict`): Containes those variable whose values are need to get extracted from UMS page itself.
    token_list (`obj:dict`): Containes esseential variables to simulate login page request.

    '''

    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    def getRequest(self, session, base_url):
        '''
        It will return an html tree `obj:lxml.html` parsed by `class:lxml.html`.
        Http requests are made in `class:requests.session`.

        Args::

        session (`class:requests.session`): Represents an pre intialized instance of session object in which all the requests are made.
        base_url (`class:str`): Url to get fetched.

        '''
        homeData_response = session.get(base_url)
        homeData_tree = html.fromstring(homeData_response.content)
        return homeData_tree


    def postRequest(self, session, base_url, payload=None, upload_stream=None):
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
            tree = session.post(base_url, data=payload, files=upload_stream)
            if tree.status_code == 200:
                tree = html.fromstring(tree.content)
                return tree
            else: 
                raise ValueError("Something wrong with base_url or payload.")
        except ValueError as e:
            print('Method: postRequest | Error: {}'.format(e))
        


    def attrGetter(self, page_data, name, payload):
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
                        print('Error: ' + str(error))
            else:
                raise ValueError("page_data is NoneType")
        except ValueError as e:
            print("Method: attrGetter | Error: {}".format(e))


    def tokenGetter(self, page_data, token_list, payload):
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
            target=self.attrGetter,args=(page_data, item, payload))
            t.start()
            t.join()
        return

    @abstractmethod
    def initiater(self):
        '''
        Abstract Method to re-defined in other child class.
        It will be the main method of other class.
        '''
        pass
    
    #

        



'''
def pdfs():
    res = Homework()
    basePage = getRequest(sess,res.baseUrl)
    tokenList = list(res.varToken.keys())
    tokenList.remove('ctl00_RadScriptManager1_TSM')
    tokenGetter(basePage,tokenList,res.varToken)
    res.speToken(basePage)
    courseList = res.course(basePage)
    res.buttonToken(courseList['MEC107'])
    finalPage = sess.post(res.baseUrl,files=res.finalToken)
    finalPage = html.fromstring(finalPage.content)
    res.resourceGetter(finalPage)
    tokenGetter(finalPage,tokenList,res.varToken)
    res.speToken(finalPage)
    res.buttonToken(courseList['MEC107'],course_resources=1)
    n = sess.post(res.baseUrl,files=res.finalToken,stream =True)
    with open('output.pdf', 'wb') as target:
        n.raw.decode_content = True
        shutil.copyfileobj(n.raw, target)
    
'''     
    
    
