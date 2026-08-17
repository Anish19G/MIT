import urllib.request
r=urllib.request.urlopen('http://127.0.0.1:5000/')
print('STATUS', r.getcode())
html = r.read().decode(errors='ignore')
print(html[:1200])
