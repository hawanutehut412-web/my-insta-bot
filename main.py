import telebot
from telebot import types
import random
import os
import json

# আপনার বটের API টোকেন
API_TOKEN = '8484828745:AAGWVI1cLifDzNRzOE3KYCSQpOeEg4jW1Hw'
bot = telebot.TeleBot(API_TOKEN)

# আপনার অ্যাডমিন আইডি
ADMIN_ID = 7575034636 

DB_FILE = "users_db.json"
USED_NAMES_FILE = "used_names.txt"
REG_RATE = 6.50 

# নামের তালিকা
all_names = ["Norberto", "Julian", "Santiago", "Leonardo", "Matthias", "Sebastian", "Adrian", "Dominic", "Fabian", "Lorenzo", "Xavier", "Marco", "Silas", "Maxwell", "Damian", "Arlo", "Ryker", "Jasper", "Atlas", "Brooks", "Gideon", "Enzo", "Beau", "Jude", "Cassian", "Milo", "Ezra", "Felix", "Oscar", "Theo", "Hugo", "Otis", "Arthur", "Leo", "Finn", "Kai", "Axel", "Roman", "Luca", "Nico", "Ivan", "Erik", "Odin", "Zane", "Troy", "Zeke", "Jace", "Kaleb"]

# ডাটাবেস ফাংশন
def load_db():
    if not os.path.exists(DB_FILE): return {}
    with open(DB_FILE, "r") as f: return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

def load_used_names():
    if not os.path.exists(USED_NAMES_FILE): return set()
    with open(USED_NAMES_FILE, "r") as f: return set(line.strip() for line in f)

def save_used_name(name):
    with open(USED_NAMES_FILE, "a") as f: f.write(name + "\n")

user_temp_data = {}
withdraw_temp = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("➕ Register a new account", "💰 Balance", "📤 Withdraw", "👤 Profile", "💬 Help")
    bot.send_message(message.chat.id, "বট সচল আছে। নিচের মেনু ব্যবহার করুন:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_menu_clicks(message):
    chat_id = message.chat.id
    if message.text == "➕ Register a new account":
        used_names = load_used_names()
        available_names = [n for n in all_names if n not in used_names]
        if not available_names:
            bot.send_message(chat_id, "⚠️ সব নাম ব্যবহৃত হয়ে গেছে!")
            return
        selected_name = random.choice(available_names)
        save_used_name(selected_name)
        gender = random.choice(["Male", "Female"])
        reg_text = f"📝 **Register account using the specified data and get {REG_RATE} BDT**\n\n👤 **First name:** {selected_name}\n👤 **Last name:** ✖️\n🚻 **Gender:** {gender}\n\n🔐 *Be sure to use the specified data.*"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Done ➡", callback_data="start_reg_steps"))
        bot.send_message(chat_id, reg_text, parse_mode="Markdown", reply_markup=markup)

    elif message.text == "💰 Balance":
        db = load_db()
        bal = db.get(str(chat_id), 0.0)
        bot.send_message(chat_id, f"💵 আপনার বর্তমান ব্যালেন্স: {bal:.2f} টাকা।")

    elif message.text == "👤 Profile":
        bot.send_message(chat_id, f"👤 **Your Profile:**\n\n📛 Name: {message.from_user.first_name}\nℹ️ ID: `{message.from_user.id}`", parse_mode="Markdown")

    elif message.text == "📤 Withdraw":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("bKash", callback_data="w_bkash"),
                   types.InlineKeyboardButton("Nagad", callback_data="w_nagad"))
        bot.send_message(chat_id, "টাকা তোলার পদ্ধতি বেছে নিন:", reply_markup=markup)

# --- Withdraw প্রসেস ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("w_"))
def withdraw_req(call):
    method = "bKash" if "bkash" in call.data else "Nagad"
    withdraw_temp[call.message.chat.id] = {'method': method}
    msg = bot.send_message(call.message.chat.id, f"Please your {method} number:")
    bot.register_next_step_handler(msg, get_withdraw_amount)

def get_withdraw_amount(message):
    withdraw_temp[message.chat.id]['number'] = message.text
    bot.send_message(message.chat.id, "Please your amount:")
    bot.register_next_step_handler(message, check_balance_and_finish)

