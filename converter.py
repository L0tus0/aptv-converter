from __future__ import annotations

import os
import re
import urllib.parse
import urllib.request
from pathlib import Path


UPSTREAM_URL = os.environ.get(
    "UPSTREAM_URL",
    "https://raw.githubusercontent.com/Kimentanm/aptv/refs/heads/master/m3u/iptv.m3u",
)

OUT_DIR = Path("dist")

DROP_PREFIXES = (
    "#EXT-X-APP",
    "#EXT-X-APTV-TYPE",
    "#EXT-X-SUB-URL",
)

ATTR_RE = re.compile(r'(?P<key>[\w-]+)="(?P<value>[^"]*)"')


def fetch_text(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 aptv-converter/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
    return raw.decode("utf-8-sig", errors="replace")


def should_drop_line(line: str) -> bool:
    stripped = line.strip()
    return any(stripped.startswith(prefix) for prefix in DROP_PREFIXES)


def normalize_header_key(key: str) -> str | None:
    lowered = key.lower()
    if lowered == "http-user-agent":
        return "User-Agent"
    if lowered in {"http-referer", "http-referrer"}:
        return "Referer"
    return None


def strip_http_header_attrs(extinf_line: str) -> tuple[str, dict[str, str]]:
    left, comma, right = extinf_line.partition(",")
    headers: dict[str, str] = {}

    def replace_attr(match: re.Match[str]) -> str:
        key = match.group("key")
        value = match.group("value")
        header_key = normalize_header_key(key)

        if header_key is None:
            return match.group(0)

        headers[header_key] = value
        return ""

    cleaned_left = ATTR_RE.sub(replace_attr, left)
    cleaned_left = re.sub(r"\s{2,}", " ", cleaned_left).rstrip()

    return cleaned_left + comma + right, headers


def append_kodi_headers(url: str, headers: dict[str, str]) -> str:
    if not headers:
        return url

    items = []
    for key in ("User-Agent", "Referer"):
        value = headers.get(key)
        if value:
            encoded = urllib.parse.quote(value, safe="")
            items.append(f"{key}={encoded}")

    if not items:
        return url

    sep = "&" if "|" in url else "|"
    return url + sep + "&".join(items)


def is_media_url(line: str) -> bool:
    stripped = line.strip()
    return bool(stripped) and not stripped.startswith("#")


def convert(lines: list[str], mode: str) -> list[str]:
    out: list[str] = []
    pending_headers: dict[str, str] = {}

    for raw in lines:
        line = raw.rstrip("\n\r")

        if should_drop_line(line):
            continue

        if line.startswith("#EXTINF"):
            cleaned_extinf, headers = strip_http_header_attrs(line)
            pending_headers = headers

            if mode == "cleaned":
                out.append(line)
            else:
                out.append(cleaned_extinf)

            if mode == "vlc":
                user_agent = headers.get("User-Agent")
                referer = headers.get("Referer")
                if user_agent:
                    out.append(f"#EXTVLCOPT:http-user-agent={user_agent}")
                if referer:
                    out.append(f"#EXTVLCOPT:http-referrer={referer}")

            continue

        if is_media_url(line):
            if mode == "kodi":
                out.append(append_kodi_headers(line, pending_headers))
            else:
                out.append(line)

            pending_headers = {}
            continue

        out.append(line)

    return out


def write_m3u(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    text = fetch_text(UPSTREAM_URL)
    lines = text.splitlines()

    outputs = {
        "iptv.cleaned.m3u": convert(lines, "cleaned"),
        "iptv.vlc.m3u": convert(lines, "vlc"),
        "iptv.kodi.m3u": convert(lines, "kodi"),
    }

    for filename, converted in outputs.items():
        write_m3u(OUT_DIR / filename, converted)

    print("Generated:")
    for filename in outputs:
        print(f"  {OUT_DIR / filename}")


if __name__ == "__main__":
    main()
