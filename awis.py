import datetime
import urllib.parse as urlparse
import urllib
import hmac
import hashlib
import base64
import requests

#Query Options  # refer to AWIS API reference for full details.
# Action = "UrlInfo" 
# Url = "www.huffingtonpost.com/"
# ResponseGroup = "TrafficData"


SignatureVersion = "2"
SignatureMethod = "HmacSHA256"
ServiceHost = "awis.amazonaws.com"
PATH = "/"

def create_timestamp():
    now = datetime.datetime.now()
    timestamp = now.isoformat()
    return timestamp

def create_uri(params):
    params = [(key, params[key])
        for key in sorted(params.keys())]
    return urlparse.urlencode(params)

def create_signature(uri, secret):
    # Uri = create_uri(params)
    msg = "\n".join(["GET", ServiceHost, PATH, uri])
    hmac_signature = hmac.new(secret.encode(), msg.encode(), hashlib.sha256)
    signature = base64.b64encode(hmac_signature.digest())
    return urlparse.quote(signature)

def get_access_url(target_url, access_id, secret_key, action="UrlInfo", response_group="Related,TrafficData,ContentData"):
    params = {
    'Action':action,
    'Url':target_url,
    'ResponseGroup':response_group,
    'SignatureVersion':SignatureVersion,
    'SignatureMethod':SignatureMethod,
    'Timestamp': create_timestamp(),
    'AWSAccessKeyId':access_id
    }
    uri = create_uri(params)
    signature = create_signature(uri, secret_key)
    return "http://{0}/?{1}&Signature={2}".format(ServiceHost, uri, signature)

def get_site_info(url, access_id, secret_key):
    return requests.get_access_url(url, access_id, secret_key).text

    