# -*- coding: utf-8 -*-
import datetime
import json
import random
import time

import pandas
import pymongo
import requests

import CrawPlayerInfo


class CrawDailyMatch:
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['NBA']
    collection1 = db['daily_match']
    collection2 = db['match_list']
    collection3 = db['play_by_plays']

    def __init__(self):
        self.url_daily_match = "https://china.nba.com/static/data/scores/gamedaystatus_%s.json"
        self.url_daily_snapshot = 'https://china.nba.com/static/data/game/snapshot_%s.json'
        self.url_playByPlays = 'https://china.nba.com/static/data/game/playbyplay_%s_%s.json'
        self.code = 'utf-8'
        self.mtlist = {'0', '14', '15', '16', '17', '19', '21', '22'}

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

    def display_process(self, count, length, date):
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
    def daily_process(self, date):
        count = 0  # 进度计数器
        url_daily_match = self.url_daily_match % date
        [game_id, timestamp] = self.get_gameid(url_daily_match)  # 获取当日比赛ID,以及当日数据更新时间戳
        match_list_data = {'date': date, 'url': url_daily_match, 'timestamp': timestamp, 'content': {}}
        for each in game_id:
            raw_data = self.get_daily_match_info(each)  # 获取比赛详细数据
            match_list_data = self.resol_match_list_data(match_list_data, raw_data)  # 获取并更新当日比赛列表
            self.get_playByPlays_info(each, raw_data['payload']['boxscore']['period'])  # 获取文字直播信息
            count = self.display_process(count, len(game_id), date)
        self.save_match_list(match_list_data)  # 汇总整理好当日比赛列表后保存
        return ""

    # 从url_daily_match得到每场比赛的id
    def get_gameid(self, url):
        try:
            time.sleep(random.uniform(1, 2))  # 避免爬取速度过快
            r = requests.get(url)
            r.raise_for_status()
            r.encoding = self.code
            data = json.loads(r.content)
            game_id = []
            for each in data['payload']['gameDates'][0]['games']:
                game_id.append(each['gameId'])
            return [game_id, data['timestamp']]
        except:
            return [[], ""]

    # 获取每场比赛的具体数据, 并将信息汇总整理, 每次存入一场比赛数据
    def get_daily_match_info(self, each):
        time.sleep(random.uniform(1, 3))  # 避免爬取速度过快
        url_daily_snapshot = self.url_daily_snapshot % each
        raw_data = self.get_raw_data(url_daily_snapshot)
        daily_match_data = self.resol_daily_match_data(raw_data, url_daily_snapshot)
        self.save_daily_match(daily_match_data)
        return raw_data

    def resol_daily_match_data(self, raw_data, url):
        data = raw_data['payload']
        home_data = data['homeTeam']
        away_data = data['awayTeam']
        resol_data = {}
        resol_data.update({'gameId': data['gameProfile']['gameId'], 'url': url, 'timestamp': raw_data['timestamp']})
        resol_data['gameTime'] = self.get_game_time(data['gameProfile']['utcMillis'])
        resol_data['seasonType'] = data['gameProfile']['seasonType']
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
            if self.collection1.find_one({'url': data['url']})['timestamp'] == data['timestamp']:
                print('\n%s基础数据重复爬取\n' % data['gameId'])
            else:
                self.collection1.update_one({'url': data['url']}, {'$set': data})

    # 汇总整理一天的比赛对阵概要，每次存入一天比赛列表
    def resol_match_list_data(self, match_list_data, raw_data):
        data = raw_data['payload']
        match_content = data['homeTeam']['profile']['displayAbbr'] + str(data['boxscore']['homeScore']) + '-' + \
                        data['awayTeam']['profile']['displayAbbr'] + str(data['boxscore']['awayScore'])
        match_list_data['content'].update({data['gameProfile']['gameId']: match_content})
        return match_list_data

    def save_match_list(self, data):
        if self.collection2.count_documents({'url': data['url']}) == 0:
            self.collection2.insert_one(data)
        else:
            if self.collection2.find_one({'url': data['url']})['timestamp'] == data['timestamp']:
                print('\n%s比赛列表数据重复爬取\n' % data['date'])
            else:  # 数据更新
                self.collection2.update_one({'url': data['url']}, {'$set': data})

    # 获取每场比赛的文字直播数据，每次存入一场比赛文字直播数据
    def get_playByPlays_info(self, each, period):
        playByPlays_data = {'gameId': each, 'period': period, 'playByPlays': {}}
        for i in range(1, int(period) + 1):
            url_playByPlays = self.url_playByPlays % (each, str(i))
            raw_data = self.get_raw_data(url_playByPlays)  # 已包含延时
            playByPlays_data = self.resol_playByPlays_data(raw_data, i, playByPlays_data)
        self.save_playByPlays(playByPlays_data)

    def resol_playByPlays_data(self, raw_data, i, playByPlays_data):
        data = raw_data['payload']['playByPlays'][0]['events']
        for each in data:
            if each['messageType'] in self.mtlist:
                self.mtlist.remove(each['messageType'])
                print(each['messageType'] + each['description'])
        data.reverse()
        playByPlays_data['playByPlays'].update({'period_' + str(i): data})
        return playByPlays_data

    def save_playByPlays(self, data):
        if self.collection3.count_documents({'gameId': data['gameId']}) == 0:
            self.collection3.insert_one(data)
        else:
            print('\n%s文字直播数据重复爬取\n' % data['gameId'])
        return ""

    # 获取比赛信息的主入口
    def get_game_profile(self):

        start_time = '2019-01-01'
        end_time = '2019-01-03'
        craw_list = pandas.date_range(start_time, end_time)
        for each in craw_list:
            self.daily_process(each.strftime('%Y-%m-%d'))
        # for y in range(2019, 2020):
        #     for m in range(1, 4):
        #         if m < 10:
        #             m = '0' + str(m)
        #         for d in range(1, 32):
        #             if d < 10:
        #                 d = '0' + str(d)
        #             date = str(y) + "-" + str(m) + "-" + str(d)
        #             self.daily_process(date)
        return ""


if __name__ == '__main__':
    CrawDailyMatch().get_game_profile()
