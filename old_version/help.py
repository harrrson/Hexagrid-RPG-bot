import discord

__modules={'roll','cc','session'}

__main_help="Main help text"
__roll_help="Roll module help"
async def init(message:discord.Message,command):
    message_text=''
    try:
        if command[0] not in __modules:
            message_text=__main_help
        elif command[0]=='roll':
            message_text=__roll_help
    except IndexError:
        message_text=__main_help

    await message.channel.send(message_text)