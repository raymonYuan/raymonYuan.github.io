#coding=utf-8
from __future__ import unicode_literals
from pyquery import PyQuery as pq
from pymongo import MongoClient
import re
import jieba.analyse
import pyecharts
import time
client = MongoClient("mongodb://localhost:27017")
db = client['lianjia']
tb_data = 'houses'
#from  pyecharts import Bar
#组装url
def getUrls(region,num):
	baseurl = "https://wh.lianjia.com/ershoufang/"
	urllist = []
	for i in range(num):
		url = baseurl+region+'/pg'+str(i+1)+'/'
		urllist.append(url)
	return urllist

#获取url页面内容,并保存
def getData(urllist):
	col = db[tb_data]
	for url in urllist:
		time.sleep(3)
		try:
			doc = pq(url,timeout=1)
			print ("now get data from :"+url)
			a = doc("body > div.content > div.leftContent > ul > li")
			for item in a.items():
				price = item.find(" div.info.clear > div.priceInfo > div.totalPrice > span").html()#总价
				title = item.find(" div.info.clear > div.title > a").html()#标题
				infos = item.find(" div.info.clear > div.address > div").text().split("|")
				address = infos[0]#小区
				houseType = infos[1]#户型
				square = infos[2].replace("平米",'')#面积
				unitprice = item.find(" div.info.clear > div.priceInfo > div.unitPrice > span").text()#单价
				followInfo = item.find("div.info.clear > div.followInfo").text().split("/")
				frequence = followInfo[1] #带看次数
				house={
					"region":region['name'] ,
					"title": title,
					"totalPrice":price ,
					"unitprice":unitprice ,
					"square":square ,
					"houseType":houseType ,
					"frequence":frequence ,
				}
				x = col.insert_one(house)
		except Exception as e:
			#如果中途遇到报错则跳过
			print("!ERROR:"+url+"\nERROR-NUM：")
			print(e)
			continue

#计算区域单价
def calUnitPrice(regions):
	col = db[tb_data]
	xattr = []
	value = []
	for region in regions:
		try:
			sum = 0
			count = 0
			xattr.append(region['name'])
			unitprices = col.find({"region":region['name']},{"unitprice":1}) 
			# print(region['name'])
			for i in unitprices:
				sum +=  int(re.search('(\d+)',i['unitprice'])[0])
				# print(type(re.findall('(\d+)',i['unitprice'])))
				count += 1
			value.append(round(sum/count))
		except Exception as e:
			print (e)
			value.append(0)
			continue
	print(xattr)
	print(value)
	bar = pyecharts.Bar("各区房价对比")
	# x = sum(value)
	# print (x )
	bar.add("武汉",xattr,value,xaxis_interval=0, xaxis_rotate=30,label_text_color=["#000"],
		label_color=['#ADFF2F'],is_label_show=True, label_text_size=14)
	# bar.add("武汉", xattr, value, is_convert=False, is_label_show=True, label_text_size=18, is_random=True,
 #                xaxis_interval=0, xaxis_rotate=20,
 #                legend_text_size=18, label_text_color=["#000"])
	# bar.use_theme('dark')
	bar.render() 
#房价区间
def getPriceQJ(regions):
	xattr = []
	valueMin = []
	valueMax = []
	col = db[tb_data]
	for region in regions:
		try:
			xattr.append(region['name'])
			unitprices = col.find({"region":region['name']},{"unitprice":1}) 
			regionPrices = []
			for i in unitprices:
				regionPrices.append(int(re.search('(\d+)',i['unitprice'])[0]))
			valueMin.append(min(regionPrices))
			valueMax.append(max(regionPrices))
		except Exception as e:
			print (e)
			valueMin.append(0)
			valueMax.append(0)
			continue 
	print(valueMax)
	bar = pyecharts.Bar(" ")
	# 利用第一个 add() 图例的颜色为透明，即 'rgba(0,0,0,0)'，并且设置 is_stack 标志为 True
	bar.add("", xattr, valueMin, label_color=['rgba(0,0,0,0)'], is_stack=True)
	bar.add("武汉", xattr, valueMax, is_label_show=True, is_stack=True, 
		label_pos='inside',xaxis_interval=0, xaxis_rotate=30,)
	bar.use_theme('dark')
	bar.render()

