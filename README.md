# kitchen-compass
This is a Telegram bot to help you plan your meals for the week.

- The bot will suggest by 2 recipes for 2 people with a calorie count of appox 700kcal each.
- You can request modifications to the plan for example asking for a different number of recipes, portions, kcal, specific ingredients, or simply changing the recipe alltogether.
- You can also request to generate a list of groceries from the proposed recipes.
- You can interact with the bot via text or voice message.

## Build and run the app with Docker
`docker build -t kitchen_compass --build-arg openaiapikey=$OPENAI_API_KEY --build-arg telegramapikey=$KITCHEN_COMPASS_TELEGRAM_BOT_TOKEN .`

## Dependencies 
- [Python Telegram Bot](https://docs.python-telegram-bot.org/en/stable/index.html)
- [OpenAI Python Library](https://platform.openai.com/docs/libraries/python-library)
- [Whisper](https://platform.openai.com/docs/tutorials/meeting-minutes/transcribing-audio-with-whisper)
- [Docker's Python guide](https://docs.docker.com/language/python/)

## Disclaimer
Please note that the recipes are AI generated and the content is not verified.
