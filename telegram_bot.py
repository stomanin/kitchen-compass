import os
import logging
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

# Telegram Bot token from BotFather
TOKEN = os.getenv('KITCHEN_COMPASS_TELEGRAM_BOT_TOKEN')

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

# OPENAI token and configs
MODEL = "gpt-3.5-turbo"
TEMPERATURE = 0 #degree of randomness of the model's output

def get_completion_from_messages(messages, model=MODEL, temperature=TEMPERATURE):
    response = client.chat.completions.create(model=model,messages=messages,temperature=temperature)
    return response.choices[0].message.content

def save_context_get_response(text):
    #adds the user input to the context with user role
    messages.append({'role':'user', 'content':f"{text}"})
    #gets the response
    response = get_completion_from_messages(messages) 
    print(response)
    #saves the context for history
    messages.append({'role':'assistant', 'content':f"{response}"})
    print(messages)
    return response

# system instructions
from prompt import system_instructions
messages =  []
messages.append({'role':'system', 'content':f"{system_instructions}"})

# setting up logging module, to know when (and why) things don't work as expected
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# start function called every time the Bot receives a Telegram message that contains the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.is_bot == False:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Hello, I'm your KitchenCompass bot 👩‍🍳, I am here to help plan your meals for the week! 🍽!\
            \n \n⌛ Hold on a few moments until I prepare a meal plan for you. ⌛\
            \n \nI will propose 2 recipes 📋 for 2 people 👯 with a calorie count of appox 700kcal per portion."
        )
        
        responses = get_completion_from_messages(messages)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=responses)

async def audio_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("audio handler")
    if update.message.from_user.is_bot == False:
        if update.message.voice:
            file_id = update.message.voice.file_id
            # download file
            file = await context.bot.get_file(file_id)
            await file.download_to_drive(f"downloaded_audio_{file_id}.ogg")  # You can specify the desired file name
            
            # use whisper to transcribe audio messages
            from openai import OpenAI
            client = OpenAI()

            with open(f"downloaded_audio_{file_id}.ogg", 'rb') as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file,
                    response_format="text"
                )
            print(transcription)
            # delete downloaded audio file after the transcription is done
            os.remove(f"downloaded_audio_{file_id}.ogg")
            
            response = save_context_get_response(transcription)

            #returns the response
            await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

# triggers the openai bot 
async def chatgptbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.is_bot == False:
        response = save_context_get_response(update.message.text)
        #returns the response
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    # /start command handler
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    #prompt handler
    prompt_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), chatgptbot)    
    application.add_handler(prompt_handler)

    #audio handler
    audio_handler_instance = MessageHandler(filters.VOICE, audio_handler)
    application.add_handler(audio_handler_instance)

    application.run_polling()