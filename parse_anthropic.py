import urllib.request

url = "https://www.anthropic.com/news/claude-3-7-sonnet"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        # Find context around TAU-bench but starting from an offset to find the next occurrence
        tau_idx = html.find("TAU-bench", html.find("TAU-bench") + 1)
        if tau_idx != -1:
            print(html[max(0, tau_idx-100) : min(len(html), tau_idx+200)])
except Exception as e:
    print(f"Error: {e}")
