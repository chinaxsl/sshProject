from datetime import datetime

import copy
from django.shortcuts import render
from django.views.generic.base import View
from search.models import ProjectType,Project
from django.http import HttpResponse
import json
from elasticsearch import Elasticsearch
import datetime
# Create your views here.
client = Elasticsearch(hosts=['localhost'])
page_items_num = 15
def date2int(value):
    convert_dict = {"天":1,"周":7,"月":30,"年":365}
    if value in convert_dict.keys():
        num  = convert_dict[value]
    else :
        return 1
    return num

def getBody(key_words,from_website,page,area='',date=''):
    body = {
        "query": {
            "bool": {
                "must": [{"match_all": {}}],
                "filter": {}
            }},
        "from": 0,
        "size": 15,
        "highlight": {
            "pre_tags": ['<span class="keyWord">'],
            "post_tags": ["</span>"],
            "fields": {
                "title": {},
                "content": {}
            }
        },
        "sort": [{"date": {"order": "desc"}}]
    }
    if (key_words):
        body['query']['bool']['must'] = [{
            "multi_match": {
                "query": key_words,
                "fields": ["tags", "title", "content"]
            }}]
    if (from_website):
        website_dict = {"term": {"from_website": from_website}}
        body['query']['bool']['filter'] = {"bool": {"must": [website_dict]}}
    if (area):
        area_dict = {"term": {"location": area}}
        if (from_website):
            must_list = body['query']['bool']['filter']['bool']['must']
            must_list.append(area_dict)
        else:
            body['query']['bool']['filter'] = {"bool": {"must": [area_dict]}}
    if (date):
        begin_day = "now-%dd/d" % (date2int(date))
        date_dict = {"range": {"date": {"lt": "now/d", "gte": begin_day}}}
        if from_website or area:
            must_list = body['query']['bool']['filter']['bool']['must']
            must_list.append(date_dict)
        else:
            body['query']['bool']['filter'] = {"bool": {"must": [date_dict]}}
    body['from'] = (page - 1) * page_items_num
    body['size'] = page_items_num
    return body

def getCompanyBody(key_words, from_website, page, area='', type=''):
    body = {
        "query": {
            "bool": {
                "must": [{"match_all": {}}],
                "filter": {}
            }},
        "from": 0,
        "size": 15,
        "highlight": {
            "pre_tags": ['<span class="keyWord">'],
            "post_tags": ["</span>"],
            "fields": {
                "company_name": {},
                "company_main_industry": {}
            }
        },
        "sort": [{"company_crawltime": {"order": "desc"}}]
    }
    if (key_words):
        body['query']['bool']['must'] = [{
            "multi_match": {
                "query": key_words,
                "fields": ["company_name", "company_main_industry"]
            }}]
    if (from_website):
        website_dict = {"term": {"from_website": from_website}}
        body['query']['bool']['filter'] = {"bool": {"must": [website_dict]}}
    if (area):
        area_dict = {"term": {"company_detailed_location": area}}
        if (from_website):
            must_list = body['query']['bool']['filter']['bool']['must']
            must_list.append(area_dict)
        else:
            body['query']['bool']['filter'] = {"bool": {"must": [area_dict]}}
    if (type):
        type_dict = {"term": {"company_type": type}}
        if from_website or area:
            must_list = body['query']['bool']['filter']['bool']['must']
            must_list.append(type_dict)
        else:
            body['query']['bool']['filter'] = {"bool": {"must": [type_dict]}}
    body['from'] = (page - 1) * page_items_num
    body['size'] = page_items_num
    return body

class SearchSuggest(View):
    def get(self,request):
        key_words = request.GET.get('s','')
        re_datas = []
        if key_words:
            s = ProjectType.search()
            s = s.suggest('my_suggest',key_words,completion={
                "field":"suggest","fuzzy":{
                    "fuzziness":2
                }
            })
            suggestions = s.execute_suggest()
            for match in suggestions.my_suggest[0].options:
                source = match._source
                re_datas.append(source['title'])
        return HttpResponse(json.dumps(re_datas),content_type="application/json")

