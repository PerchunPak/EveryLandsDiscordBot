from discord.ext import commands
from discord import Intents, Status, Activity, ActivityType, Client

from datetime import datetime
from os import getpid
from traceback import format_exc

from yaml import safe_load
from re import match

# Токен бота
TOKEN = 'TOKEN_HERE'

bot_intents = Intents.default()
bot_intents.members = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned,
    description="EveryLands бот",
    case_insensitive=True,
    help_command=None,
    status=Status.invisible,
    intents=bot_intents,
    fetch_offline_members=True
)

bot.ready_for_commands = False


@bot.event
async def on_connect():
    print("\nУстановлено соеденение с дискордом")


@bot.event
async def on_ready():

    print('\nЗашел как:\n'
         f'{bot.user}\n'
         f'{bot.user.id}\n'
          '-----------------\n'
         f'{datetime.now().strftime("%X %d.%m.%Y")}\n'
          '-----------------\n'
         f'Шардов: {str(bot.shard_count)}\n'
         f'Серверов: {str(len(bot.guilds))}\n'
         f'Пользователей: {str(len(bot.users))}\n'
          '-----------------')

    bot.ready_for_commands = True
    bot.started_at = datetime.utcnow()
    bot.app_info = await bot.application_info()

    from base64 import b64decode
    await bot.change_presence(status=Status.online, activity=Activity(
        name=bytes(b64decode('0L/QtdGA0LXRhiDRgtC+0L8=')).decode("UTF-8"), type=ActivityType.playing))


