""" This is auto salmonrun program """
from asyncio import sleep
import requests
import json
import discord
import datetime
import locale
import random

locale.setlocale(locale.LC_ALL, '')

URL = 'https://spla2.yuu26.com/coop/schedule'
WEAPON_URL = 'https://splatoon2.ink/data/locale/ja.json'
HEADERS = {'User-Agent': 'runrunbot/1.0 (twitter @KON_md100)'}
TOKEN = 'MzU3OTQyMjQ5Mjc2OTY0ODc0.DquLWg.GKun6e7ZFskvFFACUyVJV2HTbpw'
CHANNEL = discord.Object(id=str(351380982068150272))
CLIENT = discord.Client()
PATH_SALMONRUNDATA = 'tmp/salmonrun_data.json'
PATH_WEAPONDATA = 'tmp/weapon.json'


@CLIENT.event
async def on_ready():
    print('Logged in as')
    print(CLIENT.user.name)
    print(CLIENT.user.id)
    print('------')


@CLIENT.event
async def on_message(message):
    if message.content.startswith('!later'):
        await CLIENT.send_message(message.channel, show_salmon_date("later"))
    elif message.content.startswith('!new'):
        await CLIENT.send_message(message.channel, show_salmon_date("new"))
    elif message.content.startswith('!omi'):
        await CLIENT.send_message(message.channel, omikuji_weapon())
    elif message.content.startswith('!dai'):
        await CLIENT.send_message(message.channel, university_go_or_wait())
    elif message.content.startswith('!kan'):
        await CLIENT.send_message(message.channel, show_gusher_map())
    elif message.content.startswith('!kon'):
        await CLIENT.send_message(message.channel, kon())


@CLIENT.event
async def salmon_processing():
    """
    指定の時間に鮭のpopを通知する
    """
    while True:
        await CLIENT.wait_until_ready()
        now = datetime.datetime.now()
        nowplaydata = change_presence()
        try:
            await CLIENT.change_presence(game=discord.Game(name=nowplaydata))
        except AttributeError:
            pass
        except TimeoutError:
            pass
        with open (PATH_SALMONRUNDATA, 'r') as f:
            json_data = json.load(f)
            poptime = datetime.datetime.strptime(json_data['result'][0]['start'], '%Y-%m-%dT%H:%M:%S')
        nowtime = datetime.time(now.hour, now.minute)
        poptime = datetime.time(poptime.hour, poptime.minute)
        if (nowtime == poptime):
            try:
                await CLIENT.send_message(CHANNEL, show_salmon_date("now"))
            except AttributeError:
                pass
            except TimeoutError:
                pass

        waittime = 60 - now.second
        await sleep(waittime)


def download_salmondate():
    """
    鮭の予定をダウンロード
    """
    r = requests.get(URL, headers=HEADERS)
    if r.status_code != 200:
        print('jsonが取得できませんでした')
        return False
    salmon_data = r.json()
    with open(PATH_SALMONRUNDATA, 'w') as f:
        json.dump(salmon_data, f, ensure_ascii=False, indent=2)



def download_wepon():
    """
    ブキの情報をダウンロード
    """
    r = requests.get(WEAPON_URL, headers=HEADERS)
    if r.status_code != 200:
        print('jsonが取得できませんでした')
        return False
    weapon_data = r.json()
    with open(PATH_WEAPONDATA, 'w') as f:
        json.dump(weapon_data, f, ensure_ascii=False, indent=2)
        


def change_presence():
    """
    次の鮭までの時間を表示
    """
    nowplay = 0
    with open (PATH_SALMONRUNDATA, 'r') as f:
        json_data = json.load(f)
        poptime = datetime.datetime.strptime(
            json_data['result'][0]['start'], '%Y-%m-%dT%H:%M:%S')
        endtime = datetime.datetime.strptime(
            json_data['result'][0]['end'], '%Y-%m-%dT%H:%M:%S')

    now = datetime.datetime.now()
    remaining_time = poptime - now + datetime.timedelta(minutes=1)
    remaining_days = remaining_time.days
    remaining_hours = remaining_time.seconds//3600
    remaining_minutes = remaining_time.seconds % 3600//60
    if (remaining_days > 0):
        nowplay = "次は" + str(remaining_days) + "日" + \
            str(remaining_hours) + "時間" + str(remaining_minutes) + "分後"
    else:
        if (remaining_time - datetime.timedelta(minutes=1) > datetime.timedelta(seconds=0)):
            if (remaining_hours > 0):
                nowplay = "次は" + str(remaining_hours) + "時間" + \
                    str(remaining_minutes) + "分後"
            else:
                nowplay = str(remaining_minutes) + "分後"
        else:
            remaining_time = endtime - now + datetime.timedelta(minutes=1)
            remaining_days = remaining_time.days
            remaining_hours = remaining_time.seconds//3600
            remaining_minutes = remaining_time.seconds % 3600//60
            if (remaining_days > 0):
                nowplay = "開催中：残り" + \
                    str(remaining_days) + "日" + str(remaining_hours) + \
                    "時間" + str(remaining_minutes) + "分"
            else:
                if (remaining_minutes > 0):
                    if (remaining_hours > 0):
                        nowplay = "開催中：残り" + str(remaining_hours) + \
                            "時間" + str(remaining_minutes) + "分"
                    else:
                        nowplay = "開催中：残り" + str(remaining_minutes) + "分"
                else:
                    download_salmondate()

    return nowplay


