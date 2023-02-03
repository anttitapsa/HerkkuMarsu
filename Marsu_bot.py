'''
This is bot utilised for Inkubios credits system. 
Bot saves the amount of money user have into csv file after buying treats or adding money.

Token got from BotFather should be saved in config.txt file. The program parses the TOKEN 
automaticly form config.txt file 
'''

import reader_writer
import configparser
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler

CHOOSE, TREATS, CREDITS, SLEEP = range(4)
TOKEN = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Starts the ConversationHandler.
    Returns the state CHOOSE, which activates the function choose
    '''
    name = update.message.from_user.first_name
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Hei {name},\nolen HerkkuMarsu ja vastaan namupalvelun tileistä.\nValitse jokin alla olevista toiminnoista.",
        reply_markup=main_menu_keyboard()
    )

    return CHOOSE

async def choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Function checks if the user is in csv file. If not, user is added into the file.

    The function returns state based on the message sent to bot.
    '''
    message =  update.message.text 
    user = update.message.from_user.username
    if reader_writer.find_user(user) == False:
        reader_writer.add_user(user)

    if message == "Osta Herkkuja":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Kuinka paljon rahaa haluat käyttää rahaa (max. 20 euroa)?\n\nKatso jääkaapin ovesta haluamasi tuotteen hinta ja lähtä käyttämäsi rahasumma. Käytäthän desimaaleissa pistettä (.) ja enimmillää kahta (2) desimaalia. Huomaathan, että tilisi ei saa mennä miinukselle.",
            reply_markup=ReplyKeyboardRemove()
        )
        return TREATS

    elif message == "Lisää rahaa":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Kuinka paljon haluat lisätä rahaa tilillesi (max. 20 euroa)?\n\nTipauta siniseen kassalippaaseen niin monta euroa kuin uskot lähiaikoina tarvitsevasi ja kerro tämä rahasumma minulle. Käytäthän desimaaleissa pistettä (.) ja enimmillää kahta (2) desimaalia.",
            reply_markup=ReplyKeyboardRemove()
        )
        return CREDITS

    elif message == "Tarkista kreditit":
        amount = reader_writer.check_money(user)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Tililläsi on {amount} euroa.",
            reply_markup=main_menu_keyboard()
        )
    
    elif message == "END":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Menen nukkumaan. Jos haluat herättää minut, lähetä komento start.\nZZZZZZZZZZZ...",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
       
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    If the message is number between 0-20 with or without max 2 decimals (decimal 2 can only be 0 or 5),
    function is called.

    The amount user give is subtracted form their money in csv file. If the money would go negative,
    bot don't allow buying. 
    '''
    message =  update.message.text
    user = update.message.from_user.username
    amount = reader_writer.use_money(user, message)
    if amount < 0:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text= f"Sinulla ei ole tarpeeksi rahaa. Tarvitset vielä {-amount} euroa.\n\nLISÄÄ RAHAA TILILLESI ENNEN OSTOA!",
            reply_markup=main_menu_keyboard()
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text= f"Käytit {message} euroa! Tililläsi on tällä hetkellä {amount} euroa.",
            reply_markup=main_menu_keyboard()
        )
    return CHOOSE

async def add_credits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    If the message is number between 0-20 with or without max 2 decimals (decimal 2 can only be 0 or 5),
    function is called.

    The amount user give is added to their money in csv file.
    '''
    message =  update.message.text
    user = update.message.from_user.username
    amount = reader_writer.add_money(user, message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text= f"Lisäsit tilillesi {message} euroa! Tililläsi on tällä hetkellä {amount} euroa.",
        reply_markup=main_menu_keyboard()
    )
    return CHOOSE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Function returns the state CHOOSE (main menu) if user send message
    which is not recognised by bot. 
    '''
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text = "Jokin meni pieleen. Käytithän pistettä (.) desimaaliluvuissa? Koititko lisätä tai käyttää enemmän kuin 20 euroa. Valitse alla olevista toiminnoista.",
        reply_markup=main_menu_keyboard()
    )
    return CHOOSE

##########Keyboards##########

# The Keybord utlised for commanding the bot

def main_menu_keyboard():
  keyboard = [[KeyboardButton('Osta Herkkuja')],
              [KeyboardButton('Lisää rahaa')],
              [KeyboardButton('Tarkista kreditit')],
              [KeyboardButton('END')]]
  return ReplyKeyboardMarkup(keyboard)

##########MAIN############

def main():
    # Token got from BotFather should be saved in config.txt file 
    # The program parses the TOKEN automaticly form config.txt file 

    config = configparser.ConfigParser()
    config.read('config.txt')
    TOKEN = config["TOKEN"]["telegram_bot_token"]

    money_filter = filters.Regex("^(?:([2][0])(?:\.0)?|[1][0-9](?:\.([0-9]|[0-9][0,5]))?|[1-9](?:\.([0-9]|[0-9][0,5]))?|0?\.([0-9]|[0-9][0,5]))$") 
    application = ApplicationBuilder().token(TOKEN).build()

    # Handler for the conversation 
    # Handler is activated with /start command
    # If the message is Osta Herkkuja or Lisää rahaa or Tarkista kreditit or END, then
    # the choose-function is called
    #
    # If END is called, the conversationHander is closed
    conv_handler = ConversationHandler(
                                        entry_points= [CommandHandler('start', start)],
                                        states={CHOOSE: [MessageHandler(filters.Regex("^(Osta Herkkuja|Lisää rahaa|Tarkista kreditit|END)$"), choose)],
                                                TREATS: [MessageHandler(money_filter, buy)],
                                                CREDITS: [MessageHandler(money_filter, add_credits)],
                                        },
                                        fallbacks= [MessageHandler(filters.TEXT, cancel)]
                                    )   
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()