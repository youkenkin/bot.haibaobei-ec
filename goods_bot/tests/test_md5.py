import hashlib

md5 = hashlib.md5("阿玉".encode('utf-8')).hexdigest()
print(md5)