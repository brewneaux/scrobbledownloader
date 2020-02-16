# scrobbledownload

![Test](https://github.com/brewneaux/scrobbledownloader/workflows/Test/badge.svg)

This is a Python Docker app for downloading last.fm listens, correlating with the Spotify API (which has much cleaner metadata about tracks than last.fm) for track information, and downloading lyrics from genius.com if it can.

The data is stored via SQLAlchemy, and can be configured for any database that SQLalchemy supports.  

## Secrets file

This application requires a secrets file to be presented to it, since we need to connect to three different APIs.  It's a JSON file (for now), that needs to look something like:

```json
{
    "lastfm_api_key": "",
    "lastfm_api_secret": "",
    "lastfm_username": "",
    "spotify_client_id": "",
    "spotify_client_secret": "",
    "scrobbles_per_page": 1000,
    "genius_token": "",
    "db_connection_string": "some sqlalchemy connection string"
}

```

The easiest way to give this to the application is through a docker mount, such as 

```
docker run --rm  -t -v $(pwd)/secrets.json:/run/settings.json scrobble-downloader
```
