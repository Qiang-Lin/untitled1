# -*- coding: utf-8 -*-
import json
import random
import time

import pymongo
import requests


class MyCraw:
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['NBA']
    url_daily_match = "https://china.nba.com/static/data/scores/gamedaystatus_%s.json"
    url_daily_snapshot = 'https://china.nba.com/static/data/game/snapshot_%s.json'
    url_playByPlays = 'https://china.nba.com/static/data/game/playbyplay_%s_%s.json'
    code = 'utf-8'
    mtlist = {'0', '14', '15', '16', '17', '19', '21', '22'}
    collection1 = db['daily_match']
    collection2 = db['match_list']
    collection3 = db['play_by_plays']

    def __init__(self):
        pass

    def get_raw_data(self, url):
        try:
            time.sleep(random.uniform(1, 2))  # 避免爬取速度过快
            r = requests.get(url)
            r.raise_for_status()
            r.encoding = self.code
            raw_data = json.loads(r.content)
        except:
            raw_data = {}
        return raw_data
