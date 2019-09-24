# -*- coding: utf-8 -*-

import pymongo

client = pymongo.MongoClient(host='localhost', port=27017)
db = client['NBA']
collection1 = db['play_info']


def get_player_info():
    print('没想到吧！')
    return ""


if __name__ == '__main__':
    get_player_info()
