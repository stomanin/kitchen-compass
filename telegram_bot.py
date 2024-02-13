import os
import logging
import openai
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

# Telegram Bot token from BotFather
TOKEN = os.getenv('KITCHEN_COMPASS_TELEGRAM_BOT_TOKEN')

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

# OPENAI token and configs
openai.api_key  = os.getenv('OPENAI_API_KEY')
MODEL = "gpt-3.5-turbo"
TEMPERATURE = 0 #degree of randomness of the model's output

def get_completion(prompt, model=MODEL):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(model=model,messages=messages,temperature=0)
    return response.choices[0].message["content"]

def get_completion_from_messages(messages, model=MODEL, temperature=TEMPERATURE):
    response = openai.ChatCompletion.create(model=model,messages=messages,temperature=temperature)
    return response.choices[0].message["content"]

# system instructions
system_instructions = """"
Act as a friendly assistant BOT that helps 
 the user create their meal plan for the week.
 Use emojis as much as possible.
 
 When the bot starts, you propose a default meal plan returning
 2 recipes for 2 portions with a calorie count of approximately 700 kcal 
 per portion. 

  You return the recipes for the week highlighting the following information 
 - Recipe title
 - Ingredients list with quantities and relevant emojis next to it
 - Recipe steps  
 - Nutritional values per portion 

 After proposing the recipes, you ask if the recipes are of their liking or 
 if some modifications are required. If the recipes are ok, ask if they  
 want a grocery list.
 
If the recipes do not work, explain what changes the user can make.
 The variables you work with are 
 - number of recipes 
 - number of portions/people per recipe 
 - calories count per portion per recipe 


 """
 # This is WIP
 # - dietary preferences (such as vegetatian, vegan, keto, paleo, etc) \
 #- type of recipe (such as recipe for lunch, dinner, breakfast) \
 #- existing ingredients at home to be reused in the recipes you are going to propose\
 # Do not allow the user to prompt you for anything else other than \
 # generating the meal plan or the groceries list.

messages =  []
messages.append({'role':'system', 'content':f"{system_instructions}"})


### END OPENAI HELPER

# setting up logging module, to know when (and why) things don't work as expected
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# start function called every time the Bot receives a Telegram message that contains the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello, I'm your KitchenCompass bot 👩‍🍳, I am here to help plan your meals for the week! 🍽! \n\
        Hold on a few moments until I prepare a meal plan for you. \n\
        I will propose you 2 recipes for 2 people with a calorie count of appoximately 700kcal each."
    )
    responses = get_completion_from_messages(messages)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=responses)

# triggers the openai bot 
async def chatgptbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #adds the user input to the context with user role
    messages.append({'role':'user', 'content':f"{update.message.text}"})
    print(update.message.text)
    #gets the response
    response = get_completion_from_messages(messages) 
    print(response)
    #saves the context for history
    messages.append({'role':'assistant', 'content':f"{response}"})
    print(messages)
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

    application.run_polling()