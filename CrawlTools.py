# -*- coding: utf-8 -*-
import datetime
import json
import os
import random
import shutil
import time
from io import BytesIO

import pymongo
import requests
from PIL import Image


class MyCrawl:
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['NBA']
    # 待抓包的路径
    url_daily_match = "https://china.nba.com/static/data/scores/gamedaystatus_%s.json"
    url_daily_snapshot = 'https://china.nba.com/static/data/game/snapshot_%s.json'
    url_playByPlays = 'https://china.nba.com/static/data/game/playbyplay_%s_%s.json'
    url_player_list = 'https://china.nba.com/static/data/league/playerlist_%s.json'
    url_player = 'https://china.nba.com/static/data/player/stats_%s.json'
    url_player_pic = 'https://china.nba.com/media/img/players/head/260x190/%s.png'
    # 图片文件存储路径
    file_dir = './res'
    file_path_team = 'F:\\NBA_Data\\team'
    code = 'utf-8'
    mtlist = {'0', '14', '15', '16', '17', '19', '21', '22'}
    collection1 = db['daily_match']
    collection2 = db['match_list']
    collection3 = db['play_by_plays']
    collection4 = db['player_info']
    collection5 = db['player_hotzone']
    collection5 = db['team_info']

    def __init__(self):
        pass

    # 抓包获取到原始数据
    def get_raw_data(self, url):
        try:
            time.sleep(random.uniform(1, 3))  # 避免爬取速度过快
            r = requests.get(url)
            r.raise_for_status()
            r.encoding = self.code
            raw_data = json.loads(r.content)
        except:
            raw_data = {}
        return raw_data

    def get_raw_pic(self, url, file_path, file_name):
        try:
            time.sleep(random.uniform(2, 4))
            r = requests.get(url)
            image = Image.open(BytesIO(r.content))
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            image.save(os.path.join(file_path, file_name))
        except:
            shutil.copy(self.file_dir + '/not_found.png', os.path.join(file_path, file_name))
            pass
        return ""

    # 比赛时间保存在‘gameProfile’下的‘utcMillis’
    def get_game_time(self, time_tamp):
        time_tamp = int(time_tamp) / 1000
        date_array = datetime.datetime.fromtimestamp(time_tamp)
        game_time = date_array.strftime("%Y-%m-%d %H:%M:%S")
        return game_time
