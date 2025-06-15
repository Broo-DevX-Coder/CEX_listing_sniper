import hmac,hashlib,base64,time



start = time.time()
prehash = f"dfjughlakjdrsfhgh;aehyrg;auhr;tkjap8vtyuihoaehtropehg;kjdnfflgug"
signature = hmac.new(
"reererer".encode('utf-8'),
prehash.encode('utf-8'),
hashlib.sha256
).digest()
print(base64.b64encode(signature).decode()) 

print((time.time()) - start)