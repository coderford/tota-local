import logging
import re
import threading
from redis import StrictRedis
from telegram.ext.dispatcher import run_async
from telegram import InlineKeyboardButton as ikb
from telegram import InlineKeyboardMarkup as ikm
from telegram.error import NetworkError, TelegramError, Unauthorized
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          CallbackQueryHandler, MessageHandler, Updater, JobQueue)
from telegram import Update, ChatAction
import telegram
from user import Verto
from message import Message
from assingment import Resources
from multiprocessing import Pool


CHOOSING, TYPING_REPLY, TYPING_CHOICE, LOAD = range(4)
reply_keyboared_setup = [[ikb('Reg. Number',callback_data='Reg. Number'), ikb('Password',callback_data='Password')]]
reply_keyboared_options = [[ikb('Messages',callback_data='Messages'),ikb('Resources',callback_data='Resources')]]
markup_setup = ikm(reply_keyboared_setup)
markup_options = ikm(reply_keyboared_options)



logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
@run_async
def start(bot, update):
    r = StrictRedis()
   
    data = {'umsReg':'','umsPass':'','msg0':'','msg1':'','msg2':'','msg3':'','msg4':'','msg5':'','msg6':'','msg7':'','msg8':''}
    l = r.keys()
    
    def msgDispatcher():
        lock = threading.Lock()
        with lock:
            chat_id = str(update.message.chat_id)
            if (chat_id in l) and (r.hget(chat_id,'umsReg')) and (r.hget(chat_id,'umsPass')):
                update.message.reply_text('Welcome Back!',reply_markup = markup_options)
                return
            else:
                    r.hmset(chat_id,data)
                    update.message.reply_text(
                        "Hi Dear\n\n"
                        "I hope you are fine. My name is ToTa. "
                        "I am your personal bot to handle your daily tedious tasks of UMS. "
                        "\n\nI am created by Shekh Ataul.\nA.K.A -- DEVIL!"
                        "\n\nTo Get Started Press: Setup",
                        reply_markup = ikm([[ikb('Setup',callback_data='setup')]]))
                    return
    msgDispatcher()
    return
    
@run_async   
def setup(bot, update):
    query = update.callback_query
    bot.send_chat_action(chat_id=query.message.chat_id, action=ChatAction.TYPING)
    bot.edit_message_text(text="First Time Setup: \n\nYou have to enter your Registration Number and UMS Password to use me.",
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        reply_markup = markup_setup)    
    return CHOOSING
@run_async
def user_choice(bot, update, user_data):
    query = update.callback_query
    bot.send_chat_action(chat_id=query.message.chat_id, action=ChatAction.TYPING)
    user_data['choice'] = query.data
    bot.edit_message_text(text="Enter your %s" % query.data,
                     chat_id=query.message.chat_id,
                     message_id=query.message.message_id)
    return TYPING_REPLY
@run_async
def received_information(bot, update, user_data):
    p = StrictRedis()
    text = update.message.text
    reg_pattern = re.compile(r"^[0-9]*$")
    category = user_data['choice']
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    if (category == 'Reg. Number'):
        if (re.match(reg_pattern, text)and len(text) <= 8):
            user_data[category] = text
            lock = threading.Lock()
            with lock:
                p.hset(update.message.chat_id,'umsReg',text)
                del user_data['choice']
                update.message.reply_text(
                    "Now click on Password",
                    reply_markup = markup_setup)
                return CHOOSING
        else:
            update.message.reply_text(
                "Please enter a valid %s!" % user_data['choice'])
        return CHOOSING
    else:
        user_data[category] = text
        lock1 = threading.Lock()
        with lock1:
            p.hset(update.message.chat_id,'umsPass',text)
            del user_data['choice']
            update.message.reply_text("Thanks for entering Password!",
            reply_markup=ikm([[ikb('Load Data',callback_data='load')]]))
            return LOAD
