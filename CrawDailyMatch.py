# -*- coding: utf-8 -*-
import datetime
import json
import time

import pymongo
import requests


class craw_daily_match():
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['NBA']
    collection1 = db['daily_match']

    def __init__(self):
        self.url_daily_match = "https://china.nba.com/static/data/scores/gamedaystatus_%s.json"
        self.url_daily_snapshot = 'https://china.nba.com/static/data/game/snapshot_%s.json'

    def get_game_time(self, time_tamp):
        time_tamp = time_tamp / 1000
        date_array = datetime.datetime.fromtimestamp(time_tamp)
        game_time = date_array.strftime("%Y-%m-%d %H:%M:%S")
        return game_time

    # 从start_url得到每场比赛的id
    def get_gameid(self, url):
        r = requests.get(url)
        data = json.loads(r.content)
        game_id = []
        for each in data['payload']['gameDates'][0]['games']:
            game_id.append(each['gameId'])
        return game_id

    def get_daily_match_info(self, game_id, date):
        count = 0
        for each in game_id:
            url_daily_snapshot = self.url_daily_snapshot % each
            r = requests.get(url_daily_snapshot)
            raw_data = json.loads(r.content)

            self.resol_raw_data(raw_data['payload'])
            count = self.display_process(len(game_id), count, date)
        print("\n")
        return ""

    # 把列表解析成数据框
    def resol_raw_data(self, data):
        data1 = data['homeTeam']['score']
        for each in data1:
            print(each)

        return ""

    def store_data_to_mongodb(self, data):
        self.collection1.insert_many(data)
        return None

    def display_process(self, length, count, date):
        count = count + 1
        print('\r{:s}比赛日数据获取进度:{:.2f}%'.format(date, count * 100 / length), end='')
        return count

    # 主函数
    def get_game_profile(self):
        for y in range(2019, 2020):
            for m in range(4, 5):
                if m < 10:
                    m = '0' + str(m)
                for d in range(4, 6):
                    time.sleep(1)  # 避免爬取速度过快
                    d = '0' + str(d)
                    date = str(y) + "-" + str(m) + "-" + str(d)
                    url_daily_match = self.url_daily_match % date
                    game_id = self.get_gameid(url_daily_match)
                    self.get_daily_match_info(game_id, date)


if __name__ == '__main__':
    craw_daily_match().get_game_profile()
