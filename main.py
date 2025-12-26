import telebot

# আপনার আসল টোকেনটি নিচে বসানো হয়েছে
bot = telebot.TeleBot("8535484364:AAHA4qu20AR8i2k2C1Xwqoa8C43pdJ39Ghk")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "হ্যালো! আপনার বটটি এখন Render সার্ভারে সচল আছে।")

bot.polling()
