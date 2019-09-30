import argparse
import string

import pandas

import CrawlDailyMatch
import CrawlPlayerInfo

parser = argparse.ArgumentParser()
parser.description = 'Select what kind of information you want to fetch'
parser.add_argument("-d", "--daily", dest="daily_match", help="Crawl the daily_match or not", default=True)
parser.add_argument("-s", "--start", dest="start_time", action='store', type=str, metavar='start_time')
parser.add_argument("-e", "--end", dest="end_time", action='store', type=str, metavar='end_time')
parser.add_argument("-p", "--player", dest="player_info", action='store', type=str, default=string.ascii_uppercase)
parser.add_argument("-t", "--team", dest="team_info", help="Crawl the team_info or not", default=False)
args = parser.parse_args()
# 爬取每日比赛信息
if args.daily_match:
    if args.start_time is None or args.end_time is None:
        print("爬取数据时间范围未输入")
    else:
        craw_list = pandas.date_range(args.start_time, args.end_time)
        for each in craw_list:
            CrawlDailyMatch.daily_process(each.strftime('%Y-%m-%d'))
# 爬取球员信息
if args.player_info:
    for each in args.player_info:
        print(each)
        CrawlPlayerInfo.player_process(each)
    pass
# 爬取球队信息
if args.team_info:
    pass
