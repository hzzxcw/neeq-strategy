# -*- coding: utf-8 -*- 

import sys  
reload(sys)  
sys.setdefaultencoding('utf-8')  
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import *
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
import re



class ParsePdf():
    def __init__(self,pdfUrl):
        fp = open(pdfUrl, 'rb') #'c:/a.pdf'
    
        #用文件对象来创建一个pdf文档分析器
        parser = PDFParser(fp)
        # 创建一个  PDF 文档 
        self.doc = PDFDocument(parser)
        # 提供初始化密码
        # 创建PDf 资源管理器 来管理共享资源
        rsrcmgr = PDFResourceManager()
        # 创建一个PDF设备对象
        laparams = LAParams()
        self.device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        self.interpreter = PDFPageInterpreter(rsrcmgr, self.device)
    
    def parsePdfText(self,reString):
        for page in PDFPage.create_pages(self.doc):
            self.interpreter.process_page(page)
            layout = self.device.get_result()
            s = ''
            for x in layout:
                #print type(x)
                #if(isinstance(x, LTFigure)):
                #    for z in x:
                #        print type(z)
                       
                if(isinstance(x, LTTextBoxHorizontal)):
                    #a = x.get_text().encode('gbk')
                    #print x.get_text()
                    txt = x.get_text()
                    if len(txt) > 0:
                        s = s + txt
            #print s
            match = re.findall(reString,s) #u'\d+\s+[\u5e74]\s+\d+\s+[\u6708]\s+\d+\s+[\u65e5]'
                        #print re.sub("\n", "", a)  
                        #i= i + 1
                        #print i
            if match:
                return match  
           
                            

	
