# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import time
import pymysql
import datetime

# 初始化默认URL
# url = 'https://www.zhipin.com/c101020100/e_104-h_101020100/?query=%E5%85%BC%E8%81%8C&page=1&ka=page-1'  # 上海
# url = 'https://www.zhipin.com/c101190100/e_104-h_101190100/?query=%E5%85%BC%E8%81%8C&page=1&ka=page-1'  #  南京
url = 'https://www.zhipin.com/c101210100/h_101210100/?query=%E5%85%BC%E8%81%8C&page=1&ka=page-1'    # 杭州
# db = pymysql.connect("127.0.0.1", "root", "a", "crawler")
db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='a', db='crawler', charset="utf8")
cursor = db.cursor()


def init():
    global url

    headers = {
        'x-devtools-emulate-network-conditions-client-id': "5f2fc4da-c727-43c0-aad4-37fce8e3ff39",
        'upgrade-insecure-requests': "1",
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'dnt': "1",
        'accept-encoding': "gzip, deflate",
        'accept-language': "zh-CN,zh;q=0.8,en;q=0.6",
        'cookie': "__c=1501326829; lastCity=101020100; __g=-; __l=r=https%3A%2F%2Fwww.google.com.hk%2F&l=%2F; __a=38940428.1501326829..1501326829.20.1.20.20; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1501326839; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1502948718; __c=1501326829; lastCity=101020100; __g=-; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1501326839; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1502954829; __l=r=https%3A%2F%2Fwww.google.com.hk%2F&l=%2F; __a=38940428.1501326829..1501326829.21.1.21.21",
        'cache-control': "no-cache",
        'postman-token': "76554687-c4df-0c17-7cc0-5bf3845c9831"
    }

    proxies = {
        'http': 'http://222.183.255.255'
    }

    var = 100  # 默认抓取页数var页
    while var > 0:
        html = requests.get(url, headers=headers, proxies=proxies)
        if html.status_code != 200:  # 爬的太快网站返回403
            print('status_code is %d' % html.status_code)
            # 此处可以记录当前url到日志
            break
        soup = BeautifulSoup(html.text, "html.parser")
        jobList = soup.select('div.job-list ul li')

        jobItems = []
        for job in jobList:
            jobItem = {}
            jobItem['href'] = 'https://www.zhipin.com' + job.select('div.info-primary h3.name a')[0].get('href')
            jobItem['jobid'] = job.select('div.info-primary h3.name a')[0].get('data-jobid')
            jobItem['title'] = job.select('div.info-primary h3.name a div.job-title')[0].get_text()
            jobItem['salary'] = clear_salary(job.select('div.info-primary h3.name a span.red')[0].get_text())

            tags = job.select('div.info-primary h3.name a div.info-detail div.tags')
            if tags:
                jobItem['tags'] = tags[0].get_text()
            else:
                jobItem['tags'] = ''

            des = job.select('div.info-primary h3.name a div.info-detail p')
            if des:
                jobItem['des'] = des[0].get_text()
            else:
                jobItem['des'] = ''

            publishTime = job.select('div.info-publis p')
            if publishTime:
                jobItem['publishTime'] = clear_publishTime(publishTime[0].get_text())
            else:
                jobItem['publishTime'] = 0

            company = job.select('div.info-company h3.name a')
            if company:
                jobItem['company'] = company[0].get_text()
            else:
                jobItem['company'] = 0

            jobItem['source_url'] = url
            jobItem['from_plat'] = "BOSS直聘"
            jobItem['create_time'] = int(time.time())
            jobItem['update_time'] = int(time.time())

            save(jobItem)
            print(jobItem)
            jobItems.append(jobItem)

        # 重新赋值全局url
        url = getUrl(url)
        var = var - 1
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
    if not publishTime.find('布于'):
        return 0
    publishTime = publishTime.replace("发布于", "2018-")
    publishTime = publishTime.replace("月", "-")
    publishTime = publishTime.replace("日", "")
    if publishTime.find("昨天") > 0:
        publishTime = str(datetime.date.today() - datetime.timedelta(days=1))
    elif publishTime.find(":") > 0:
        publishTime = str(datetime.date.today())

    timeArray = time.strptime(publishTime, "%Y-%m-%d")
    publishTime = time.mktime(timeArray)
    return publishTime


# """
def save(job):
    global cursor
    global db

    selectSql = "SELECT jobid FROM jobs WHERE company = '%s' AND title = '%s'" % (job['company'],job['title'])
    r = cursor.execute(selectSql)

    insertSql = "INSERT INTO jobs (jobid, href, title,salary_low,salary_high,salary_avg,tags,des,publishTime,company,source_url,from_plat,create_time,update_time) VALUES ('%s', '%s', '%s','%s', '%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
        job['jobid'], job['href'], job['title'], job['salary']['low'], job['salary']['high'], job['salary']['avg'],
        job['tags'], job['des'], job['publishTime'], job['company'], job['source_url'], job['from_plat'],
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


def getUrl(last):
    url_list = last.split("&")

    url = ''
    for urlItem in url_list:
        if "https://www.zhipin.com" in urlItem:
            url += urlItem
        elif "page=" in urlItem:
            urlItem_list = urlItem.split("=")
            pageNum = int(urlItem_list[1]) + 1
            url += "&" + urlItem_list[0] + "=" + str(pageNum)
        elif "ka=" in urlItem:
            url += "&ka=page-next"
        else:
            return last

    return url


if __name__ == "__main__":
    init()