def show_salmon_date(date):
    """
    鮭の予定を表示
    """
    now = datetime.datetime.now()
    if date == "new":
        salmon_date = 0
    elif date == "later":
        salmon_date = 1
    else:
        msg = "日時取得エラーです\n"
        return msg

    with open (PATH_SALMONRUNDATA, 'r') as f:
        json_data = json.load(f)
        start_date = datetime.datetime.strptime(
            json_data['result'][salmon_date]['start'], '%Y-%m-%dT%H:%M:%S')
        end_date = datetime.datetime.strptime(
            json_data['result'][salmon_date]['end'], '%Y-%m-%dT%H:%M:%S')
        start_date_str = start_date.strftime('%m/%d %H時 - ')
        end_date_str = end_date.strftime('%m/%d %H時')
        msg = start_date_str + end_date_str + "\n"

        if salmon_date == 0:
            if (start_date - now).days < 0:
                remaining_salmon_time = end_date - now
                msg += '開催中：あと' + str(remaining_salmon_time.seconds//3600) + '時間' + str(remaining_salmon_time.seconds%3600//60) + '分後に終了\n'
            else:
                remaining_salmon_time = start_date - now
                msg += 'あと' + str(remaining_salmon_time.seconds//3600) + '時間' + str(remaining_salmon_time.seconds%3600//60) + '分後に開催\n'

        elif salmon_date == 1:
            after_salmon_time = start_date - now
            msg += 'あと' + str(after_salmon_time.seconds//3600) + '時間' + str(after_salmon_time.seconds%3600//60) + '分後に開催\n'

        msg += "ステージ:\n\t" + \
            json_data['result'][salmon_date]['stage']['name'] + "\n"
        msg += "ブキ:\n"
        for f in json_data['result'][salmon_date]['weapons']:
            msg += "\t" + f['name'] + "\n"

    return msg


def omikuji_weapon():
    with open (PATH_WEAPONDATA, 'r') as f:
        weapon_data = json.load(f)
        data = weapon_data['weapons']
    keys = list(data.keys())
    random_number = random.randint(0, len(keys)-1)
    random_weapon = data[keys[random_number]]['name']
    msg = "次に使うブキは" + random_weapon + "に決まり"
    return msg


def university_go_or_wait():
    random_number = random.randint(0, 1)
    word_list = ['行く', '行かない']
    msg = "今日は大学に" + word_list[random_number]
    return msg


def show_gusher_map():
    map_list_url = {'トキシラズいぶし工房': 'https://pbs.twimg.com/media/DQ02uHWVwAAxcmM.jpg:large',
                    '難破船ドン・ブラコ': 'https://pbs.twimg.com/media/Djp61D4U0AAZpvH.jpg:large',
                    'シェケナダム': 'https://pbs.twimg.com/media/DNv1wZYUIAAUQ0q.jpg:large',
                    '海上集落シャケト場': 'https://pbs.twimg.com/media/DNv1xZ8UMAAP4zv.jpg:large'}
    with open (PATH_SALMONRUNDATA, 'r') as f:
        json_data = json.load(f)
        now_salmon_stage = json_data['result'][0]['stage']['name']
    try:
        todays_gusher_map_url = map_list_url[now_salmon_stage]
    except KeyError:
        todays_gusher_map_url = now_salmon_stage + 'のカンケツセンデータがありません'
    return todays_gusher_map_url


def kon():
    random_freq = random.uniform(0, 10)
    msg = '今日は{0:.1f}'.format(random_freq) + ' GHzな気持ち\nかんそう：' 
    if random_freq < 1:
        msg += 'もうちょっと周波数上げましょう\n'
    elif random_freq < 3:
        msg += 'いい感じだけど，それじゃあ空間伝播できないよ\n'
    elif random_freq < 5:
        msg += 'いいね！それだけ．\n'
    elif random_freq < 7:
        msg += '電波ゆんゆん．どんどん伝播していこう\n'
    elif random_freq < 9:
        msg += '最高！どんな空間だって渡り歩けそう\n'
    elif random_freq < 10:
        msg += '俺が電波だ\n'
    return msg


"""
デバッグ用
"""
# print(show_salmon_date("now"))
# print(show_salmon_date("later"))
# print(change_presence())

# download_salmondate()
# download_wepon()
CLIENT.loop.create_task(salmon_processing())
CLIENT.run(TOKEN)
