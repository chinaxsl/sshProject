# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi


class SshspiderPipeline(object):
    def process_item(self, item, spider):
        return item


    # 自定义Json文件导出
class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open('data.json','w',encoding='utf-8')
    def process_item(self, item, spider):
        date_str = str(item['date'])
        item['date'] = date_str
        lines  = json.dumps(dict(item),ensure_ascii=False) + '\n'
        self.file.write(lines)
        return item
    def spider_closed(self,spider):
        self.file.close()

    # 同步执行数据库插入操作
class MySQLPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect(host='127.0.0.1',port=3306,user='root',password='123456',db='sshspider',charset='utf8',use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql ="""
            insert into association_news(object_id,title,content,date,tags)
            Value(%s,%s,%s,%s,%s)
        """
        self.cursor.execute(insert_sql,(item['object_id'],item['title'],item['content'],item['date'],item['tags']))
        self.conn.commit()
        return item


    #异步执行数据库插入操作
class MySQLTwistedPipeline(object):
    def __init__(self,dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls,settings):
        dbparms = dict(
            host = settings['MYSQL_HOST'],
            db = settings['MYSQL_DBNAME'],
            user = settings['MYSQL_USER'],
            passwd = settings['MYSQL_PASSWORD'],
            charset = 'utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode = True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb",**dbparms)

        return cls(dbpool)


    def process_item(self, item, spider):
        #使用Twisted将MySQL插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert,item)
        query.addErrback(self.handle_error) #处理异常


    #异步插入的错误处理
    def handle_error(self,failure):
        print(failure)


    #插入操作
    def do_insert(self,cursor,item):
        #执行具体的插入
        #根据不同的item执行不同的sql语句
        insert_sql,params =item.get_insert_sql()
        cursor.execute(insert_sql, params)