def check_balance_and_finish(message):
    chat_id = message.chat.id
    try:
        requested_amount = float(message.text)
    except ValueError:
        bot.send_message(chat_id, "ভুল ইনপুট! দয়া করে সঠিক সংখ্যা লিখুন।")
        return

    db = load_db()
    current_balance = db.get(str(chat_id), 0.0)

    if requested_amount > current_balance:
        bot.send_message(chat_id, "আপনার একাউন্টে পর্যাপ্ত পরিমাপে ব্যালেন্স নাই পরে আবার চেষ্টা করুন।")
    else:
        # ব্যালেন্স থেকে টাকা কেটে নেওয়া (ঐচ্ছিক, আপনি চাইলে পরে অ্যাডমিন এপ্রুভালের সময়ও কাটতে পারেন)
        # এখানে শুধু অ্যাডমিনকে রিকোয়েস্ট পাঠানো হচ্ছে
        data = withdraw_temp.get(chat_id)
        bot.send_message(chat_id, "The admin will complete your payment shortly.")
        
        admin_msg = (f"🏧 **Withdraw Request!**\n"
                     f"👤 User: {message.from_user.first_name}\n"
                     f"🆔 ID: `{chat_id}`\n"
                     f"💰 Amount: {requested_amount} BDT\n"
                     f"📱 Method: {data['method']}\n"
                     f"📞 Number: `{data['number']}`")
        bot.send_message(ADMIN_ID, admin_msg)
    
    if chat_id in withdraw_temp: del withdraw_temp[chat_id]

# --- রেজিস্ট্রেশন ধাপগুলো (আগের মতই) ---
@bot.callback_query_handler(func=lambda call: call.data == "start_reg_steps")
def step1_webmail(call):
    msg = bot.send_message(call.message.chat.id, "📧 Please send your Webmail:")
    bot.register_next_step_handler(msg, step2_password)

def step2_password(message):
    user_temp_data[message.chat.id] = {'webmail': message.text}
    msg = bot.send_message(message.chat.id, "🔐 Please send your Password:")
    bot.register_next_step_handler(msg, step3_userid)

def step3_userid(message):
    user_temp_data[message.chat.id]['pass'] = message.text
    msg = bot.send_message(message.chat.id, "🆔 Please send your User ID:")
    bot.register_next_step_handler(msg, step4_2fa)

def step4_2fa(message):
    user_temp_data[message.chat.id]['userid'] = message.text
    msg = bot.send_message(message.chat.id, "🔐 Please send your 2Fa Key:")
    bot.register_next_step_handler(msg, final_submit)

def final_submit(message):
    chat_id = message.chat.id
    two_fa = message.text
    data = user_temp_data.get(chat_id)
    if data:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Approve", callback_data=f"appv_{chat_id}"))
        report = f"📩 **New Submission!**\n\n📧 Webmail: `{data['webmail']}`\n🔐 Pass: `{data['pass']}`\n🆔 User ID: `{data['userid']}`\n🔑 2FA Key: `{two_fa}`\n👤 User: {message.from_user.first_name} | ID: `{chat_id}`"
        bot.send_message(ADMIN_ID, report, parse_mode="Markdown", reply_markup=markup)
        bot.send_message(chat_id, "✅ **সফলভাবে জমা হয়েছে!**\n\nআপনার একাউন্টটি বর্তমানে **৪৮ ঘণ্টার জন্য রিভিউতে** রয়েছে। সফলভাবে যাচাই শেষে আপনার ব্যালেন্স যুক্ত হবে।", parse_mode="Markdown")
        del user_temp_data[chat_id]

@bot.callback_query_handler(func=lambda call: call.data.startswith("appv_"))
def admin_approve(call):
    if call.from_user.id != ADMIN_ID: return
    target_id = call.data.split("_")[1]
    db = load_db()
    db[target_id] = db.get(target_id, 0.0) + REG_RATE
    save_db(db)
    bot.answer_callback_query(call.id, "এপ্রুভ করা হয়েছে!")
    bot.send_message(target_id, f"🎉 অভিনন্দন! আপনার কাজ এপ্রুভ হয়েছে এবং {REG_RATE} টাকা ব্যালেন্সে যোগ করা হয়েছে।")
    bot.edit_message_text(f"✅ ইউজার {target_id}-এর কাজ এপ্রুভ করা হয়েছে।", chat_id=ADMIN_ID, message_id=call.message.message_id)

bot.polling(none_stop=True)