@run_async
def loadData(bot,update):
    c = StrictRedis()
    query = update.callback_query
    chat_id = query.message.chat_id
    regNumber = c.hget(chat_id,'umsReg')
    umsPass = c.hget(chat_id,'umsPass')
    count=0
    bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    try:
        homeUms = Verto(regNumber,umsPass)
        homeData = homeUms.initiater()
        if homeData != 'Incorrect Credentials':
            pass
        else:
            bot.edit_message_text(text='Incorrect Credentials',
                                chat_id=chat_id,
                                message_id=query.message.message_id)
            raise ValueError("Something Went Wrong")   
    except ValueError as error:
        return
    else:
        def msg():
                msgUms = Message(homeData)
                msgList = msgUms.initiater()
                no_msg = 0
                for i, item in enumerate(msgList):
                    if item != '':
                        no_msg = no_msg + 1
                        item = ('|').join(item)
                        c.hset(chat_id,'msg'+str(i),item)
                c.hset(chat_id,'#msg',str(no_msg))

        def course():
            courseRes = Resources(homeUms.session)
            courseList = courseRes.course_codes()
            c.hset(chat_id,'#course',str(len(courseList)))
            for i,item in enumerate(courseList):
                c.hset(chat_id,'c{}'.format(i),item)
        msg()
        pool = Pool(4)
        p1 = pool.Process(target=course)
        p1.start()
        p1.join()
        bot.edit_message_text(text="All set, Now what you want to know about?",
        chat_id=chat_id,message_id=query.message.message_id,
        reply_markup=markup_options)
        
    return

def dataUpdater(bot,job):
        c = StrictRedis()
        for v in c.keys():
            chat_id = v
            regNumber = c.hget(chat_id,'umsReg')
            umsPass = c.hget(chat_id,'umsPass')
            count=0
            try:
                homeUms = Verto(regNumber,umsPass)
                homeData = homeUms.initiater()
                if homeData != None:
                    msgUms = Message(homeData)
                    msgList = msgUms.initiater()
                    for i,item in enumerate(msgList):
                        if item != '':
                            item = ('|').join(item)
                            if item == c.hget(chat_id,'msg'+str(i)):
                                pass
                            else:
                                lock = threading.Lock()
                                c.hset(chat_id,'msg'+str(i),item)
                                with lock:
                                    annc_sub,annc_by,annc_body = item.split('|')
                                    bot.send_message(chat_id=chat_id,text=annc_sub+'\n\n'+annc_by+'\n\n'+annc_body)
                    del msgList
                else:
                    update.message.reply_text('Something Went Wrong')
                    raise ValueError("Something Went Wrong")
            except ValueError as e:
                print('Error: '+str(e))
                           


@run_async
def options(bot,update):
    query = update.callback_query
    chat_id = query.message.chat_id
    d = StrictRedis()
    l = sorted(d.hkeys(chat_id))
    choice = query.data
    if choice == "Messages":
        counter = int(d.hget(chat_id,'#msg'))
        for i in range(0,counter):
                k =  d.hget(chat_id,'msg'+str(i))                
                annc_sub,annc_by,annc_body = k.split('|')
                if i == counter-1:
                    bot.send_message(text=annc_sub+'\n\n'+annc_by+'\n\n'+annc_body,chat_id=chat_id,reply_markup=markup_options)
                else:
                    bot.send_message(text=annc_sub+'\n\n'+annc_by+'\n\n'+annc_body,chat_id=chat_id)

        return
    elif choice == "Resources":
        num_courses = int(d.hget(chat_id,'#course'))
        course_markup = []
        temp = []
        t = []
        for i in range(0,num_courses,2):
            if i+1 < num_courses:
                course_markup.append([ikb('{}'.format(d.hget(chat_id,'c{}'.format(i))),callback_data='{}'.format(d.hget(chat_id,'c{}'.format(i)))),
                                    ikb('{}'.format(d.hget(chat_id,'c{}'.format(i+1))),callback_data='{}'.format(d.hget(chat_id,'c{}'.format(i+1))))])
            else:
                course_markup.append([ikb('{}'.format(d.hget(chat_id,'c{}'.format(i))),callback_data='{}'.format(d.hget(chat_id,'c{}'.format(i))))])
        bot.send_message(text="Choose Subject --",chat_id=chat_id,reply_markup=ikm(course_markup))
    
    else:
        update.message.reply_text("Sorry Wrong Input!")
        return
