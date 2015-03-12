#coding=utf-8
from contentFetch import StockTransWebParse
import time
from cMySql import CMySql


def neeqTranseTask(startDate,startDateEight,endDate,dbConnKey):
   x = StockTransWebParse(dbConnKey)
   
   print 'all stock'
   x.parseDataAllStock("http://www.neeq.cc/ajax/QTDM")
   

   print 'quoto'
   mysql = CMySql()
   mysql.setoptions(*dbConnKey)
   mysql.start()
   
   sql = u"delete from stockquoto where tradingday='" + startDateEight + "'"    
   mysql.insert(sql)      
   for a in range(200):
       #print a + 1     
      x.parseDataAllStockQuoto("http://www.neeq.cc/ajax/QTHangQin?qTType=0&currentPage=" + str(a+1) + "&sorttype=0")
   
   
   print 'report broker way'
   for a in range(2):
      x.parseData("http://www.neeq.cc/controller/GetDisclosureannouncementPage?type=1&company_cd=& \
      key=%E8%82%A1%E7%A5%A8%25%E5%81%9A%E5%B8%82&subType=0&startDate=" + startDate+ "&endDate=" + endDate + "&queryParams=0 \
      &page=" +str(a+1) + "&_=1423912635115",\
      u'\d+\s*[\u5e74]\s*\d+\s*[\u6708]\s*\d+\s*[\u65e5]')
   
   sql = u"delete from bondanalysis_xsbstockbroker where reportdate='" + startDate + "'"    
   mysql.insert(sql)      
   
   print 'broker'
   for a in range(2):
      x.parseDataZss("http://www.neeq.cc/controller/GetDisclosureannouncementPage?type=1&company_cd=& \
      key=%E8%82%A1%E7%A5%A8%25%E5%81%9A%E5%B8%82&subType=0&startDate=" + startDate+ "&endDate=" + endDate + "&queryParams=0 \
      &page=" +str(a+1) + "&_=1423912635115",\
      u'[\u505a][\u5e02][\u5546]\s*\d+\S*[\u8bc1][\u5238]',startDate)
   
   print 'preview'
   for a in range(10):
       #print a + 1     
      x.parseDataDshgg("http://www.neeq.cc/controller/GetDisclosureannouncementPage?type=1&company_cd= \
          &key=%E8%91%A3%E4%BA%8B%E4%BC%9A&subType=0&startDate=" + startDate+ "&endDate=" + endDate + "&queryParams=0 \
          &page="+ str(a+1) +"&_=1422968920464")
   
   mysql.close() 
   del x   
   

if __name__ == "__main__":
   startDate = time.strftime("%Y-%m-%d")
   startDateEight = time.strftime("%Y%m%d")
   endDate = startDate
   dbConnKey = ("localhost", "root", "root", "neeq", "utf8")
   
   neeqTranseTask(startDate,startDateEight,endDate, dbConnKey)


