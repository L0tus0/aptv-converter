# APTV M3U Converter

Daily converter for the APTV IPTV list.

Upstream:

```text
https://raw.githubusercontent.com/Kimentanm/aptv/refs/heads/master/m3u/iptv.m3u
```

## Outputs

```text
dist/iptv.cleaned.m3u
dist/iptv.vlc.m3u
dist/iptv.kodi.m3u
```

### `iptv.cleaned.m3u`

Removes APTV-specific global extension lines, but keeps most upstream metadata.

### `iptv.vlc.m3u`

Converts per-channel HTTP headers to `#EXTVLCOPT`.

### `iptv.kodi.m3u`

Converts per-channel HTTP headers to Kodi-style URL pipe parameters.

Example:

```text
http://example.com/live.m3u8|User-Agent=AptvPlayer-UA
```

## Update Schedule

The list is updated daily by GitHub Actions.

Manual update is also available through `workflow_dispatch`.

## Usage

After pushing this repository to GitHub, use one of these raw URLs:

```text
https://raw.githubusercontent.com/<your-username>/<repo-name>/main/dist/iptv.vlc.m3u
https://raw.githubusercontent.com/<your-username>/<repo-name>/main/dist/iptv.kodi.m3u
https://raw.githubusercontent.com/<your-username>/<repo-name>/main/dist/iptv.cleaned.m3u
```

For Android TV players, try them in this order:

1. `iptv.vlc.m3u`
2. `iptv.kodi.m3u`
3. `iptv.cleaned.m3u`