@run_async
def res(bot, update):
    c = StrictRedis()
    query = update.callback_query
    chat_id = query.message.chat_id
    course = query.data
    regNumber = c.hget(chat_id,'umsReg')
    umsPass = c.hget(chat_id,'umsPass')
    try:
        homeUms = Verto(regNumber,umsPass)
        homeData = homeUms.initiater()
        if homeData != 'Incorrect Credentials':
            pass
        else:
            bot.edit_message_text(text='Incorrect Credentials',
                                chat_id=chat_id,
                                message_id=query.message.message_id)
            raise ValueError("Something Went Wrong")   
    except ValueError as error:
        return
    else:
        courseIns = Resources(homeUms.session,course)
        resList = courseIns.reslist()
        for i,item in enumerate(resList):
            txt = item[-1]
            start = txt.find('$lblFileUplaodByTeacher')
            txt = txt[start-5:start]
            if item[2] == u'\xa0':
                item[2] = ''
            res_num_markup = ikm([[ikb('Download',callback_data='hot{}YinZ{}'.format(course,txt))]])
            text_data = 'Course - {}\n{} \n\n {}\n\n {}'.format(course,item[0],item[1].strip(),item[2].strip())
            bot.send_message(text=text_data,chat_id=chat_id,reply_markup=res_num_markup)
            x = '|'.join(item)
            c.hset(chat_id,'{}_{}'.format(course,item[-1]),x)
@run_async
def res_download(bot, update):
    c = StrictRedis()
    query = update.callback_query
    chat_id = query.message.chat_id
    temp = query.data
    n = temp.find('Z')
    value = temp[n+1:]
    n = temp.find('Y')
    course = temp[3:n]
    temp = '{}_ctl00$cphHeading$rgAssignment$ctl00${}$lblFileUplaodByTeacher'.format(course,value)
    
    res_data = c.hget(chat_id,temp)
    res_data = res_data.split('|')
    res_button = res_data[-1]
    regNumber = c.hget(chat_id,'umsReg')
    umsPass = c.hget(chat_id,'umsPass')
    try:
        homeUms = Verto(regNumber,umsPass)
        homeData = homeUms.initiater()
        if homeData != 'Incorrect Credentials':
            pass
        else:
            bot.edit_message_text(text='Incorrect Credentials',
                                chat_id=chat_id,
                                message_id=query.message.message_id)
            raise ValueError("Something Went Wrong")   
    except ValueError as error:
        return
    else:
        downInst = Resources(homeUms.session,course=course)
        lock = threading.Lock()
        with lock:
            down = downInst.initiater(res_button)
            bot.send_message(text = down,chat_id=chat_id)
            bot.send_document(chat_id=chat_id, document=open('{}'.format(down),'rb'))
    
def main():
    
    updater = Updater(token = '409921301:AAEENBR4R283_Vxo-yIyfOgvpUp5Gu0SFzI')
    dp = updater.dispatcher
    start_handler = CommandHandler('start',start)
    msg_handler = CallbackQueryHandler(options,pattern='^(Messages|Resources)$')
    res_handler = CallbackQueryHandler(res,pattern='[A-Z0-9]')
    res_down_handler = CallbackQueryHandler(res_download,pattern='^(hot)')
    conv_handler = ConversationHandler(
        entry_points = [CallbackQueryHandler(setup,pattern='^setup$')],
        states =  {
            CHOOSING:[CallbackQueryHandler(user_choice, pattern='^(Reg. Number|Password)$',
                                    pass_user_data=True)],
            #TYPING_CHOICE:[MessageHandler(Filters.text, user_choice,
                                        #pass_user_data = True)],
            TYPING_REPLY:[MessageHandler(Filters.text,
                                            received_information,
                                            pass_user_data = True)],
            LOAD: [CallbackQueryHandler(loadData,pattern='^load$')],
        
        },
        fallbacks = [])
    dp.add_handler(conv_handler)
    dp.add_handler(msg_handler)
    dp.add_handler(start_handler)
    dp.add_handler(res_handler)
    dp.add_handler(res_down_handler)
    updater.start_polling()

    j = updater.job_queue
    j.run_repeating(dataUpdater,interval=60,first=60)
    

main()

