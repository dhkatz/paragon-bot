# LOAD BOT CONFIGURATION
try:
    from config.config import __token__, __prefix__, __ownerid__
except ImportError:
    import os

    __token__ = os.environ.get(' DISCORD_TOKEN ')
    __prefix__ = os.environ.get(' DISCORD_PREFIX ')
    __ownerid__ = os.environ.get(' DISCORD_OWNERID ')

# LOAD BOT MODULES
from config.config import __cogs__
