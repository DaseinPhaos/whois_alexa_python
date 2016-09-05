"""
##Introduction
A simple module used to fetch information about websites
using data from http://www.alexa.com

##Requirement
--------
**python 3**
**requests** 2.1.0 + by Kenneth Reitz : https://github.com/kennethreitz/requests/

Example
--------
Fetch website information about google.com:
```
import alexa
import json
info = alexa.get_website_info("google.com")
print(json.dumps(info, indent=2))
# now the information fetched shall be printed out neetly and nicely.
```
"""

import requests
import html.parser as htmlparser
import json

_base_url = "http://www.alexa.com/siteinfo/"

class _parser_impl_base():
    def __init__(self, target_data):
        self._parsed_data = target_data

    def handle_starttag(self, tag, attrs):  return
    
    def handle_data(self, data): return
    
    def handle_endtag(self, tag): return


class _gender_parser(_parser_impl_base):
    def __init__(self, target_dict):
        self._parsed_data = target_dict
        self._parsed_data["visitor gender"]={}
        self._parsed_data["visitor education"] = {}
        self._parsed_data["visitor location"] = {}
        self._rb = False
        self._l = 0

    def handle_starttag(self, tag, attrs):
        if self._rb == True:
            if tag == "span" and len(attrs)==1 and attrs[0][0] == "style":
                self._l += int(attrs[0][1].split(":")[1].split("%")[0])

    def handle_data(self, data):
        if data == "Male":
            self._rb = True
            self._l = 0
        elif data == "Female":
            #global self._parsed_data
            self._parsed_data["visitor gender"]['male'] = str(self._l / 200.0)
            self._l = 0
        elif data == "No College":
            #global self._parsed_data
            self._parsed_data["visitor gender"]['female'] = str(self._l / 200.0)
            self._l = 0
        elif data == "Some College":
            #global self._parsed_data
            self._parsed_data["visitor education"]['no college'] = str(self._l / 200.0)
            self._l = 0
        elif data == "Graduate School":
            #global self._parsed_data
            self._parsed_data["visitor education"]['some college'] = str(self._l / 200.0)
            self._l = 0
        elif data == "College":
            #global self._parsed_data
            self._parsed_data["visitor education"]['graduate'] = str(self._l / 200.0)
            self._l = 0
        elif data == "Home":
            #global self._parsed_data
            self._parsed_data["visitor education"]['college'] = str(self._l / 200.0)
            self._l = 0
        elif data == "School":
            #global self._parsed_data
            self._parsed_data["visitor location"]['home'] = str(self._l / 200.0)
            self._l = 0
        elif data == "Work":
            #global self._parsed_data
            self._parsed_data["visitor location"]['school'] = str(self._l / 200.0)
            self._l = 0
        elif data == "Login with Facebook":
            #global self._parsed_data
            self._parsed_data["visitor location"]['work'] = str(self._l / 200.0)
            self._l = 0


class _loadspeed_parser(_parser_impl_base):
    def __init__(self, target_dict):
        self._parsed_data = target_dict
        self._ready = True

    def handle_starttag(self, tag, attrs):
        if tag == "div" and len(attrs) > 0 and attrs[0] == ("class", "row-fluid col-pad pybar demo-gender"):
            return _gender_parser(self._parsed_data)

    def handle_data(self, data):
        if data.strip() == "": return
        if self._ready == True:
            ##global self._parsed_data
            self._parsed_data['loadspeed'] = data.strip()
            self._ready = False


class _subdomain_parser(_parser_impl_base):
    def __init__(self, target_dict):
        self._parsed_data = target_dict
        self._index = -1
        self._ready = False
        self._parsed_data['subdomains'] = {}

    def handle_starttag(self, tag, attrs):
        if self._index < 9 and tag == "span":
            self._ready = True
        if tag == "section" and len(attrs) > 0 and attrs[0] == ("id", "loadspeed-panel-content"):
            return _loadspeed_parser(self._parsed_data)

    
    def handle_data(self, data):
        if data.strip() == "": return
        if self._ready == True:
            self._index += 1
            if self._index % 2 == 0:
                self._k = data.strip()
            else:
                self._parsed_data['subdomains'][self._k] = data.strip()
                self._ready = False


