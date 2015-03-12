#!/usr/bin/python
# -*- coding:utf-8 -*-
 
"""CMySql类，简单的MySQL增删改查
@version: 0.1
@author: 代码疯子
@contect: stackexploit[AT]gmail.com
@see: http://www.programlife.net/
"""
 
try:
    import MySQLdb
except ImportError:
    raise ImportError("[E]: MySQLdb module not found!")
 
class CMySql(object):
    def __init__(self):
        self.Option = {"host" : "", "password" : "", "username" : "", "database" : "","charset" : ""}
 
    def setoptions(self, host, pwd, user, db, charset):
        self.Option["host"] = host
        self.Option["password"] = pwd
        self.Option["username"] = user
        self.Option["database"] = db
        self.Option["charset"] = charset
    def start(self):
        try:
            self.db = MySQLdb.connect(
                        host = self.Option["host"],
                        user = self.Option["username"],
                        passwd = self.Option["password"],
                        db = self.Option["database"],
                        charset = self.Option["charset"]
            )
                    
        except Exception, e:
            print e
            raise Exception("[E] Cannot connect to %s" % self.Option["host"])
 
    def create(self, sqlstate):
        """
        @todo: sqlstate可以自己改成其他参数，下同
        """
        self.cursor = self.db.cursor()
        self.cursor.execute(sqlstate) #创建
        self.db.commit()
        self.cursor.close()
 
    def insert(self, sqlstate):
        """
        @todo: 虽然函数名是insert，不过增删改都行
        """
        self.cursor = self.db.cursor()
        self.cursor.execute(sqlstate) #增、删、改
        self.db.commit()
        self.cursor.close()
 
    def query(self, sqlstate):
        self.cursor = self.db.cursor()
        self.cursor.execute(sqlstate) #查
        qres = self.cursor.fetchall()
        self.cursor.close()
        return qres
 
    def one_query(self, sqlstate):
        self.cursor = self.db.cursor()
        self.cursor.execute(sqlstate) #查
        qres = self.cursor.fetchall()[0]
        self.cursor.close()
        return qres
 
    def close(self):
        self.db.close()
        
        
if __name__ == "__main__":
    print "test"
    cMySql = CMySql()
    cMySql.setoptions("localhost", "root", "root", "neeq")
    cMySql.start()
    cMySql.close()