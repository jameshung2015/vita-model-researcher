import urllib.request

url = "https://www.anthropic.com/news/claude-3-7-sonnet"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        idx = html.find("128K")
        if idx != -1:
            print(html[max(0, idx-100) : min(len(html), idx+200)])
except Exception as e:
    print(f"Error: {e}")