class _related_tbody_parser(_parser_impl_base):
    def __init__(self, target_dict):
        self._parsed_data = target_dict
        self._ready = False
        self._index = 0
        self._tbody_met = False
        self._parsed_data['related sites'] = []
    
    def handle_starttag(self, tag, attrs):
        if self._index < 10 and tag == "a":
            self._ready = True
        if tag == "tbody":
            if self._tbody_met == True: 
                return _subdomain_parser(self._parsed_data)
            else: self._tbody_met = True

    def handle_data(self, data):
        if self._ready == True:
            self._parsed_data['related sites'].append(data.strip())
            self._index += 1
            self._ready = False


class _related_content_parser(_parser_impl_base):
    def handle_starttag(self, tag, attrs):
        if tag == "tbody":
            return _related_tbody_parser(self._parsed_data)

class _linksin_parser(_parser_impl_base):
    def __init__(self, target_dict):
        self._parsed_data = target_dict
        self._ready = False

    def handle_starttag(self, tag, attrs):
        if tag == "span" and len(attrs) > 0 and attrs[0] == ("class", "font-4 box1-r"):
            self._ready = True
        elif tag == "section" and len(attrs) > 0 and attrs[0] == ("id", "related-content"):
            return _related_content_parser(self._parsed_data)

    def handle_data(self, data):
        if self._ready == True:
            self._parsed_data["total sites linking in"] = data
            self._ready = False

class _upstream_tbody_parser(_parser_impl_base):
    def __init__(self, target_dict):
        self._parsed_data = target_dict
        self._index = -1
        self._k_ready = False
        self._v_ready = False
        self._parsed_data['upstreams'] = {}

    def handle_starttag(self, tag, attrs):
        if self._index < 5:
            if tag == "a": self._k_ready = True
            elif tag == "span" and len(attrs) == 1 and attrs[0] == ("class", ""):
                self._v_ready = True
        elif tag == "section" and len(attrs) > 0 and attrs[0] == ("id", "linksin-panel-content"):
            return _linksin_parser(self._parsed_data)
    
    def handle_data(self, data):
        if data.strip() == "": return
        if self._k_ready == True:
            self._index += 1
            self._k = data
            self._k_ready = False
        elif self._v_ready == True:
            self._parsed_data['upstreams'][self._k] = data.strip()
            self._v_ready = False
    

class _keyword_tbody_parser(_parser_impl_base):
    def __init__(self, target_dict):
        self._parsed_data = target_dict
        self._index = -1
        self._ready = False
        self._parsed_data['keywords'] = {}

    def handle_starttag(self, tag, attrs):
        if tag == "td" and len(attrs) == 2:
            self._k = attrs[1][1]
        elif tag == "span" and len(attrs) == 1 and attrs[0] == ("class", ""):
            self._ready = True
        elif tag == "tbody":
            return _upstream_tbody_parser(self._parsed_data)
    
    def handle_data(self, data):
        if self._ready == True:
            self._parsed_data['keywords'][self._k] = data.strip()
            self._ready = False


class _keyword_table_parser(_parser_impl_base):
    def __init__(self, target_dict):
        self._parsed_data = target_dict
        self._ready = False

    def handle_starttag(self, tag, attrs):
        if tag == "table" and len(attrs) > 2 and attrs[2] == ("id", "keywords_top_keywords_table"):
            self._ready = True
        elif self._ready == True and tag == 'tbody':
            return _keyword_tbody_parser(self._parsed_data)


class _engagement_parser(_parser_impl_base):
    def __init__(self, target_dict):
        self._parsed_data = target_dict
        self._index = 0
        self._ready = False
        self._parsed_data["user engagement"] = {}

    def handle_starttag(self, tag, attrs):
        if tag == "strong":
            self._index += 1
            self._ready = True
        
    def handle_data(self, data):
        if self._ready == True:
            #global self._parsed_data
            if self._index == 1:
                self._parsed_data["user engagement"]["bounce rate"] = data.strip()
            elif self._index == 2:
                self._parsed_data["user engagement"]["daily pageviews per visitor"] = data.strip()
            else:
                self._parsed_data["user engagement"]["daily time on site"] = data.strip()


    def handle_endtag(self, tag):
        self._ready = False
        if self._index == 3:
             return _keyword_table_parser(self._parsed_data)


