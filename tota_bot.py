import logging
import re
import threading
from redis import StrictRedis
from telegram.ext.dispatcher import run_async
from telegram import ReplyKeyboardMarkup
from telegram.error import NetworkError, TelegramError, Unauthorized
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, RegexHandler, Updater, JobQueue)
from telegram import Update
import telegram
import tota as mainf

CHOOSING, TYPING_REPLY, TYPING_CHOICE, LOAD = range(4)
reply_keyboared_setup = [['Username', 'Password']]
reply_keyboared_options = [['Messages']]
markup_setup = ReplyKeyboardMarkup(reply_keyboared_setup, one_time_keyboard = True)
markup_options = ReplyKeyboardMarkup(reply_keyboared_options,one_time_keyboard=False)



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
            if chat_id in l:
                update.message.reply_text("Exists")
                return
            else:
                    r.hmset(chat_id,data)
                    update.message.reply_text(
                        "Hi Dear, WhatsUP!\n\n"
                        "I hope you are fine. My name is ToTa. "
                        "I am your personal bot to handle your daily tedious tasks of UMS. "
                        "Like updating you about new messages, announcements, lecture pdf's, fee statements, marks, and other features of UMS. "
                        "\n\nI am created by **Shekh Ataul**.\nA.K.A -- DEVIL!"
                        "\n\nTo Get Started Enter Command: \n/setup"
                        )
                    return 
        return
    
@run_async   
def setup(bot, update):
    update.message.reply_text(
        "First Time Setup:"
        "\n\nYou have to enter your Registration Number and UMS Password to use me.",
        reply_markup = markup_setup)
    return CHOOSING
@run_async
def user_choice(bot, update, user_data):
    text = update.message.text
    user_data['choice'] = text
    update.message.reply_text('Enter your %s(UMS):' % text)
    return TYPING_REPLY
@run_async
def received_information(bot, update, user_data):
    p = StrictRedis()
    text = update.message.text
    reg_pattern = re.compile(r"^[0-9]*$")
    category = user_data['choice']
    if (category == 'Username'):
        if (re.match(reg_pattern, text)and len(text) <= 8):
            user_data[category] = text
            lock = threading.Lock()
            with lock:
                p.hset(update.message.chat_id,'umsReg',text)
                del user_data['choice']
                update.message.reply_text(
                    "Now click on Password(UMS)",
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
            update.message.reply_text("Thanks for entering Password!"
            "Enter Command: \n/load")
            return LOAD
@run_async
def loadData(bot,update):
    c = StrictRedis()
    chat_id = update.message.chat_id
    regNumber = c.hget(chat_id,'umsReg')
    umsPass = c.hget(chat_id,'umsPass')
    count=0
    try:
        homeTree = mainf.homePage(regNumber,umsPass)
        if homeTree != None:
            msgList = mainf.mesgData(homeTree)
            for i,item in enumerate(msgList):
                if item != '':
                    item = ('|').join(item)
                    c.hset(chat_id,'msg'+str(i),item)


            
        else:
            update.message.reply_text('Something Went Wrong')
            raise ValueError("Something Went Wrong")
        
    except ValueError as error:
        update.message.reply_text("Error : %s"% error)
    
    update.message.reply_text("All set, Now what you want to know about?",reply_markup=markup_options)
    return 

def dataUpdater(bot,job):
        c = StrictRedis()
        for v in c.keys():
            chat_id = v
            regNumber = c.hget(chat_id,'umsReg')
            umsPass = c.hget(chat_id,'umsPass')
            count=0
            try:
                homeTree = mainf.homePage(regNumber,umsPass)
                if homeTree != None:
                    msgList = mainf.mesgData(homeTree)
                    for i,item in enumerate(msgList):
                        if item != '':
                            item = ('|').join(item)
                            if item == c.hget(chat_id,'msg'+str(i)):
                                bot.send_message(chat_id=chat_id,text="Repeating...")
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
def messages(bot,update):
    chat_id = update.message.chat_id
    d = StrictRedis()
    l = sorted(d.hkeys(chat_id))
    for i,item in enumerate(l):
        if(item == 'msg'+str(i) and (d.hget(chat_id,'msg'+str(i)) != '')):
            k =  d.hget(chat_id,'msg'+str(i))
            lock = threading.Lock()
            with lock:
                annc_sub,annc_by,annc_body = k.split('|')
                update.message.reply_text(annc_sub+'\n\n'+annc_by+'\n\n'+annc_body)
        
def main():
    
    updater = Updater(token = '409921301:AAEENBR4R283_Vxo-yIyfOgvpUp5Gu0SFzI')
    dp = updater.dispatcher
    start_handler = CommandHandler('start',start)
    msg_handler = MessageHandler(Filters.text,messages)
    conv_handler = ConversationHandler(
        entry_points = [CommandHandler('setup', setup)],
        states =  {
            CHOOSING:[RegexHandler('^(Username|Password)$', user_choice,
                                    pass_user_data = True)],
            TYPING_CHOICE:[MessageHandler(Filters.text, user_choice,
                                        pass_user_data = True)],
            TYPING_REPLY:[MessageHandler(Filters.text,
                                            received_information,
                                            pass_user_data = True)],
            LOAD: [CommandHandler('load', loadData)],
        
        },
        fallbacks = [])
    dp.add_handler(conv_handler)
    dp.add_handler(msg_handler)
    dp.add_handler(start_handler)
    updater.start_polling()
    j = updater.job_queue
    j.run_repeating(dataUpdater,interval=60,first=60)
    return

main()

