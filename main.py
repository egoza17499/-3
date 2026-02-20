# Main Bot Application

# This is the main application for the bot.

class Bot:
    def __init__(self):
        self.message_dispatcher = MessageDispatcher()

    def run(self):
        print('Bot is running...')

class MessageDispatcher:
    def dispatch(self, message):
        print(f'Dispatching message: {message}')

if __name__ == '__main__':
    bot = Bot()
    bot.run()