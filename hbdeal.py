#!/usr/bin/env python
# -*- coding: utf-8 -*-
#coding = uft-8
#coding by xsseng - 9166794@qq.com
#tipping btc address:1Fck8AG9Ev656NKJ3VWTJXT2vjAJZGiBEN

import urllib
import urllib2
import json
import time

#用户配置信息
url_buy = 'https://api-otc.huobi.pro/v1/otc/trade/list/public?coinId=1&tradeType=1&currentPage=1&payWay=&country='
url_sell = 'https://api-otc.huobi.pro/v1/otc/trade/list/public?coinId=1&tradeType=0&currentPage=1&payWay=&country='
url_order = 'https://api-otc.huobi.pro/v1/otc/order/submit'
url_get_order = 'https://api-otc.huobi.pro/v1/otc/order/confirm?order_ticket='
agent = 'User-Agent,Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0.2 Safari/604.4.7'
avg_data = []
#---------------------#
#防波动收购差价配置
d_price = 1200
#防做空收购数量境界
max_buy_num = 0.18
#爬虫定时/秒
t = 1
#输入用户cookie和token头的值
cookie = ''
token = ''
#---------------------#


#获取收售比特币的数据
def get_buy(url,headers):
   req = urllib2.Request(url)
   req.add_header("User-Agent",headers) 
   req.add_header("Host","api-otc.huobi.pro") 
   content = urllib2.urlopen(req)
   buy_data = content.read() 
   content.close()
   return buy_data


#将json格式化，得出最低价格
def json_data(jsondata):
   json_to_python = json.loads(jsondata)
   mindata_json = json_to_python['data'][0]
   new_min_json = json.dumps(mindata_json,ensure_ascii=False)
   new_min_data = json.loads(new_min_json)
   min_price = new_min_data['price']
   min_number = new_min_data['tradeCount']
   min_id = new_min_data['id']
   min_tradeNo = new_min_data['tradeNo']
   return min_price,min_number,min_id


#取出售商家参考平均值
def avg_sell(jsondata_sell):
   json_to_python = json.loads(jsondata_sell)
   for i in range(5):
      maxdata_json = json_to_python['data'][i]
      new_max_json = json.dumps(maxdata_json,ensure_ascii=False)
      new_max_data = json.loads(new_max_json)
      avg_data.append(new_max_data['price'])
   return (avg_data[0]+avg_data[1]+avg_data[2]+avg_data[3]+avg_data[4])//5


#get_ticket脚本
def get_ticket(buyNum,minBuy,tradeId):
   maxTradeLimit = buyNum * minBuy
   data = {'tradeId':tradeId,'amount':maxTradeLimit,'remark':''}
   req = urllib2.Request(url_order)
   req.add_header("User-Agent",agent)
   req.add_header("Host","api-otc.huobi.pro")
   req.add_header("token",token)
   req.add_header("Referer","https://otc.huobipro.com")
   req.add_header("Cookie",cookie)
   req.add_data(urllib.urlencode(data))
   content = urllib2.urlopen(req)
   order_data = content.read()
   content.close()
   json_to_python = json.loads(order_data)
   ticket_json = json_to_python['data']
   new_ticket_json = json.dumps(ticket_json,ensure_ascii=False)
   new_ticket = json.loads(new_ticket_json)
   try:
      ticket = new_ticket['ticket']
   except TypeError:
      ticket = 0
   return ticket


#下单脚本
def get_order(order_ticket):
   data = ''
   req = urllib2.Request(url_get_order+order_ticket)
   req.add_header("User-Agent",agent)
   req.add_header("Host","api-otc.huobi.pro")
   req.add_header("token",token)
   req.add_header("Referer","https://otc.huobipro.com")
   req.add_header("Cookie",cookie)
   req.add_data(urllib.urlencode(data))
   content = urllib2.urlopen(req)
   result_data = content.read()
   content.close()
   return result_data


#主逻辑与下单脚本
def btc_scan():
    buydata = get_buy(url_buy,agent)
    selldata = get_buy(url_sell,agent)
    minBuy,buyNum,tradeId = json_data(buydata)
    avgSell = avg_sell(selldata)
    if avgSell - minBuy > d_price:
       if buyNum < max_buy_num:
          ticket  = get_ticket(buyNum,minBuy,tradeId)
          if ticket != 0:
             order_result = get_order(ticket)
          else:
             order_result = 'error order'
          return '1','price differences:'+str(avgSell - minBuy),ticket,order_result
       else:
          return '2','count to much!',buyNum
    else:
       return 0,'waitting','min buy price:'+str(minBuy),'sell avg price:'+str(avgSell)


#定时执行
def timer(n):
   while True:
      print time.strftime('%X',time.localtime()),
      print btc_scan()
      time.sleep(n)
timer(t)
