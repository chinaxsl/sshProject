from django.db import models

# Create your models here.
from datetime import datetime
from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, InnerObjectWrapper, Completion, Keyword, Text
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer
from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=["localhost"])


class CustAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustAnalyzer("ik_max_word",filter=["lowercase"])


class ProjectType(DocType):
    #中标项目类型
    suggest = Completion(analyzer=ik_analyzer)
    location = Text(analyzer = "ik_max_word")
    title = Text(analyzer = "ik_max_word")
    date = Date()
    tags = Text(analyzer = "ik_max_word")
    content = Text(analyzer = "ik_max_word")
    object_id = Keyword()
    url = Keyword()
    from_website = Keyword
    class Meta:
        index = "ssh"
        doc_type = "project"
class Project(models.Model):
    #中标项目
    location = models.CharField('location',max_length=100)
    title = models.CharField('title',max_length=200)
    date = models.DateField('date')
    tags = models.CharField('tags',max_length=200)
    content = models.TextField()
    object_id = models.CharField('id',max_length=50,primary_key=True)
    url = models.CharField('url',max_length=300)
    from_website = models.CharField("from_website",max_length=200)
    def __str__(self):
        return self.title
    class Meta:
        db_table = "project"
        ordering = ['-date']

if __name__ == "__main__":
    ProjectType.init()