class _engagement_content_parser(_parser_impl_base):
    def handle_starttag(self, tag, attrs):
        if tag == "section" and len(attrs) > 0 and attrs[0] == ("id", "engagement-content"):
            return _engagement_parser(self._parsed_data)


class _visitor_tbody_parser(_parser_impl_base):
    def __init__(self, target_dict):
        self._parsed_data = target_dict
        self._index = -1
        self._buffer = {}
        self._parsed_data["visitor by country"] = []

    
    def handle_data(self, data):
        if data.strip() == "": return
        self._index += 1
        if self._index % 3 == 0:
            self._buffer["country"] = data[2:]
        elif self._index % 3 == 1:
            self._buffer["percentage"] = data
        elif self._index % 3 == 2:
            self._buffer["rank in country"] = data
            self._parsed_data["visitor by country"].append(self._buffer)
            self._buffer = {}

    def handle_endtag(self, tag):
        if tag == "tbody":
            return _engagement_content_parser(self._parsed_data)


class _visitor_table_parser(_parser_impl_base):
    def __init__(self, target_dict):
        self._parsed_data = target_dict
        self._ready = False

    def handle_starttag(self, tag, attrs):
        if tag == "table" and len(attrs) > 2 and attrs[2] == ("id", "demographics_div_country_table"):
            self._ready = True
        elif self._ready == True and tag == "tbody":
            return _visitor_tbody_parser(self._parsed_data)

class _local_rank_parser(_parser_impl_base):
    def __init__(self, target_dict):
        self._parsed_data = target_dict
        self._ready = False
        self._final = False

    def handle_starttag(self, tag, attrs):
        if tag == "strong" and self._final == False:
            self._ready = True

    def handle_data(self, data):
        if data.strip() == "": return
        if self._ready == True:
            #global self._parsed_data
            self._parsed_data["rank"]["local"] = data.strip()
            self._ready = False
            self._final = True

    def handle_endtag(self, tag):
        if tag == "strong": return _visitor_table_parser(self._parsed_data)

class _global_rank_parser(_parser_impl_base):
    def __init__(self, target_dict):
        self._parsed_data = target_dict
        self._ready = False
        self._final = False
    
    def handle_starttag(self, tag, attrs):
        if tag == "strong" and self._final == False:
            self._ready = True
        elif tag == "span" and len(attrs) > 0 and attrs[0] == ("class", "bottom"):
            return _local_rank_parser(self._parsed_data)

    def handle_data(self, data):
        if data.strip() == "": return
        if self._ready == True:
            self._parsed_data["rank"] = {}
            self._parsed_data["rank"]["global"] = data.strip()
            self._ready = False
            self._final = True


class _rank_sec_parser(_parser_impl_base):
    def handle_starttag(self, tag, attrs):
        if tag == "span" and len(attrs) > 0 and attrs[0] == ("class", "bottom"):
            return _global_rank_parser(self._parsed_data)

class _root_parser(_parser_impl_base):
    def handle_starttag(self, tag, attrs):
        if tag == "div" and len(attrs) > 0 and attrs[0] == ("class", "row-fluid summary"):
                return _rank_sec_parser(self._parsed_data)

class _AlexaHTMLParser(htmlparser.HTMLParser):
    def __init__(self):
        self._parsed_data = {}
        self._parser = _root_parser(self._parsed_data)
        return htmlparser.HTMLParser.__init__(self)
    
    def handle_starttag(self, tag, attrs):
        r = self._parser.handle_starttag(tag, attrs)
        if r != None:
            self._parser = r
    
    def handle_data(self, data):
        self._parser.handle_data(data)
    
    def handle_endtag(self, tag):
        r = self._parser.handle_endtag(tag)
        if r != None:
            self._parser = r



def get_website_info(url):
    r = requests.get(_base_url+url)
    if r.status_code != requests.codes.ok : r.raise_for_status()
    else:
        p = _AlexaHTMLParser()
        p.feed(r.text)
        if p._parsed_data["rank"]["global"] == "-":
            raise ValueError("Website not found in the database.")
        return p._parsed_data
