import urllib.request

url = "https://arxiv.org/html/2602.12670v1"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        idx = html.find("Opus 4.6", html.find("Opus 4.6", html.find("Opus 4.6") + 1) + 1)
        if idx != -1:
            print(html[max(0, idx-100) : min(len(html), idx+300)])
except Exception as e:
    print(f"Error: {e}")