#区域房源数量对比
def getDistrictCount(regions):
	col = db[tb_data]
	xattr = []
	value = []
	for region in regions:
		xattr.append(region['name'])
		counts = col.find({"region":region['name']},{"unitprice":1}).count()
		value.append(counts)
	print(xattr)
	print(value)
	bar = pyecharts.Bar("样本数量")
	bar.add("武汉",xattr,value,xaxis_interval=0, xaxis_rotate=30,is_label_show=True, label_text_size=14)
	bar.render() 

#看房次数对比 Pie 
def distFrequnce(regions):
	col = db[tb_data]
	xattr = []
	value = []
	toltalsum = 0
	for region in regions:
		sum = 0
		counts = 0
		xattr.append(region['name'])
		freqs =  col.find({"region":region['name']},{"frequence":1})
		for  freq in freqs:
			sum += int(re.search('(\d+)',freq['frequence'])[0])
			counts += 1
		value.append(sum/counts)
	pie = pyecharts.Pie("看房次数占比")
	# for i in value:
	# 	toltalsum += i
	# print(toltalsum)
	pie.add("看房次数", xattr, value, radius=[40, 75],
    label_text_color=None,
    is_label_show=True,
    legend_orient="vertical",
    legend_pos="left")
	pie.render()
def houseType():
	col = db[tb_data]
	xattr = []
	value = []
	counts = {}#dict保存数据
	types = col.find({},{"houseType":1})
	for t in types:
		word = t['houseType']
		if not word in counts.keys():
			counts[word] = 0
		counts[word]=counts[word] + 1
		# print(t)
	items = list(counts.items())
	items.sort(key=lambda x:x[1],reverse=True)
	for i in range(10):
		word,count = items[i]
		xattr.append(word)
		value.append(count)
	pie = pyecharts.Pie("户型对比")
	pie.add(
    "武汉",
    xattr,
    value,
    center=[75, 50],
    is_random=True,
    radius=[30, 75],
    rosetype="area",
    is_legend_show=False,
    is_label_show=True,)
	pie.render()

def loanbar(regions):
	col = db[tb_data]
	xattr = []
	value = [7731,6984,5674,8917,7732,8168,6547,7358,5487,3492,4739,2993,5737,7857]
	for region in regions:
		xattr.append(region['name'])
	# print(xattr)
	bar = pyecharts.Bar("平均80平月供")
	bar.add("武汉",xattr,value,xaxis_interval=0, xaxis_rotate=30,
		label_color=['#008B8B'],is_label_show=True, label_text_size=14)
	bar.render()

def priceMap(regions):
	col = db[tb_data]
	xattr = []
	value = []
	for region in regions:
		try:
			sum = 0
			count = 0
			xattr.append(region['name'].strip()+"区")
			unitprices = col.find({"region":region['name']},{"unitprice":1}) 
			# print(region['name'])
			for i in unitprices:
				sum +=  int(re.search('(\d+)',i['unitprice'])[0])
				# print(type(re.findall('(\d+)',i['unitprice'])))
				count += 1
			value.append(round(sum/count))
		except Exception as e:
			print (e)
			value.append(0)
			continue
	print(xattr)
	print(value)
	map = pyecharts.Map("武汉", width=800, height=800)
	map.add("武汉", xattr, value, maptype='武汉', is_label_show=True,
		is_visualmap=True,visual_range=[min(value), max(value)],is_map_symbol_show=False, visual_text_color="#000")
	map.render()

def wordCloud(regions):
	words = ''
	col = db[tb_data]
	for region in regions:
		tiltes = col.find({"region":region['name']},{"title":1}) 
		for title in tiltes:
			words += title['title']
	# print(words)
	# 基于TF-IDF算法的关键字抽取, topK返回频率最高的几项, 默认值为20, withWeight
    # 为是否返回关键字的权重
	tags = jieba.analyse.extract_tags(words, topK=100, withWeight=True)
	keys = []
	values = []
	for tag in iter(tags):
		keys.append(tag[0])
		values.append(tag[1])
	wordcloud = pyecharts.WordCloud(width=1300, height=620)
	wordcloud.add("", keys, values, word_size_range=[20, 100])
	wordcloud.render()


if __name__ == '__main__':
	col = db['districts']
	num = 50
	regions = col.find({},{"_id":0})
	houseType()
	db.close



