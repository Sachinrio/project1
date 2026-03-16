import urllib.request
req = urllib.request.Request('https://udyamregistration.gov.in/UdyamRegistration.aspx', headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        with open('udyam.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("Saved to udyam.html")
except Exception as e:
    print("Error:", e)
