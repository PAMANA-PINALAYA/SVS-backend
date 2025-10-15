import hashlib
print(hashlib.sha256("testuser".encode("utf-8")).hexdigest())