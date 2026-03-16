import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request('https://udyamregistration.gov.in/UdyamRegistration.aspx', headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, context=ctx).read().decode('utf-8')

print("--- AADHAAR ---")
print('\n'.join(re.findall(r'<input[^>]+id=\"[^\"]*aadhaar[^\"]*\"[^>]*>', html, re.IGNORECASE)))
print("--- NAME ---")
print('\n'.join(re.findall(r'<input[^>]+id=\"[^\"]*name[^\"]*\"[^>]*>', html, re.IGNORECASE)))
print("--- BUTTON ---")
print('\n'.join(re.findall(r'<input[^>]+id=\"[^\"]*validate[^\"]*\"[^>]*>', html, re.IGNORECASE)))
print('\n'.join(re.findall(r'<button[^>]+id=\"[^\"]*validate[^\"]*\"[^>]*>', html, re.IGNORECASE)))
