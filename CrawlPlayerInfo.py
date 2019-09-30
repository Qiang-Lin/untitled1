# -*- coding: utf-8 -*-

import random
import string
import time

from CrawlTools import MyCrawl

my_crawl = MyCrawl()
file_path_player = 'F:\\NBA_Data\\player'


# 显示球员爬取进度
def display_process(count, length, word):
    count = count + 1
    print('\r球员{:s}数据获取进度:{:.2f}%'.format(word, count * 100 / length), end='')
    return count


# 获取每日比赛场次与数据，包括球队总览与球员个人的数据
def player_process(word):
    time.sleep(random.uniform(1, 3))  # 避免爬取速度过快
    count = 0  # 进度计数器
    url_player_list = my_crawl.url_player_list % word
    player_code = get_player_code(url_player_list)  # 获取当日比赛ID,以及当日数据更新时间戳
    for each in player_code:
        raw_data = get_player_info(each)  # 获取比赛详细数据
        resol_data = resol_player_data(raw_data, word)
        save_player(resol_data)
        get_player_pic(raw_data)
        count = display_process(count, len(player_code), word)
    return ""


def get_player_pic(raw_data):
    data = raw_data['payload']['player']['playerProfile']
    player_id = data['playerId']
    player_name = data['code']
    url_player_pic = my_crawl.url_player_pic % player_id
    my_crawl.get_raw_pic(url_player_pic, file_path_player, player_name + '.png')
    return ""




# 从url_daily_match得到每场比赛的id
def get_player_code(url_player_list):
    raw_data = my_crawl.get_raw_data(url_player_list)
    player_code = []
    try:
        for each in raw_data['payload']['players']:
            player_code.append(each['playerProfile']['code'])
        return player_code
    except:
        return []


# 获取每场比赛的文字直播数据，每次存入一场比赛文字直播数据
def get_player_info(each):
    url_player = my_crawl.url_player % each
    raw_data = my_crawl.get_raw_data(url_player)
    return raw_data


def resol_player_data(raw_data, word):
    data = raw_data['payload']
    player = data['player']['playerProfile']
    resol_data = {}
    resol_data.update({'InitName': word, 'code': player['code'], 'displayName': player['displayName'],
                       'timestamp': raw_data['timestamp']})
    resol_data.update(data)
    return resol_data


def save_player(resol_data):
    if my_crawl.collection4.count_documents({'code': resol_data['code']}) == 0:
        my_crawl.collection4.insert_one(resol_data)
    else:
        if my_crawl.collection4.find_one({'code': resol_data['code']})['timestamp'] != resol_data['timestamp']:
            my_crawl.collection4.update_one({'code': resol_data['code']}, {'$set': resol_data})


# 获取比赛信息的主入口
def get_player_profile():
    for word in string.ascii_uppercase:
        player_process(word)
    return ""


if __name__ == '__main__':
    get_player_profile()
