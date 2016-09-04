import requests
import json
import io
import html.parser

# def search_via_json_whois(domain_name):
#     headers = {
#         "Accept": "application/json", 
#         "Authorization": "Token token=1b12a4c74d1cc12611deac40ca6eae78"
#     }
#     r = requests.get("https://jsonwhois.com/api/v1/whois", headers=headers, params={"domain":domain_name})
#     if r.status_code != 200: return None 
#     return r.json()

def save_json_to_file(json_object, file_name):
    if file_name.rstrip(".")[-1] != "json": file_name += ".json"
    f = io.FileIO(file_name, 'w')
    f.write(json.dumps(json_object, indent=1).encode())
    f.close()

class WhoIsHTMLParser(html.parser.HTMLParser):
    def __init__(self):
        self._status = 0
        self.data = {}
        return html.parser.HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == "div" and attrs == [("class", "whois_result"), ("id","registryData")]:
            self._status = 1
            self.data["registry"] = {}
        if tag == "div" and attrs == [("class", "whois_result"), ("id","registrarData")]:
            self._status = 2
            self.data["registrar"] = {}

    def handle_data(self, data):
        if self._status == 1:
            split_at = data.find(":")
            if split_at != -1:
                k = data[:split_at]
                v = data[split_at+1:]
                self.data["registry"][k]=v
        if self._status == 2:
            split_at = data.find(":")
            if split_at != -1:
                k = data[:split_at]
                v = data[split_at+1:]
                self.data["registrar"][k]=v
                if k == "DNSSEC": self._status = 0
    def handle_endtag(self, tag):
        self._status = 0

def search_via_whois(domain_name):
    r = requests.get("http://www.whois.com/whois/"+domain_name)
    if r.status_code != requests.codes.ok:
        r.raise_for_status()
    else:
        p = WhoIsHTMLParser()
        p.feed(r.text)
        return p.data