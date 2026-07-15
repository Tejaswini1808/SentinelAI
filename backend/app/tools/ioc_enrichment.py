"""Mock IOC enrichment (WHOIS / VirusTotal-style reputation / GeoIP / malware
family) for IPs, domains, hashes, and emails. Deterministic based on a hash of
the IOC so the same input always enriches the same way, standing in for real
threat-intel API calls per the MVP scope."""
import hashlib
import re

_IP_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")
_HASH_RE = re.compile(r"^[a-fA-F0-9]{32}$|^[a-fA-F0-9]{40}$|^[a-fA-F0-9]{64}$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

_COUNTRIES = ["US", "NL", "RU", "CN", "DE", "BR", "SG", "VN", "IR", "GB"]
_MALWARE_FAMILIES = ["Emotet", "Qakbot", "Cobalt Strike", "AsyncRAT", "LockBit", "IcedID", None, None]
_REGISTRARS = ["NameCheap Inc.", "GoDaddy.com LLC", "Cloudflare Inc.", "Alibaba Cloud", "PDR Ltd."]


def _classify(ioc: str) -> str:
    if _IP_RE.match(ioc):
        return "ip"
    if _HASH_RE.match(ioc):
        return "hash"
    if _EMAIL_RE.match(ioc):
        return "email"
    return "domain"


def _seeded_bytes(ioc: str) -> bytes:
    return hashlib.sha256(ioc.encode()).digest()


def enrich(ioc: str) -> dict:
    ioc_type = _classify(ioc)
    digest = _seeded_bytes(ioc)
    score = digest[0] % 100
    malicious = score >= 65

    result = {
        "ioc": ioc,
        "ioc_type": ioc_type,
        "reputation": {
            "malicious": malicious,
            "score": score,
            "categories": ["c2", "malware"] if malicious else ["benign"],
            "known_malware_family": _MALWARE_FAMILIES[digest[1] % len(_MALWARE_FAMILIES)] if malicious else None,
        },
        "geoip": {
            "country": _COUNTRIES[digest[2] % len(_COUNTRIES)],
            "asn": f"AS{10000 + digest[3] * 137}",
        },
    }

    if ioc_type in ("domain", "email"):
        domain = ioc.split("@")[-1] if ioc_type == "email" else ioc
        result["whois"] = {
            "domain": domain,
            "registrar": _REGISTRARS[digest[4] % len(_REGISTRARS)],
            "created_days_ago": digest[5] * 3,
            "privacy_protected": bool(digest[6] % 2),
        }

    return result