class SearchView(View):
    def get(self,request):
        key_words = request.GET.get("q","")
        page = request.GET.get("p","1")
        try:
            page = int(page)
        except:
            page = 1
        start_time = datetime.now()
        response = client.search(
            index="ssh",
            body={
                "query":{
                    "multi_match":{
                        "query":key_words,
                        "fields":["tags","title","content"]
                    }
                },
                "from":(page-1)*10,
                "size":10,
                "highlight":{
                    "pre_tags": ['<span class="keyWord">'],
                    "post_tags": ["</span>"],
                    "fields":{
                        "title":{},
                        "content":{}
                    }
                }
            }
        )
        # jobbole_count = redis_cli.get("jobbole_count")
        end_time = datetime.now()
        last_time = (end_time - start_time).total_seconds()
        total_nums = response["hits"]["total"]
        if (page%10)>0:
            page_nums = int(total_nums/10)+1
        else:
            page_nums = int(total_nums/10)
        hit_list = []
        for hit in response["hits"]["hits"]:
            hit_dict = {}
            try:
                hit_dict["title"]="".join(hit["highlight"]["title"])
            except:
                hit_dict["title"]="".join(hit["_source"]["title"])
            try:
                hit_dict["content"] = "".join(hit["highlight"]["content"][:500])
            except:
                hit_dict["content"] = "".join(hit["_source"]["content"][:500])
            hit_dict["date"] = hit["_source"]["date"]
            hit_dict["url"] = hit["_source"]["url"]
            hit_dict["score"] = hit["_score"]

            hit_list.append(hit_dict)
        return render(request,"result.html",{"all_hits":hit_list,
                                             "total_nums":total_nums,
                                             "page":page,
                                             "page_nums":page_nums,
                                             "key_words":key_words,
                                             "last_time":last_time})

class ListView(View):
    def get(self,request):
        key_words = request.GET.get("q","")
        from_website = request.GET.get("from","")
        area = request.GET.get("area","")
        date = request.GET.get("date","")
        page = request.GET.get("p","1")
        try:
            page = int(page)
        except:
            page = 1
        body = getBody(key_words,from_website,page,area=area,date = date)
        response = client.search(
            index="ssh",
            doc_type="project",
            body=body
        )
        total_nums = response["hits"]["total"]
        projects_list = []
        for hit in response["hits"]["hits"]:
            hit_dict = {}
            try:
                hit_dict["title"]="".join(hit["highlight"]["title"])
            except:
                if 'title' not in hit["_source"].keys():
                    continue
                hit_dict["title"]="".join(hit["_source"]["title"])
            try:
                hit_dict["content"] = "".join(hit["highlight"]["content"][:100])
            except:
                hit_dict["content"] = "".join(hit["_source"]["content"][:100])
            hit_dict["date"] = hit["_source"]["date"]
            hit_dict["url"] = hit["_source"]["url"]
            hit_dict["from_website"] = hit["_source"]["from_website"]
            hit_dict["tags"] = hit["_source"]["tags"]
            hit_dict["location"] = hit["_source"]["location"]
            projects_list.append(hit_dict)
        return render(request,"list.html",{"projects_list":projects_list,
                                             "total_nums":total_nums,
                                             "page":page,
                                             "page_items_num":page_items_num,
                                             "key_words":key_words})

class AssociationView(View):
    def get(self,request):
        key_words = request.GET.get("q","")
        from_website = request.GET.get("from","")
        date = request.GET.get("date","")
        page = request.GET.get("p","1")
        try:
            page = int(page)
        except:
            page = 1
        body = getBody(key_words,from_website,page,date=date)
        response = client.search(
            index="ssh",
            doc_type="association_news",
            body=body
        )

        total_nums = response["hits"]["total"]
        association_list = []
        for hit in response["hits"]["hits"]:
            hit_dict = {}
            try:
                if 'title' not in hit["_source"].keys():
                    continue
                hit_dict["title"]="".join(hit["highlight"]["title"])
            except:
                hit_dict["title"]="".join(hit["_source"]["title"])
            try:
                hit_dict["content"] = "".join(hit["highlight"]["content"][:500])
            except:
                hit_dict["content"] = "".join(hit["_source"]["content"][:500])
            hit_dict["date"] = hit["_source"]["date"]
            try:
                hit_dict["url"] = hit["_source"]["url"]
            except:
                hit_dict["url"] = "$"
            hit_dict["from_website"] = hit["_source"]["from_website"]
            hit_dict["tags"] = hit["_source"]["tags"]
            association_list.append(hit_dict)


        return render(request, "assciation.html", {"association_list":association_list,
                                             "total_nums":total_nums,
                                             "page":page,
                                             "page_items_num":page_items_num,
                                             "key_words":key_words})

