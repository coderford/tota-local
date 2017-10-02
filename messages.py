from lxml import html
import threading



class Messages:
    '''
    This class extract messages from `obj:lxml.tree` User's UMS Homepage Data Object 
    and returns all the messages in `obj:list` list.

    Attributes::

    mesgList (`obj:list`): Contains all the extracted messages.
    msgPth (`obj:list`): Containes xpath to those values are need to get extracted from UMS page itself.
    

    Args::
    
    page_data (`obj:lxml.html`): Represents an pre intialized instance of html tree object.
    data_xpath (`obj:list`): Containes xpath to those values are need to get extracted from UMS page itself.
    data_category (`obj:int`): It will determine which html element is need to extract 
    Raises:
        ValueError: If page_num is not an acceptable int.
    '''
    def __init__(self,page_data):
        self.mesgList = ['','','','','','','','','']
        self.msgPath = ['//div[@id ="owl-demo"]/div/div[@class="Announcement_Subject"]/text()',
                            '//div[@id ="owl-demo"]/div/div[@class="Announcement_Name"]/text()',
                            '//div[@id ="owl-demo"]/div/div/div[@class="Announcement"]/text()']
        self.msgExtractor(page_data,self.msgPath)
    
    
    def dataExtractor(self,page_data,data_xpath,data_category):
        '''
        This method will extract html elements from a pre html tree `obj:lxml.html` obj.
        '''
        items = page_data.xpath(data_xpath)
        if data_category == 0:
            for i,item in enumerate(items):
                item = item.strip("\r\n")
                item = item.strip()
                self.mesgList[i] = [item,'','']

        elif data_category == 1:
            for j,item in enumerate(items):
                item = item.strip("\r\n")
                item = item.strip()
                self.mesgList[j][1] = 'By: '+ item
        elif data_category == 2:
            for k,item in enumerate(items):
                item = item.strip("\r\n")
                item = item.strip()
                self.mesgList[k][2] = item
                

    def msgExtractor(self,page_data,data_xpath):
        '''
        This method will extract html elements from a pre html tree `obj:lxml.html` obj
        '''
        for index,item in enumerate(data_xpath):
            threads = threading.Thread(
                target=self.dataExtractor, args=(page_data, item,index))
            threads.start()
            threads.join()
        return None

    