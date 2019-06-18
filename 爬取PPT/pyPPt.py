from pyquery import PyQuery as pq
import requests
import os

#下载单个网页的PPT
def downUrl(url,filepath):
	print("downloading from url:"+url)
	doc = pq(url,encoding='gbk')
	a = doc("body > div > div.pleft.left > dl > dd > ul.downurllist >li>a")
	downUrl = a.attr("href")
	pptname = doc("body > div > div.pleft.left > dl > dd > div.ppt_info.clearfix > h1").text()
	filename = filepath+"/"+pptname+".zip"
	# filename = downUrl.split("/")[-1]
	r = requests.get(downUrl)
	if not os.path.exists(filepath):
		os.makedirs(filepath)
	with open(filename,'wb') as f:
	    f.write(r.content)
	print("PPT downloaded:"+filename)

#获取ppt的网页链接
def geturls(index):
	baseurl = 'http://www.1ppt.com'
	doc = pq(baseurl+"/moban/ppt_moban_"+index+".html")
	hrefs = doc("body > div.w.center.mt4  > dl.dlbox >dd >ul>li>a")
	urls =  []
	for item in hrefs.items():
	    prefs = item.attr('href')
	    urls.append(baseurl+str(prefs))
	return urls

if __name__ == '__main__':
	index = input("请输入需要爬取的页数:")
	urls = geturls(index)
	savepath = "./PPT"
	for url in urls:
		downUrl(url,savepath)