class CompanyView(View):

    def get(self,request):
        key_words = request.GET.get("q", "")
        from_website = request.GET.get("from", "")
        type = request.GET.get("type", "")
        page = request.GET.get("p", "1")
        area = request.GET.get("area", "")
        try:
            page = int(page)
        except:
            page = 1
        body = getCompanyBody(key_words,from_website,page = page,area=area,type=type)
        response = client.search(
            index="ssh",
            doc_type="company",
            body=body
        )
        total_nums = response["hits"]["total"]
        company_list = []
        for hit in response["hits"]["hits"]:
            hit_dict = {}
            try:
                if 'company_name' not in hit["_source"].keys():
                    continue
                hit_dict["company_name"]="".join(hit["highlight"]["company_name"])
            except:
                hit_dict["company_name"]="".join(hit["_source"]["company_name"])
            try:
                hit_dict["company_main_industry"] = "".join(hit["highlight"]["company_main_industry"])
            except:
                hit_dict["company_main_industry"] = "".join(hit["_source"]["company_main_industry"])
            hit_dict["company_register_time"] = hit["_source"]["company_register_time"]
            try:
                hit_dict["url"] = hit["_source"]["url"]
            except:
                hit_dict["url"] = "#"
            hit_dict["company_detailed_location"] = hit["_source"]["company_detailed_location"]
            hit_dict["company_money"] = hit["_source"]["company_money"]
            hit_dict["from_website"] = hit["_source"]["from_website"]
            hit_dict["company_type"] = hit["_source"]["company_type"]
            try:
                hit_dict["company_crawltime"] = hit["_source"]["company_crawltime"]
            except:
                hit_dict["company_crawltime"] = ''
            company_list.append(hit_dict)
        return render(request, "company.html", {"company_list":company_list,
                                             "total_nums":total_nums,
                                             "page":page,
                                             "page_items_num":page_items_num,
                                             "key_words":key_words})
class CompetitionView(View):
    def get(self,request):
        key_words = request.GET.get("q","")
        page = request.GET.get("p","1")
        from_website = request.GET.get("from","")
        date = request.GET.get("date","")
        page_items_num = 15
        try:
            page = int(page)
        except:
            page = 1

        body = getBody(key_words,from_website,page,date=date)

        response = client.search(
            index="ssh",
            doc_type="xuluren_news",
            body=body
        )
        total_nums = response["hits"]["total"]
        xiuluren_list = []
        for hit in response["hits"]["hits"]:
            hit_dict = {}
            try:
                hit_dict["title"]="".join(hit["highlight"]["title"])
            except:
                hit_dict["title"]="".join(hit["_source"]["title"])
            try:
                hit_dict["content"] = "".join(hit["highlight"]["content"][:500])
            except:
                hit_dict["content"] = "".join(hit["_source"]["content"][:500])
            hit_dict["date"] = hit["_source"]["date"]
            try:
                hit_dict["url"] = hit["_source"]["url"]
            except:
                hit_dict["url"] = "$"
            hit_dict["from_website"] = hit["_source"]["from_website"]
            hit_dict["tags"] = hit["_source"]["tags"]
            xiuluren_list.append(hit_dict)
        return render(request, "competition.html", {"xiuluren_list":xiuluren_list,
                                             "total_nums":total_nums,
                                             "page":page,
                                             "page_items_num":page_items_num,
                                             "key_words":key_words})
