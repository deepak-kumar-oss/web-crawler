import hashlib
from urllib.parse import urljoin, urldefrag, urlparse

def normalize(url, base=None):
    if base:
        url = urljoin(base, url)
    url = urldefrag(url)[0]
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "http://" + url
    return url

def make_doc_id(url: str) -> str:
    return hashlib.sha1(url.encode()).hexdigest()
