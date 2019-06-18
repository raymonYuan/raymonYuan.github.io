
import itchat
import requests
import time
import random
from itchat.content import *
# 用于记录回复过的好友
replied = []
# 获取新年祝福语
def GetRandomGreeting():
	res = requests.get("http://www.xjihe.com/api/life/greetings?festival=新年&page=10", headers = {'apiKey':'sQS2ylErlfm9Ao2oNPqw6TqMYbJjbs4g'})
	results = res.json()['result']
	print(results)
	return results[random.randrange(len(results))]['words']


# 发送新年祝福语
def SendGreeting(msg):
	global replied
	friend = itchat.search_friends(userName=msg['FromUserName'])
	if friend['RemarkName']:
		itchat.send((friend['RemarkName']+','+GetRandomGreeting()), msg['FromUserName'])
	else:
		itchat.send((friend['NickName']+','+GetRandomGreeting()), msg['FromUserName'])
	replied.append(msg['FromUserName'])

#raymonYuan 更新了触发条件
def pd(msg):
	if '新年' in msg  or '新春' in msg or '新岁' in msg:
		return True
	else:
		return False

# 文本消息
#raymonYuan: 更新了回复方式，显得更智能
@itchat.msg_register([TEXT])
def text_reply(msg):
	if msg['FromUserName'] not in replied:
		if  pd(msg['Text']):
			SendGreeting(msg)
		else :
			itchat.send("谢谢!^-^", msg['FromUserName'])

# 其他消息
@itchat.msg_register([PICTURE, RECORDING, VIDEO, SHARING])
def others_reply(msg):
	if msg['FromUserName'] not in replied:
		SendGreeting(msg)



if __name__ == '__main__':

	itchat.auto_login()
	itchat.run()
