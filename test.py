import hashlib
print(hashlib.sha256("adminpass".encode("utf-8")).hexdigest())