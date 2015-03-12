#coding=utf-8

import re
import urllib
import urllib2
import cookielib
import urllib,urllib2,cookielib
import re
import json
import os 
from parsePdf import ParsePdf
import datetime
from cMySql import CMySql
import time
import logging
import logging.config
import traceback
from hanzi2pinyin import hanzi2piny
from bs4 import BeautifulSoup

def callbackfunc(blocknum, blocksize, totalsize):
    '''回调函数
    @blocknum: 已经下载的数据块
    @blocksize: 数据块的大小
    @totalsize: 远程文件的大小
    '''
    percent = 100.0 * blocknum * blocksize / totalsize
    if percent > 100:
        percent = 100
    print "%.2f%%"% percentx
    
    
class WebParse:
    post_data=""#登陆提交的参数
    def __init__(self):
        '''初始化类，并建立cookies值'''
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-agent', 'User-Agent	Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0'),('Referer','http://www.cbrc.gov.cn/chinese/jrjg/')]
        urllib2.install_opener(opener)
            

    def login(self,loginurl,bianma):
        '''模拟登陆'''
        req = urllib2.Request(loginurl,self.post_data)
        _response = urllib2.urlopen(req)
        _d=_response.read()
        _d =_d.decode(bianma)
        return _d

    def getpagehtml(self,pageurl,bianma):
        '''获取目标网站任意一个页面的html代码'''
        req2=urllib2.Request(pageurl)
        _response2=urllib2.urlopen(req2)
        _d2=_response2.read()
        _d2 =_d2.decode(bianma)
        return _d2
        
    
    def getpagepdf(self,pageurl,name):
        '''获取目标网站任意一个页面的html代码'''    
        urllib.urlretrieve(pageurl, name)  

