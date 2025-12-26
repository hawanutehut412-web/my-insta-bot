import telebot

# আপনার বট টোকেনটি এখানে দিন
bot = telebot.TeleBot("YOUR_BOT_TOKEN_HERE")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "আপনার বটটি এখন Render সার্ভারে ২৪ ঘণ্টা সচল আছে!")

bot.polling()
