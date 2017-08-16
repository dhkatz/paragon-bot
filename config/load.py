# LOAD BOT CONFIGURATION
try:
    from config.config import __token__, __prefix__, __ownerid__, __cleverbot__, __reddit__
except ImportError:
    import os

    __token__ = os.environ.get(' DISCORD_TOKEN ')
    __prefix__ = os.environ.get(' DISCORD_PREFIX ')
    __ownerid__ = os.environ.get(' DISCORD_OWNERID ')
    __cleverbot__ = os.environ.get(' CLEVERBOT_API ')
    __reddit__ = os.environ.get(' REDDIT_LOGIN ')
# LOAD BOT MODULES
from config.config import __cogs__