class StockTransWebParse(WebParse):
    _cMySql = None
    logging.config.fileConfig('logging.conf')
    _logger = logging.getLogger('simpleExample')
    
    def __init__(self, dbConnKey):
        WebParse.__init__(self)
        self._cMySql = CMySql()
        self._cMySql.setoptions(*dbConnKey)      
        
    def chineseDateToStandard(self,date):
        #print re.sub("\W","-",re.sub(" ", "", re.sub("\n", "", date)))
        tmpDate = re.sub("\W","-",re.sub(" ", "", re.sub("\n", "", date))).split('-')
        if (len(tmpDate[1]) == 1) and (len(tmpDate[2]) == 1):
            return tmpDate[0] + '-0' + tmpDate[1] + '-0' + tmpDate[2]
        elif (len(tmpDate[1]) == 1) and (len(tmpDate[2]) == 2):
            return tmpDate[0] + '-0' + tmpDate[1] + '-' + tmpDate[2]
        elif (len(tmpDate[1]) == 2) and (len(tmpDate[2]) == 1):
            return tmpDate[0] + '-' + tmpDate[1] + '-0' + tmpDate[2]   
        else:
            return tmpDate[0] + '-' + tmpDate[1] + '-' + tmpDate[2] 
        
    def parseDataDshgg(self,url):
        self._cMySql.start()
        returnJson = WebParse.getpagehtml(self,url,"utf-8")
        filePath = ''
        filename = ''
        code = ''
        publishDate = ''
        encodedjson = json.loads(returnJson)
        if encodedjson["disclosureInfos"]:
            for value1 in encodedjson["disclosureInfos"]:
                filePath = value1['filePath']
                filename = value1['companyName']
                code = value1['companyCode']
                publishDate = value1['publishDate'][:10]
                #publishDate = (datetime.datetime.strptime(value1['publishDate'], "%Y-%m-%dT%H:%M:%S") + datetime.timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S")[:10]
                WebParse.getpagepdf(self,"http://file.neeq.com.cn/upload" + filePath, filename + '.pdf')
                #print "http://file.neeq.com.cn/upload" + filePath
                oParsePdf = ParsePdf(filename + '.pdf')
                              
                #u'[\u516c][\u53f8][\u80a1][\u7968][\u7531][\u534f][\u8bae][\u8f6c][\u8ba9][\u65b9][\u5f0f][\u53d8][\u66f4][\u4e3a][\u505a][\u5e02][\u8f6c][\u8ba9][\u65b9][\u5f0f][\u7684][\u8bae][\u6848]'
                if oParsePdf.parsePdfText(u'[\u505a][\u5e02][\u8f6c][\u8ba9][\u65b9][\u5f0f]'):
                    sql = u"delete from bondanalysis_xsbstockinfo where preview='1' and code = '%s'" % (code)
                    self._cMySql.insert(sql)   
                    sql = u"insert into bondanalysis_xsbstockinfo(code,transeDate,inputDate,companyname,companycode,new,preview) \
                    values ('%s','%s','%s','%s','%s','%s','%s')" % (code,publishDate,publishDate,filename,code,'1','1')
                    self._cMySql.insert(sql)     
                    sql = u"update bondanalysis_xsbstockinfo set new='0' where preview='1' and code in (select code from code where codetype='做市')"
                    self._cMySql.insert(sql) 
                    #sql = u"update bondanalysis_xsbstockinfo set new='0' where preview='1' and code in (select code from bondanalysis_xsbstockinfo where preview='0')"
                    #self._cMySql.insert(sql)                      
                    #print code + ' ' + filename + '公司于' + publishDate + '董事会预公告转变交易方式为做市方式'
        self._cMySql.start()            
    def parseData(self,url,reString):
        self._cMySql.start()
        returnJson = WebParse.getpagehtml(self,url,"utf-8")
        filePath = ''
        filename = ''
        code = ''
        publishDate = ''
        encodedjson = json.loads(returnJson)
        if encodedjson["disclosureInfos"]:
            for value1 in encodedjson["disclosureInfos"]:
                filePath = value1['filePath']
                filename = value1['companyName'] or 'ext'
                titleFull = value1['titleFull']
                code = value1['companyCode']
                if (code <> '000000') and (titleFull.find(u'后续',0) < 0):
                    
                    
                #print code + ":" + titleFull                   
                    publishDate= datetime.datetime.strptime(value1['publishDate'], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%dT%H:%M:%S")[:10]
                    global evaluateDate                   
                    evaluateDate = (datetime.datetime.strptime(value1['publishDate'], "%Y-%m-%dT%H:%M:%S") + datetime.timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S")[:10]                   
                    WebParse.getpagepdf(self,"http://file.neeq.com.cn/upload" + filePath, filename + '.pdf')
                    #print "http://file.neeq.com.cn/upload" + filePath
                    try:
                        oParsePdf = ParsePdf(filename + '.pdf')
                        if oParsePdf.parsePdfText(reString):   
                            tmpDate = oParsePdf.parsePdfText(reString)[0]
                            #print tmpDate
                            evaluateDate = self.chineseDateToStandard(tmpDate)
                        else:
                            self._logger.warn(code.encode('gbk') + filename.encode('gbk')+' :转做市日期使用的是预测日期'.encode('gbk'))
                    except Exception,e:
                        self._logger.error(e)
                        self._logger.error(code.encode('gbk') + filename.encode('gbk')+' :程序出错，转做市日期使用的是预测日期'.encode('gbk'))
                    sql = u"delete from bondanalysis_xsbstockinfo where preview='0' and code = '%s'" % (code)
                    self._cMySql.insert(sql)                       
                    sql = u"insert into bondanalysis_xsbstockinfo(code,transeDate,inputDate,companyname,companycode,new,preview) \
                            values ('%s','%s','%s','%s','%s','%s','%s')" % (code,evaluateDate,publishDate,filename,code,'1','0')
                    self._cMySql.insert(sql)     
        sql = u"update bondanalysis_xsbstockinfo set new='0' where preview='0' and  code in (select code from code where codetype='做市')"
        self._cMySql.insert(sql)                     
        self._cMySql.close()           
    def parseDataZss(self,url,reString,date):
        self._cMySql.start()
        returnJson = WebParse.getpagehtml(self,url,"utf-8")
        filePath = ''
        filename = ''
        code = ''
        publishDate = ''
        encodedjson = json.loads(returnJson)
        if encodedjson["disclosureInfos"]:
            for value1 in encodedjson["disclosureInfos"]:
                filePath = value1['filePath']
                filename = value1['companyName']
                code = value1['companyCode']
                if filename:
                              
                    publishDate= (datetime.datetime.strptime(value1['publishDate'], "%Y-%m-%dT%H:%M:%S")).strftime("%Y-%m-%dT%H:%M:%S")[:10]
                    WebParse.getpagepdf(self,"http://file.neeq.com.cn/upload" + filePath, filename + '.pdf')
                    #print "http://file.neeq.com.cn/upload" + filePath
                    try:
                        oParsePdf = ParsePdf(filename + '.pdf')
                        #print filename
                        if oParsePdf.parsePdfText(reString):
                            group = oParsePdf.parsePdfText(reString)
                            for entry in group:
                                key = re.sub(r"\d","",re.sub(r"\s", "", re.sub("\n", "",  entry)))
                                sql = u"insert into bondanalysis_xsbstockbroker(code,broker,reportdate) values ('%s','%s','%s')" % (code,key[4:],publishDate)
                                self._cMySql.insert(sql)
                             
                                #print re.sub(" ", "", re.sub("\n", "",  entry))[5:]
                        else:
                            self._logger.warn(code.encode('gbk') + filename.encode('gbk')+' :做市商无法识别'.encode('gbk'))
                    except Exception,e:
                        self._logger.warn(e)
                        self._logger.warn(code.encode('gbk') + filename.encode('gbk')+' :做市商无法识别'.encode('gbk'))   
        self._cMySql.close()

    def parseDataAllStock(self,url):
        self._cMySql.start()
        returnJson = WebParse.getpagehtml(self,url,"utf-8")
        filePath = ''
        filename = ''
        code = ''
        publishDate = ''
        encodedjson = json.loads(returnJson)
        #print json.loads(encodedjson["remoteData"])
        if encodedjson["remoteData"]:
            sql = u"delete from code"             
            self._cMySql.insert(sql)              
            for value1 in json.loads(encodedjson["remoteData"])["codetable"]:
                filename = re.sub(r"\s", "",value1['ZQJC'])
                code = value1['ZQDM']
                lx = value1['ZRLXMC']
                hy = value1['HYZL']                
                sql = u"insert into code(code,name,codetype,industry,pinyin) values ('%s','%s','%s','%s','%s')" % (code,filename,lx,hy,hanzi2piny().multi_get_letter(filename))
                self._cMySql.insert(sql)

        self._cMySql.close()
        
    def parseDataAllStockQuoto(self,url):
        self._cMySql.start()
        returnJson = WebParse.getpagehtml(self,url,"utf-8")
        #print url
        filePath = ''
        filename = ''
        code = ''
        publishDate = ''
        encodedjson = json.loads(returnJson)
        #print json.loads(encodedjson["remoteData"])
        if encodedjson["remoteData"]:
            #sql = u"delete from stockquoto"    
            #print json.loads(encodedjson["remoteData"])["quotes"]
            #print json.loads(encodedjson["remoteData"])["status"]
            #self._cMySql.insert(sql)     
            if json.loads(encodedjson["remoteData"])["status"] == 0:
                for value1 in json.loads(encodedjson["remoteData"])["quotes"]:
                    tradingDay = value1['date']
                    code = value1['ZQDM']
                    lclosePrice = value1['ZRSP']
                    openPrice = value1['JRKP']
                    closePrice = value1['ZJCJ']
                    highPrice = value1['ZGCJ']
                    lowPrice = value1['ZDCJ']
                    amount = value1['CJJE']   
                    rise = value1['JSD1']
                    dyield = value1['JSDF']                     
                    sql = u"insert into stockquoto(tradingday,code,open,close,high,low,lclose,amount,rise,yield) values ('%s','%s',%s,%s,%s,%s,%s,%s,%s,%s)" %     \
                        (tradingDay,code,openPrice,closePrice,highPrice,lowPrice,lclosePrice,amount,rise,dyield)
                    
                    #print sql                    
                    self._cMySql.insert(sql)                


        self._cMySql.close()
        
if __name__ == '__main__':
    #urllib.urlretrieve("http://www.cbrc.gov.cn/chinese/jrjg/index.html", 'c:/2.html')
    html_doc = urllib2.urlopen("http://www.cbrc.gov.cn/chinese/jrjg/index.html",timeout=10).read() 
    print len(html_doc)
    #print html_doc
    soup = BeautifulSoup(html_doc)
    
    shangs = soup.find_all("div",class_="zi")
    wais = soup.select("[class~=wai] a")
    num = 0
    a=[]
    for shang in shangs:
        a.append(re.sub("\s","",shang.string))

    b = []
    c = []
    for s in wais:
        if re.sub("\s","",s.string) == "更多>>":
            print "++++++++++++++++++++++++++++++++++" + a[num] + "++++++++++++++++++++++++++++++++++"
            num += 1   
        try:
            c.index(re.sub("\s","",s.string))
        except:
            c.append(re.sub("\s","",s.string))
            if re.sub("\s","",s.string) <> "更多>>":
                print re.sub("\s","",s.string)
    
