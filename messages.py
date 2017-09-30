from lxml import html
import threading



class Messages:
    def __init__(self,page_data):
        self.mesgList = ['','','','','','','','','']
        self.anncPath = ['//div[@id ="owl-demo"]/div/div[@class="Announcement_Subject"]/text()',
                            '//div[@id ="owl-demo"]/div/div[@class="Announcement_Name"]/text()',
                            '//div[@id ="owl-demo"]/div/div/div[@class="Announcement"]/text()']
        self.anncExtractor(page_data,self.anncPath)
    
    
    def dataExtractor(self,page_data,data_xpath,data_category):
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
                

    def anncExtractor(self,page_data,data_category_list):
    
        for index,item in enumerate(data_category_list):
            threads = threading.Thread(
                target=self.dataExtractor, args=(page_data, item,index))
            threads.start()
            threads.join()
        return None

    