# -*- coding: utf-8 -*-
import pymongo


class getNBAData():
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['NBA']

    def __init__(self, start_url='https://china.nba.com/static/data/player/stats_klay_thompson.json'):
        self.start_url = start_url

    # 从start_url得到每场比赛的id
    def get_gameid(self, start_url):
        import requests
        import json
        r = requests.get(start_url)
        data = json.loads(r.content)
        game_id = []
        for each in data['payload']['player']['stats']['seasonGames']:
            game_id.append(each['profile']['gameId'])
        return game_id

    # 把列表解析成数据框
    def resol_dataLs(self, dataLs, team):
        import pandas as pd
        playerData = dataLs[team]['gamePlayers']
        teamName = dataLs[team]['profile']['displayAbbr']
        for i in range(len(playerData)):
            playerData[i]['statTotal'].update(player=playerData[i]['profile']['displayName'])
            playerData[i] = playerData[i]['statTotal']
        df = pd.DataFrame(playerData, columns=list(playerData[0].keys()))
        df['teamName'] = teamName
        df['atHome'] = team
        return df

    # 把列表解析成数据框
    def resol_dataLs1(self, dataLs, team, gameTime):
        import pandas as pd
        playerData = dataLs[team]['gamePlayers']
        teamName = dataLs[team]['profile']['displayAbbr']
        for i in range(len(playerData)):
            playerData[i]['statTotal'].update(player=playerData[i]['profile']['displayName'])
            playerData[i] = playerData[i]['statTotal']
            playerData[i]['atHome'] = 'team'
            playerData[i]['gameDesc']
            self.storeData2MongoDB(self, playerData[i])
        return ""

    def storeData2MongoDB(self, data):
        collection = self.db['nba_player']
        collection.insert_one(data)
        return None

    # 数据框直接写入mysql数据库，我的密码用*代替了
    def storeData2MySql(self, data, schema, table):
        import pymongo
        import pandas as pd

        # self.collection1.insert_one(data)
        data.to_excel("D:\\NBA.xlsx")

        return None

    # 主函数
    def get_gameprofile(self):
        import datetime
        import pytz
        import requests
        import json
        import pandas as pd
        game_id = self.get_gameid(self.start_url)
        url = 'https://china.nba.com/static/data/game/snapshot_%s.json'
        for each in game_id:
            r = requests.get(url % each)
            rawdata = json.loads(r.content)
            gameTime = datetime.datetime.fromtimestamp(int(rawdata['timestamp']) / 1000,
                                                       pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d')
            homeTeam = self.resol_dataLs1(rawdata['payload'], 'homeTeam', gameTime)
            awayTeam = self.resol_dataLs1(rawdata['payload'], 'awayTeam', gameTime)

            tot_df = pd.concat([homeTeam, awayTeam])
            tot_df['gameDate'] = gameTime

            tot_df['gameDesc'] = '%s(%d)@%s(%d)' % (
                tot_df[tot_df['atHome'] == 'awayTeam']['teamName'][0], rawdata['payload']['boxscore']['awayScore'],
                tot_df[tot_df['atHome'] == 'homeTeam']['teamName'][0], rawdata['payload']['boxscore']['homeScore'])
            self.storeData2MySql(tot_df, 'python_spyder', 'worriorsGame')


if __name__ == '__main__':
    getNBAData().get_gameprofile()
