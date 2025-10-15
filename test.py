import hashlib
print(hashlib.sha256("testpass".encode("utf-8")).hexdigest())