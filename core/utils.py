from django.http import JsonResponse
import requests
from django.conf import settings

import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from django.conf import settings
import time

# Simple in-memory cache with timestamps
feed_cache = {
    "openphish": {"data": set(), "fetched_at": 0},
    "urlhaus": {"data": set(), "fetched_at": 0},
    "phishtank": {"data": set(), "fetched_at": 0}
}
CACHE_TTL = 15 * 60  # 15 minutes

def fetch_feed(feed_name, url, parser):
    now = time.time()
    if now - feed_cache[feed_name]["fetched_at"] < CACHE_TTL:
        return feed_cache[feed_name]["data"]
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            parsed_data = parser(res)
            feed_cache[feed_name]["data"] = parsed_data
            feed_cache[feed_name]["fetched_at"] = now
            return parsed_data
    except Exception:
        pass
    return set()


# Feed Parsers
def parse_openphish(res):
    return set(res.text.strip().splitlines())

def parse_urlhaus(res):
    return set(res.text.strip().splitlines())

def parse_phishtank(res):
    urls = set()
    try:
        root = ET.fromstring(res.content)
        for entry in root.findall(".//phish_detail_url"):
            urls.add(entry.text.strip())
    except ET.ParseError:
        pass
    return urls

# Feed Lookup Logic 
def check_against_feeds(url):
    openphish = fetch_feed("openphish", "https://openphish.com/feed.txt", parse_openphish)
    if url in openphish:
        return {"source": "openphish", "phishing": 1}

    urlhaus = fetch_feed("urlhaus", "https://urlhaus.abuse.ch/downloads/text/", parse_urlhaus)
    if url in urlhaus:
        return {"source": "urlhaus", "phishing": 1}

    phishtank = fetch_feed("phishtank", "http://data.phishtank.com/data/online-valid.xml", parse_phishtank)
    if url in phishtank:
        return {"source": "phishtank", "phishing": 1}

    return {"phishing": 0}

def fetch_google_safe_browsing(url):
    api_key = settings.GOOGLE_SAFE_BROWSING_KEY
    endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}"

    payload = {
        "client": {
            "clientId": "web3trustguard",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }

    try:
        res = requests.post(endpoint, json=payload, timeout=5)
        
        if res.status_code != 200:
            return {
                "source": "google",
                "error": True,
                "message": f"Google Safe Browsing HTTP {res.status_code}",
                "details": res.text
            }

        data = res.json()
        return {
            "source": "google",
            "phishing": 1 if "matches" in data else 0,
            "raw": data
        }
    except Exception as e:
        return {
            "source": "google",
            "error": True,
            "message": "Google Safe Browsing request failed",
            "details": str(e)
        }

def fetch_goplus(endpoint: str, params=None, method="GET", body=None):
    url = f"{settings.GOPLUS_BASE}{endpoint}"
    try:
        res = requests.get(url, params=params) if method == "GET" else requests.post(url, json=body)
        if res.status_code == 200:
            json_data = res.json()
            result = json_data.get("result")

            # If phishing check and GoPlus gives nothing, fallback to Google
            if endpoint == "/api/v1/phishing_site/" and (not result or "phishing" not in result):
                fallback = fetch_google_safe_browsing(params.get("url"))
                return fallback if fallback else {"error": True, "message": "Fallback failed", "raw": None}

            if not result:
                return {
                    "error": True,
                    "message": json_data.get("message", "No valid data returned"),
                    "code": json_data.get("code"),
                    "raw": json_data
                }
            return result
        return {
            "error": True,
            "message": f"Unexpected response code {res.status_code}",
            "raw": res.text
        }
    except Exception as e:
        return {
            "error": True,
            "message": "Unable to process request at the moment.",
            "details": str(e)
        }


def fetch_covalent_tx(tx_hash, chain_id):
    url = f"https://api.covalenthq.com/v1/{chain_id}/transaction_v2/{tx_hash}/"
    try:
        res = requests.get(url, params={"key": settings.COVALENT_KEY})
        return res.json().get("data", {}).get("items", [{}])[0]
    except Exception as e:
        return {"error": True, "message": "Transaction lookup failed", "details": str(e)}

def fetch_solana_tx(tx_hash):
    try:
        res = requests.post("https://api.mainnet-beta.solana.com", json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getConfirmedTransaction",
            "params": [tx_hash, {"encoding": "json"}]
        })
        return res.json().get("result", {})
    except Exception as e:
        return {"error": True, "message": "Transaction lookup failed", "details": str(e)}

def get_verified_causes():
    causes, failures = [], []
    for url in settings.VERIFIED_CAUSE_SOURCES:
        try:
            res = requests.get(url.strip(), timeout=5)
            if res.status_code == 200:
                causes.extend(res.json())
            else:
                failures.append({"source": url, "error": f"HTTP {res.status_code}"})
        except Exception as e:
            failures.append({"source": url, "error": str(e)})
    return {"verified_causes": causes, "failed_sources": failures}



def success_response(data):
    return JsonResponse({"success": True, "data": data})

def error_response(message, code=None, raw=None, status=200): 
    return JsonResponse({
        "success": False,
        "message": message,
        "code": code,
        "raw": raw
    }, status=status)
