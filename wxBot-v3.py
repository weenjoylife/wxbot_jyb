#!/usr/bin/env python
# coding: utf-8

from wxbot import *
import ConfigParser
import json
from collections import Counter
import time
import re

import sys


# 报单微信Bot
class BDWXBot(WXBot):
    def __init__(self):
        WXBot.__init__(self)

        self.tuling_key = ""
        self.robot_switch = True

        try:
            cf = ConfigParser.ConfigParser()
            cf.read('conf.ini')
            self.tuling_key = cf.get('main', 'key')
        except Exception:
            pass
        print 'tuling_key:', self.tuling_key

    def tuling_auto_reply(self, uid, msg):
        if self.tuling_key:
            url = "http://www.tuling123.com/openapi/api"
            user_id = uid.replace('@', '')[:30]
            body = {'key': self.tuling_key, 'info': msg.encode('utf8'), 'userid': user_id}
            r = requests.post(url, data=body)
            respond = json.loads(r.text)
            result = ''
            if respond['code'] == 100000:
                result = respond['text'].replace('<br>', '  ')
                result = result.replace(u'\xa0', u' ')
            elif respond['code'] == 200000:
                result = respond['url']
            elif respond['code'] == 302000:
                for k in respond['list']:
                    result = result + u"【" + k['source'] + u"】 " +\
                        k['article'] + "\t" + k['detailurl'] + "\n"
            else:	
                result = respond['text'].replace('<br>', '  ')
                result = result.replace(u'\xa0', u' ')

            print '    ROBOT:', result
            return result
        else:
            return u"知道啦"

    def auto_switch(self, msg):
        msg_data = msg['content']['data']
        stop_cmd = [u'退下', u'走开', u'关闭', u'关掉', u'休息', u'滚开']
        start_cmd = [u'出来', u'启动', u'工作']
        if self.robot_switch:
            for i in stop_cmd:
                if i == msg_data:
                    self.robot_switch = False
                    self.send_msg_by_uid(u'[Robot]' + u'机器人已关闭！', msg['to_user_id'])
        else:
            for i in start_cmd:
                if i == msg_data:
                    self.robot_switch = True
                    self.send_msg_by_uid(u'[Robot]' + u'机器人已开启！', msg['to_user_id'])

    def handle_msg_all(self, msg):
		msg_time = time.strftime('%Y-%m-%d %H:%M', time.localtime())
		
		data_list = msg['content']['data'].split()
		
		
		# 处理群发的文本消息
		if msg['msg_type_id'] == 3 and msg['content']['type'] == 0:  # group text message
		
			msg_content = msg['content']['data']
			msg_content_list = msg_content.split()
			
			pattern = re.compile(u"[0-9]+")
			res = re.findall(pattern, msg_content_list[0])
			print(res)
			
			print msg_content_list[0]
			print type(msg_content_list[0])
			
			# 汇总
			if msg['content']['data'] == u'汇总':
				mydict = {}
				baodan_records = ''
				
				with open('baodan.txt', 'r') as file:
					#baodan_records = file.read()  这一行read了，会导致for line in file.readlines() 没有数据
					#print(baodan_records)
					
					for line in file.readlines():
						
						
						user_name = line.split()[0]
						#print(user_name)
						
						if(user_name not in mydict.keys()):
							mydict[user_name] = float(line.split()[3])
						else:
							mydict[user_name] = mydict[user_name] + float(line.split()[3])				
				
				with open('qingshu.txt', 'a+') as file:
					all_records = ''
					with open('baodan.txt', 'r') as a_file:
						all_records = a_file.read()
					file.write(all_records)
					file.write('----')
					file.write('\n')
					for k,v in mydict.items():
						record_str = k + ' ' + str(v)
						file.write('汇总: ' + record_str)
						file.write('\n')
					file.write('----'+'\n')
				with open('baodan.txt', 'w+') as file:
					file.write('')
					
				with open('qingshu.txt', 'r+') as file:
					zhangdan = file.read()
					
					new_zhangdan = zhangdan.split('----')[-2]
					new_zhangdan = new_zhangdan[1:]
					
					self.send_msg_by_uid(new_zhangdan, msg['user']['id'])
			
			# 清数				
			elif msg['content']['data'] == u'清数':
				reply = u'已完成清数，小伙伴请核对记录噢'
				self.send_msg_by_uid(reply, msg['user']['id'])
			
			elif msg_content_list[0] == u'云闪付':
				user = msg['content']['user']['name']
				msg_date = msg_time
				reply = ''
				data_list = data_list[1:]
				for index,bd_data in enumerate(data_list):
					money = bd_data
					if(index == len(data_list) - 1):
						record = user + '-' + u'云闪付' + ' ' + msg_date + ' ' + money
					else:
						record = user + '-' + u'云闪付' + ' ' + msg_date + ' ' + money+ '\n'
					reply = reply + record
				self.send_msg_by_uid(u'成功录入: \n' + reply, msg['user']['id'])
				
				with open('baodan.txt', 'a+') as file:
					file.write(reply.encode(encoding='UTF-8'))
					file.write('\n')
			
			elif len(res) == 0:
				reply = u'请检查输入'
				self.send_msg_by_uid(reply, msg['user']['id'])
				
			
			
			# 录入报单
			else:
				user = msg['content']['user']['name']
				msg_date = msg_time
				reply = ''
				for index,bd_data in enumerate(data_list):
					money = bd_data
					if(index == len(data_list) - 1):
						record = user + ' ' + msg_date + ' ' + money
					else:
						record = user + ' ' + msg_date + ' ' + money+ '\n'
					reply = reply + record
				self.send_msg_by_uid(u'成功录入: \n' + reply, msg['user']['id'])
				
				with open('baodan.txt', 'a+') as file:
					file.write(reply.encode(encoding='UTF-8'))
					file.write('\n')
					
			

def main():
    bot = BDWXBot() 
    bot.DEBUG = True
    bot.conf['qr'] = 'png'

    bot.run()


if __name__ == '__main__':
    main()

