import random

def food(meal):
	dishlist = {
		'general': ['炒饭', '炒面', '泡面', '煮面', '匹萨', '烧麦', '拉肠', '炒牛河', '海带', '炸鸡', '关东煮', '米线', '面包'],
		'breakfast': ['油条', '糯米鸡', '馅饼', '肉包子', '煎堆', '素包子', '糊辣汤', '肉粥', '甜粥', '馒头', '饭团', '昨晚的剩饭', '锅贴', '生煎', '冷面', '馄饨', '小笼', '煎饼果子', '大饼夹一切', '豆汁', '焦圈', '卤煮', '炒肝', '肉夹馍', '鸡蛋灌饼'],
		'lunch': ['宫保鸡丁', '红烧肉', '扬州狮子头', '腌笃鲜', '冒菜', '缅甸菜', '赛百味', '麦当劳', '肯德基', '汉堡王', '德克士', '华莱士', '鱼香肉丝', '西红柿炒鸡蛋', '排骨饭', '麻辣香锅', '水煮鱼', '卤肉饭', '鸡排饭', '沙拉', '黄焖鸡', '酸菜鱼'],
		'dinner': ['馒头', '火锅', '傣族菜', '漆油鸡', '柠檬撒', '汉堡包', '寿喜烧', '方便面', '意大利面', '通心粉', '拉面', '盖饭', '麻辣香锅', '麻辣烫', '麻辣拌', '鸭血粉丝', '鸡公煲', '糖醋里脊', '糖醋排骨', '熏鱼']
	}
	dishes = dishlist['general']
	if meal in dishlist:
		for dish in dishlist[meal]:
			dishes.append(dish)
	
	selected_dishes = []
	for _ in range(0,3):
		selected_dish = random.choice(dishes)
		selected_dishes.append(selected_dish)
		dishes.remove(selected_dish)

	return selected_dishes

import sqlite3
import time

def msg_log(message_id, group_id, sender_id, message):
	try:
		db = sqlite3.connect('qqbot.sqlite')
		cursor = db.cursor()
		cursor.execute('''CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, group_id INTEGER, sender_id INTEGER, message TEXT, timestamp REAL)''')
		db.commit()
	except:
		db.rollback()
		db.close()
		return '[ERROR] Database error'
	
	try:
		cursor.execute('''INSERT INTO messages(id, group_id, sender_id, message, timestamp) VALUES(?, ?, ?, ?, ?)''', (message_id, group_id, sender_id, message, time.time()))
		db.commit()
	except:
		db.rollback()
	finally:
		db.close()
		return '[INFO] Transaction complete'
	
def msg_fetch(group_id, sender_id, lines=5):
	try:
		db = sqlite3.connect('qqbot.sqlite')
		cursor = db.cursor()
		cursor.execute('''SELECT message FROM messages WHERE group_id = ? AND sender_id = ? ORDER BY timestamp DESC LIMIT ?''', (group_id, sender_id, lines))
		rows = cursor.fetchall()
		msg = '以下为[CQ:at,qq=%s]发送的最后%s条记录（如果有）：' % (sender_id, lines)
		for row in rows:
			msg += '\n%s' % (row[0])
		return msg
	except:
		db.close()
		return '[ERROR] Database error'

import requests
import requests_cache
import json

requests_cache.install_cache('qqstats', expire_after=1800)

def msg_stalker(self_id, group_id, sender_id, lines=5):
	try:
		raw_memberlist = requests.get('http://127.0.0.1:5700/get_group_member_list?group_id={}'.format(group_id)).json()
		memberlist = []
		if raw_memberlist['data']:
			for member in raw_memberlist['data']:
				memberlist.append(str(member['user_id']))
		else:
			return '[ERROR] 目标群号错误或系统故障'
		if str(self_id) in memberlist:
			try:
				db = sqlite3.connect('qqbot.sqlite')
				cursor = db.cursor()
				lines = 20 if int(lines) > 20 else lines
				cursor.execute('''SELECT message FROM messages WHERE group_id = ? AND sender_id = ? ORDER BY timestamp DESC LIMIT ?''', (group_id, sender_id, lines))
				rows = cursor.fetchall()
				msg = '以下为QQ:%s在%s发送的最后%s条记录（如果有）：' % (sender_id, group_id, lines)
				for row in rows:
					msg += '\n%s' % (row[0])
				return msg
			except:
				db.close()
				return '[ERROR] 目标群号错误或系统故障'
		else:
			return '[ERROR] 你不在目标群中，你这个Stalker'
	except:
		return '[ERROR] 目标群号错误或系统故障'