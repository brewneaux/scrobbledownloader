from scrobbledownload.services.lastfm import LastFM

lfm = LastFM('vonwhoopass', 'bbaffd0e6bf0307c9e92567324870f1d')

lfm.download_scrobbles(1, 1000)