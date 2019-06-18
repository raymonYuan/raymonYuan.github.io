from pyquery import PyQuery as pq
from pymongo import MongoClient
import time
client = MongoClient("mongodb://localhost:27017")
db = client['lianjiapy']
tb_data = 'houses'

#返回地区
def getRegions(city):
	baseLj = "https://"+city+".lianjia.com/ershoufang/rs/"
	doc = pq(baseLj)
	div = doc("body > div > div > div.position > dl > dd > div:nth-child(1)")
	a = div.find('a').items()
	disticts = []
	col = db['districts']
	for i in a:
		dist = {
			"city":city,
			"dm":i.attr.href.split('/')[2],
			"name":i.text()
		}
		col.insert_one(dist)
		disticts.append(dist)
	return disticts

#返回url列表
def getUrls(city,region,num):
	baseurl = "https://"+city+".lianjia.com/ershoufang/"
	urllist = []
	for i in range(num):
		url = baseurl+region+'/pg'+str(i+1)+'/'
		urllist.append(url)
	return urllist

#获取url页面内容,并保存
def getData(city,district,urllist):
	col = db[city]
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
					"region":district ,
					"title": title,
					"totalPrice":price ,
					"unitprice":unitprice ,
					"square":square ,
					"houseType":houseType ,
					"frequence":frequence ,
				}
				col.insert_one(house)
		except Exception as e:
			#如果中途遇到报错则跳过
			print("!ERROR:"+url+"\nERROR-NUM：")
			print(e)
			continue


def saveData(city,num):
	col = db['districts']
	regions = getRegions(city)
	for region in regions:
		urls = getUrls(city,region['dm'],num)
		getData(city,region['name'],urls)
	db.close

