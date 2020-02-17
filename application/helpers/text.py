import hashlib


def encode(text, algorithm='md5'):
    if algorithm == 'md5':
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    elif algorithm == 'sha1':
        return hashlib.sha1(text.encode('utf-8')).hexdigest()
    elif algorithm == 'sha256':
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    elif algorithm == 'sha384':
        return hashlib.sha384(text.encode('utf-8')).hexdigest()
    elif algorithm == 'sha512':
        return hashlib.sha512(text.encode('utf-8')).hexdigest()
    else:
        raise ValueError
