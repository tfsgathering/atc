import datetime


def nowtime():
    return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


async def send_log(bot, emoji, content):
    try:
        log_channel = bot.get_channel(bot.logchannel)

        if log_channel:
            logmsg = f"{emoji} `{nowtime()}`\n{content}"
            await log_channel.send(logmsg)

    except Exception:
        pass