@bot.event
async def on_message(message):
    if not bot.ready_for_commands: return

    EVERYLANDS_GUILD_ID = 603908149896019978
    IDEAS_CHANNEL_ID = 810644809416310784

    try:
        if message.guild.id != EVERYLANDS_GUILD_ID or message.channel.id != IDEAS_CHANNEL_ID:
            return
        ls = False
    except AttributeError: ls = True  # проверка на лс

    # все возможные цвета в майне
    supported_colors = ['BLACK', 'DARK_BLUE', 'DARK_AQUA', 'DARK_RED',
                        'DARK_PURPLE', 'GOLD', 'GRAY', 'DARK_GRAY', 'BLUE', 'GREEN',
                        'AQUA', 'RED', 'LIGHT_PURPLE', 'YELLOW', 'WHITE']
    try:
        parsedMsg = str(message.content).split('```')[1]  # уберает ``` с сообщения
        if '#' in parsedMsg: raise Exception('# in message')  # реагирует на коментарии в сообщении
        msg = safe_load(parsedMsg)  # парсит в YAML
        if len(msg) != 1: raise Exception('Need to be one ID')
        for id in msg: msgId = msg[id]  # находит айди указаное пользователем, и использует его дальше
        if len(str(msgId['name']).split('/')) != 3: raise Exception('Not correct name')  # должно быть 3 качества
        for ell in msgId['ingredients']:
            if len(str(ell).split('/')) != 2: raise Exception('Not correct ingredients')
        if not isinstance(msgId['cookingtime'], int): raise Exception('cookingtime not int')
        if not isinstance(msgId['distillruns'], int): raise Exception('distillruns not int')
        if not isinstance(msgId['distilltime'], int): raise Exception('distilltime not int')
        if 'wood' in msgId:
            if not isinstance(msgId['wood'], int): raise Exception('wood not int')
        if not isinstance(msgId['age'], int): raise Exception('age not int')
        if not msgId['color'] in supported_colors:
            if match(r'([a-f\d]{3}|[a-f\d]{6})$', msgId['color']) is None: raise Exception('Not correct color')
        if not isinstance(msgId['difficulty'], int): raise Exception('difficulty not int')
        if not isinstance(msgId['alcohol'], int): raise Exception('alcohol not int')
        if 'effects' in msgId:
            for ell in msgId['effects']: 
                if len(str(ell).split('/')) != 3: raise Exception('Not correct effects')
        if 'lore' in msgId:
            for ell in msgId['lore']: 
                if match(r'\+{1,3}', ell) is None: raise Exception('Not correct lore')
    except Exception as e:
        if not ls: await message.delete()  # если мы не в лс, удаляет сообщение

        exception_info = format_exc()
        if '```' in exception_info: 
            exception_info = exception_info.replace('```', "*'''*")  # * означает что там были `
            additional_comment = "(\*'''\* это \```)"  # type: ignore  # noqa: W605
        else: additional_comment = ''

        MSGuser = bot.get_user(message.author.id)
        await MSGuser.send('Привет! Видимо ты написал неправильно сообщение в канал с идеями для напитков! '  # type: ignore  # noqa: W605,E501
                        # f'Если это не так, пожалуйста напиши {bot.app_info.owner}\n'
                           'Если это не так, пожалуйста напиши Perchun_Pak#9236\n'
                           'Вот формат которому **необходимо** следовать'
                           '```\n'
                           '  id: # Айди вашего напитка, обязательно на английском\n'
                           '     name: Плохое качество/Нормальное качество/&6Хорошее качество\n'
                           '     ingredients: # может быть несколько\n       - Sugar_Cane/18\n'
                           '     cookingtime: 6 # время готовки\n     distillruns: 2 # кол-во раз дистиляции\n'
                           '     distilltime: 30 # время дистиляции\n'
                           '     wood: 2 # тип бочки в которой должен будет лежать напиток\n'
                           '     age: 14 # время настаивания - 1 год - 20 минут\n'
                           '     color: DARK_RED # цвет напитика можно HEX - "ffffff"\n'
                           '     difficulty: 6 # cложность приготовления (шанс неудачи)\n'
                           '     alcohol: 30 # опьянение\n     effects: # эффекты от напитка - зелье/сила/время\n'
                           '       - FIRE_RESISTANCE/1/20-100\n       - POISON/1-0/30-0\n'
                           '     lore: # описание у напитка, необязательно для каждого качества, и в общем необязательно\n'
                           '       - +Плохое качество\n       - ++Нормальное качество\n       - +++Хорошее качество\n'
                           '```\n'
                           '\``` обязательны, а вот все что после # нужно убрать\n\n'  # type: ignore  # noqa: W605
                           'Вот хороший пример'
                           '```\n'
                           '  wheatbeer:\n'
                           '     name: Вонючее Пшеничное пиво/Пшеничное пиво/Прекрасное Пшеничное Пиво\n'
                           '     ingredients:\n       - Wheat/3\n     cookingtime: 1\n     distillruns: 5\n'
                           '     distilltime: 30\n     wood: 1\n     age: 21\n'
                           '     color: "ffb84d"\n     difficulty: 6\n     alcohol: 30\n'
                           '     lore:\n       - +++ &8Освежающе\n'
                           '```\n'
                           'А вот несколько плохих примеров\n'
                           '```\nПиав\n```\n'
                           '```\n'
                           '  ПИВО:\n     имя: Пиво\n     ингридиенты:\n'
                           '       - Яйцо эндер дракона/3\n     цвет: зеленый\n'
                           '     опьянение: много\n'
                           '```\n'
                           '\n\n\nПричина удаления сообщения: ' + str(e))
        await MSGuser.send('\nTraceBack для разработчика: %s ```\n%s\n```'
                           '\nЕсли вы знаете язык програмирования Python, можете изучить наши '
                           'исходники по ссылке https://github.com/PerchunPak/EveryLandsDiscordBot' 
                           % (additional_comment, str(exception_info)))


try:
    bot.loop.run_until_complete(bot.start(TOKEN))
except KeyboardInterrupt:
    print("\nЗакрытие")
    bot.loop.run_until_complete(bot.change_presence(status=Status.invisible))
    for e in bot.extensions.copy():
        bot.unload_extension(e)
    print("Выходим")
    bot.loop.run_until_complete(Client.close(bot))
finally:
    print("Закрыто")
