# -*- coding: utf-8 -*-
import datetime
import json
import random
import time

import pymongo
import requests


class CrawDailyMatch:
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['NBA']
    collection1 = db['daily_match']
    collection2 = db['match_list']

    def __init__(self):
        self.url_daily_match = "https://china.nba.com/static/data/scores/gamedaystatus_%s.json"
        self.url_daily_snapshot = 'https://china.nba.com/static/data/game/snapshot_%s.json'

    def display_process(self, length, count, date):
        count = count + 1
        print('\r{:s}日{:d}场比赛数据获取进度:{:.2f}%'.format(date, length, count * 100 / length), end='')
        return count

    # 比赛时间保存在‘gameProfile’下的‘utcMillis’
    def get_game_time(self, time_tamp):
        time_tamp = int(time_tamp) / 1000
        date_array = datetime.datetime.fromtimestamp(time_tamp)
        game_time = date_array.strftime("%Y-%m-%d %H:%M:%S")
        return game_time

    # 获取每日比赛场次与数据，包括球队总览与球员个人的数据
    def daily_match_process(self, date):
        url_daily_match = self.url_daily_match % date
        game_id = self.get_gameid(url_daily_match)
        self.get_daily_match_info(game_id, date)
        return ""

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
        match_list = []
        for each in game_id:
            url_daily_snapshot = self.url_daily_snapshot % each
            r = requests.get(url_daily_snapshot)
            raw_data = json.loads(r.content)
            daily_match_data = self.resol_daily_match_data(raw_data['payload'], url_daily_snapshot)
            self.save_daily_match(daily_match_data)
            count = self.display_process(len(game_id), count, date)
        return ""

    # 在此将一场比赛我们需要的信息汇总整理
    def resol_daily_match_data(self, data, url):
        home_data = data['homeTeam']
        away_data = data['awayTeam']
        resol_data = {'gameId': data['gameProfile']['gameId'], 'url': url}
        resol_data['gameTime'] = self.get_game_time(data['gameProfile']['utcMillis'])
        resol_data.update({'homeMatchup': home_data['matchup'], 'awayMatchup': away_data['matchup']})
        resol_data.update({'homeProfile': home_data['profile'], 'awayProfile': away_data['profile']})
        resol_data.update({'homeStanding': home_data['standing'], 'awayStanding': away_data['standing']})
        resol_data.update({'homeScore': home_data['score'], 'awayScore': away_data['score']})
        resol_data.update({'homeDetail': home_data['gamePlayers'], 'awayDetail': away_data['gamePlayers']})
        return resol_data

    def save_daily_match(self, data):
        # 判断数据库中是否已经存在对应数据
        if self.collection1.count_documents({'url': data['url']}) == 0:
            self.collection1.insert_one(data)
        else:
            print('\n%s基础数据重复爬取\n' % data['gameId'])

    def resol_match_list_data(self):

        return ""

    def save_match_list(self):
        return None

    # 主函数
    def get_game_profile(self):
        for y in range(2019, 2020):
            for m in range(4, 5):
                if m < 10:
                    m = '0' + str(m)
                for d in range(4, 6):
                    time.sleep(random.uniform(1, 3))  # 避免爬取速度过快
                    d = '0' + str(d)
                    date = str(y) + "-" + str(m) + "-" + str(d)
                    self.daily_match_process(date)

        return ""


if __name__ == '__main__':
    CrawDailyMatch().get_game_profile()
