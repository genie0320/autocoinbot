from Final import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN: Final = '7175733572:AAGTLJb5kYQ0ltrkn7ANIz9jwC-l2MO4xSI'
BOT_USERNAME: Final = '@pyautocoinbot'

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(f'Hi {update.effective_user.first_name}!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(f'How can I help you')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(f'This is custom command!')


# Responses
    
def handle_response(text:str) -> str:
    Processed:str = text.lower()

    if 'hello' in text:
        return 'Hey there!'
    
    if 'time' in text:
        return f'The time is {datetime.now().strftime("%H:%M")}'
    
    if 'date' in text:
        return f'The date is {datetime.now().strftime("%d/%m/%Y")}'
    
    return 'I did not understand that!'
# 7175733572:AAGTLJb5kYQ0ltrkn7ANIz9jwC-l2MO4xSI
# pip install python-telegram-bot

# https://www.youtube.com/watch?v=vZtm1wuA2yc