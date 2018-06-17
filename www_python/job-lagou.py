# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import time
import pymysql
import datetime

import sys

print(sys.getdefaultencoding())

# 初始化默认URL
# url = 'https://www.lagou.com/jobs/positionAjax.json?city=%E4%B8%8A%E6%B5%B7&needAddtionalResult=false' #上海
# url = 'https://www.lagou.com/jobs/positionAjax.json?city=%E5%8D%97%E4%BA%AC&needAddtionalResult=false' #南京
url = 'https://www.lagou.com/jobs/positionAjax.json?city=%E6%9D%AD%E5%B7%9E&needAddtionalResult=false' #杭州
db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='a', db='crawler', charset="utf8")
cursor = db.cursor()


def init():
    global url

    headers = {
        # 第一个电脑和服务器信息，
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
        # 电脑和服务器信息
        # 第二个是你从哪里进入的拉钩网，没有这个以为是机器人访问。
        'Referer': 'https://www.lagou.com/jobs/list_%E5%85%BC%E8%81%8C?city=%E4%B8%8A%E6%B5%B7&cl=false&fromSearch=true&labelWords=&suginput=',
        # 第三个为了辨别身份，有的网站需要，有的不需要
        'Cookie': 'user_trace_token=20170921093258-cc8e4c13-9e6c-11e7-9d07-525400f775ce; LGUID=20170921093258-cc8e52b6-9e6c-11e7-9d07-525400f775ce; index_location_city=%E5%85%A8%E5%9B%BD; JSESSIONID=ABAAABAACEBACDGD4C15CDA891A7242B76AA4F9B7450B8B; _gat=1; PRE_UTM=; PRE_HOST=www.sogou.com; PRE_SITE=https%3A%2F%2Fwww.sogou.com%2Flink%3Furl%3DhedJjaC291NlQquFD-D9iKfCABISWiMgDLW1Nx6fG3psqHL_zYlG_a3mlRzfPLR2; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2Fgongsi%2Fj75915.html; TG-TRACK-CODE=index_search; _gid=GA1.2.405703854.1505957562; _ga=GA1.2.1930895945.1505957562; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1505957579,1505957596,1505957630,1505969456; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1505969469; LGSID=20170921125112-7dcd03f6-9e88-11e7-9d2f-525400f775ce; LGRID=20170921125125-85aaed04-9e88-11e7-91fb-5254005c3644; SEARCH_ID=746090bf111a497aa55f7f1b8dabffd2'
        # 来路，你是从哪个页面点入的
    }

    proxies = {
        'http': 'http://222.183.255.255'
    }

    var = 1  # 默认抓取条数
    while var <= 30:
        data = {
            'first': 'false',
            'pn': var,
            'kd': '兼职',
        }
        res = requests.post(url, headers=headers, data=data, proxies=proxies)
        result = res.json()['content']['positionResult']['result']

        if result:
            for job in result:
                jobItem = {}
                jobItem['href'] = "https://www.lagou.com/jobs/" + str(job['positionId']) + ".html"
                jobItem['jobid'] = job['positionId']
                jobItem['title'] = job['positionName']
                jobItem['salary'] = clear_salary(job['salary'])
                jobItem['tags'] = job['positionLables']
                jobItem['des'] = job['firstType'] + job['secondType']
                jobItem['publishTime'] = clear_publishTime(job['formatCreateTime'])
                jobItem['company'] = job['companyFullName']
                jobItem['source_url'] = url + "&page=" + str(var)
                jobItem['from_plat'] = "拉钩"
                jobItem['create_time'] = int(time.time())
                jobItem['update_time'] = int(time.time())

                save(jobItem)
                print(jobItem)

        # 重新赋值全局url
        var = var + 1
        time.sleep(3)


def clear_salary(salary):
    if type(salary) == type({}):
        return salary
    salary_list = salary.lower().replace("k", "000").split("-")
    if len(salary_list) != 2:
        return salary
    try:
        salary_list = [int(x) for x in salary_list]
    except:
        print(salary_list)
        return salary

    salary = {
        'low': salary_list[0],
        'high': salary_list[1],
        'avg': (salary_list[0] + salary_list[1]) / 2
    }
    return salary


def clear_publishTime(publishTime):
    # 2018-04-11
    if not publishTime.find('发布'):
        # 标准格式
        try:
            timeArray = time.strptime(publishTime, "%Y-%m-%d")
            publishTime = time.mktime(timeArray)
            return publishTime
        except Exception:
            print(Exception)
            return 0

    # 2天前发布
    t = '天前发布'
    if t in publishTime:
        publishTime = int(time.time()) - int(publishTime.replace("天前发布","")) * 24*3600
        return publishTime

    #15:42发布
    t = '发布'
    if t in publishTime:
        formatTime = time.strftime("%Y-%m-%d", time.localtime()) + " " + publishTime.replace("发布","") + ":00"
        timeArray = time.strptime(formatTime, "%Y-%m-%d %H:%M:%S")
        publishTime = time.mktime(timeArray)
        return publishTime

    print("发布时间格式错误")
    return 0


# """
def save(job):
    global cursor
    global db

    selectSql = "SELECT jobid FROM jobs WHERE company = '%s' AND title = '%s'" % (job['company'], job['title'])
    r = cursor.execute(selectSql)

    insertSql = "INSERT INTO jobs (jobid, href, title,salary_low,salary_high,salary_avg,tags,des,publishTime,company,source_url,from_plat,create_time,update_time) VALUES ('%s', '%s', '%s','%s', '%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
        job['jobid'], job['href'], job['title'], job['salary']['low'], job['salary']['high'], job['salary']['avg'],
        ",".join(job['tags']), job['des'], job['publishTime'], job['company'], job['source_url'], job['from_plat'],
        job['create_time'], job['update_time'])

    if r:
        print("职位已存在！")
    else:
        try:
            # 执行sql语句
            cursor.execute(insertSql)
            db.commit()
        except Exception:
            print(Exception)
            print("数据库执行失败,sql语句：" + insertSql)


if __name__ == "__main__":
    init()
