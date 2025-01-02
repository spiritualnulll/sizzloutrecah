#       _         _             _       _ 
#   ___(_)_______| | ___  ___  | | ___ | |
#  / __| |_  /_  / |/ _ \/ __| | |/ _ \| |
#  \__ \ |/ / / /| |  __/\__ \_| | (_) | |
#  |___/_/___/___|_|\___||___(_)_|\___/|_|
# 
#           Backend Toolset
import asyncio
import yaml
import discord
import string
import random
from colorama import Fore, Style
# Load configuration from config.yaml
try:
    with open("config.yaml", "r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
except UnicodeDecodeError as e:
    print(f"{Fore.RED}[ᴇʀʀᴏʀ]{Fore.RESET} Error decoding config.yaml: {e}.  Please ensure your config file uses UTF-8 encoding.")
    exit(1) # Exit with an error code


class sizzles:
    class msg: # Message Tools 📧
        async def dev(self, message: str, type: int = "0"):
            for userid in list(config.get("OWNER_IDS")):
                user = self.bot.get_user(userid)
                #await user.send() #TBD -  This line needs further implementation.  What should be sent?
                try:
                    await user.send(message) #Attempt to send the message.
                except Exception as e:
                    print(f"Error sending message to {user}: {e}") #Handle potential errors.
    
    class prefix: # Prefix for logs 🤣
        info = f"{Fore.BLUE}[ɪɴꜰᴏ]{Fore.RESET}"
        warn = f"{Fore.YELLOW}[ᴡᴀʀɴ]"
        error = f"{Fore.RED}[ᴇʀʀᴏʀ]"
        heart = f"{Fore.MAGENTA}[<𝟥]{Fore.RESET}" 

    def hash(length: int = 8):
        """Generates a random alphanumeric code of specified length."""
        characters = string.ascii_letters + string.digits
        code = ''.join(random.choice(characters) for i in range(length))
        return code