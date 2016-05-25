TITLE  = 'Internet Archive'
ART    = 'art-default.jpg'
ICON   = 'icon-default.png'
PREFIX = '/video/internetarchive'

BASE_URL = "https://archive.org"

MOVING_IMAGE_IMG = 'https://ia902708.us.archive.org/3/items/movies/movies.png'
AUDIO_ARCHIVE_IMG = 'https://ia902704.us.archive.org/6/items/audio/audio.png'
IMAGE_IMG = 'https://ia600508.us.archive.org/12/items/image/image.png'

SUPPORTED_MEDIA_TYPES = ['collections', 'movies', 'audio', 'concerts', 'images']

MAIN_MENU_ITEMS = [
    {'title': "Moving Image Archive", 'url': '/details/movies', 'thumb': MOVING_IMAGE_IMG, 'description': "Welcome to the Archive's Moving Images library of free movies, films, and videos. This library contains over a million digital movies uploaded by Archive users which range from classic full-length films, to daily alternative news broadcasts, to cartoons and concerts."},
    {'title': "Audio Archive", 'url': '/details/audio', 'thumb': AUDIO_ARCHIVE_IMG, 'description': "Welcome to the Archive's audio and MP3 library. This library contains over two hundred thousand free digital recordings ranging from alternative news programming, to Grateful Dead concerts, to Old Time Radio shows, to book and poetry readings, to original music uploaded by our users."},
    {'title': "Images", 'url': '/details/image', 'thumb': IMAGE_IMG, 'description': "This library contains digital images uploaded by Archive users which range from maps to astronomical imagery to photographs of artwork. Many of these images are available for free download."},
]

ITEMS_PER_PAGE = 75

##########################################################################################
def Start():
    
    # Setup the default attributes for the ObjectContainer
    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)

    HTTP.CacheTime = CACHE_1HOUR
    
##########################################################################################
@handler(PREFIX, TITLE, thumb = ICON, art = ART)
def MainMenu():
    
    oc = ObjectContainer()
    
    for item in MAIN_MENU_ITEMS:
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        BrowseChoice,
                        url = BASE_URL + item['url'],
                        title = item['title'],
                        thumb = item['thumb']
                    ),
                title = item['title'],
                thumb = item['thumb'],
                summary = item['description']
            )
        )
    
    title = "Search"
    oc.add(
        InputDirectoryObject(
            key =
                Callback(
                    Search,
                    title = title
                ),
            title  = title,
            prompt = title,
            thumb = R(ICON),
            summary = 'Search the Internet Archive'
        )
    )
    
    return oc

##########################################################################################
@route(PREFIX + '/BrowseChoice')
def BrowseChoice(url, title, thumb):
    
    oc = ObjectContainer(title2 = title)
    pageElement = HTML.ElementFromURL(url)
    
    urls = []
    for item in pageElement.xpath("//*[contains(@class,'facet-mediatype')]//a"):
        try:
            if item.xpath(".//span/text()")[0].strip() in SUPPORTED_MEDIA_TYPES:
                media_type = item.xpath(".//span/text()")[0].strip()
            else:
                continue
        except:
            continue
            
        url = BASE_URL + item.xpath("./@href")[0]
        
        if url in urls:
            continue
        
        urls.append(url)

        if media_type in ['audio', 'concerts']:
            thumb = AUDIO_ARCHIVE_IMG
            
        elif media_type in ['movies']:
            thumb = MOVING_IMAGE_IMG
        
        elif media_type in ['images']:
            thumb = IMAGE_IMG
        
        oc.add(
            DirectoryObject(
                key =
                    Callback(
                        SortChoice,
                        url = url,
                        title = media_type.title(),
                        thumb = thumb,
                        media_type = media_type
                    ),
                title = media_type.title(),
                thumb = thumb
            )
        )

    if len(oc) == 1:
        return SortChoice(
            url = url,
            title = media_type.title(),
            thumb = thumb,
            media_type = media_type
        )
    else:
        return oc

##########################################################################################
@route(PREFIX + '/SortChoice')
def SortChoice(url, title, thumb, media_type):
    
    oc = ObjectContainer(title2 = title)
    
    title = 'Most Popular'
    if media_type == 'collections':
        oc.add(
            DirectoryObject(
                key =
                    Callback(
                        Collections,
                        url = url,
                        title = media_type.title(),
                        thumb = thumb,
                        sort = '-downloads'
                    ),
                title = title,
                thumb = thumb
            )    
        )
    else:
        oc.add(
            DirectoryObject(
                key =
                    Callback(
                        Items,
                        url = url,
                        title = media_type.title(),
                        thumb = thumb,
                        sort = '-downloads',
                        media_type = media_type
                    ),
                title = title,
                thumb = thumb
            )
        )

    title = 'Recently Added'
    if media_type == 'collections':
        oc.add(
            DirectoryObject(
                key =
                    Callback(
                        Collections,
                        url = url,
                        title = media_type.title(),
                        thumb = thumb,
                        sort = '-date'
                    ),
                title = title,
                thumb = thumb
            )    
        )
    else:
        oc.add(
            DirectoryObject(
                key =
                    Callback(
                        Items,
                        url = url,
                        title = media_type.title(),
                        thumb = thumb,
                        sort = '-date',
                        media_type = media_type
                    ),
                title = title,
                thumb = thumb
            )
        )
        
    title = 'A - Z'
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    AToZ,
                    url = url,
                    title =  media_type.title(),
                    thumb = thumb,
                    media_type = media_type
                ),
            title = title,
            thumb = thumb
        )
    )
    
    return oc
    
##########################################################################################
@route(PREFIX + '/AToZ')
def AToZ(url, title, thumb, media_type):

    oc = ObjectContainer(title2 = title)
    
    if not '?' in url:
        url_to_request = url + "?sort=titleSorter"
    else:
        url_to_request = url + "&sort=titleSorter"
    
    pageElement = HTML.ElementFromURL(url_to_request)
    
    for item in pageElement.xpath("//*[contains(@class,'range-maker')]//td"):
        try:
            url = BASE_URL + item.xpath(".//a/@href")[0]
        except:
            continue

        title = item.xpath(".//a/text()")[0]
        summary = item.xpath(".//a/@title")[0]
        
        if media_type == 'collections':
            oc.add(
                DirectoryObject(
                    key =
                        Callback(
                            Collections,
                            url = url,
                            title = title,
                            thumb = thumb,
                            sort = 'titleSorter'
                        ),
                    title = title + ' (%s)' % summary,
                    thumb = thumb
                )    
            )     
        else:
            oc.add(
                DirectoryObject(
                    key =
                        Callback(
                            Items,
                            url = url,
                            title = title,
                            thumb = thumb,
                            media_type = media_type,
                            sort = 'titleSorter'
                        ),
                    title = title + ' (%s)' % summary,
                    thumb = thumb
                )
            )
    
    return oc

##########################################################################################
@route(PREFIX + '/Collections', page = int)
def Collections(url, title, thumb, sort = '-downloads', page = 1):
    
    oc = ObjectContainer(title2 = title)
    
    if not '?' in url:
        url_to_request = url + "?sort=%s&page=%s" % (sort, page)
    else:
        url_to_request = url + "&sort=%s&page=%s" % (sort, page)
    
    org_url = url
    org_title = title
    org_thumb = thumb
    
    pageElement = HTML.ElementFromURL(url_to_request)
  
    # Try to find collections
    for item in pageElement.xpath("//*[contains(@class,'collection-ia')]"):
        url = BASE_URL + item.xpath(".//a/@href")[0]
        title = ''.join(item.xpath(".//*[contains(@class,'collection-title')]//a//text()")).strip()
        
        try:
            thumb = '/services/img/' + item.xpath("./@data-id")[0]

            if not thumb.startswith("http"):
                thumb = BASE_URL + thumb
        except:
            thumb = org_thumb
            
        try:
            itemCount = item.xpath(".//*[contains(@class,'collection-stats')]//*[contains(@class,'num-items')]/text()")[0].strip()
            extra     = " (" + itemCount + ")"
        except:
            extra = ""
        
        oc.add(
            DirectoryObject(
                key =
                    Callback(
                        BrowseChoice,
                        url = url,
                        title = title,
                        thumb = thumb
                    ),
                title = title + extra,
                thumb = thumb
            )
        )         

    if len(oc) < 1:
        oc.header  = "Sorry"
        oc.message = "Could not find any content"
    
    elif len(oc) >= ITEMS_PER_PAGE:
        oc.add(
            NextPageObject(
                key =
                    Callback(
                        Collections,
                        url = org_url,
                        title = org_title,
                        thumb = org_thumb,
                        page = page + 1
                    ),
                thumb = org_thumb
            )
        )
        
    return oc

##########################################################################################
@route(PREFIX + '/Items', page = int)
def Items(url, title, thumb, media_type, sort = '-downloads', page = 1):

    oc = ObjectContainer(title2 = title)
    org_url = url
    org_title = title
    org_thumb = thumb

    if not '?' in url:
        url_to_request = url + "?sort=%s&page=%s" % (sort, page)
    else:
        url_to_request = url + "&sort=%s&page=%s" % (sort, page)
   
    pageElement = HTML.ElementFromURL(url_to_request)
  
    for item in pageElement.xpath("//*[contains(@class,'item-ia')]"):
        try:
            url   = BASE_URL + "/details/" + item.xpath("./@data-id")[0]
            title = item.xpath(".//*[contains(@class,'ttl')]//a/@title")[0].strip()
        except:
            continue
        
        try:
            thumb = '/services/img/' + item.xpath("./@data-id")[0]

            if not thumb.startswith("http"):
                thumb = BASE_URL + thumb
        except:
            thumb = org_thumb
            
        try:
            summary = item.xpath(".//span/@title")[0].strip()
        except:
            summary = None
        
        if media_type == 'movies':
            oc.add(
                EpisodeObject(
                    url = url,
                    show = summary,
                    title = title,
                    thumb = thumb,
                    summary = summary
                )
            )

        elif media_type in ['audio', 'concerts']:
            oc.add(
                AlbumObject(
                    url = url,
                    title = title,
                    thumb = thumb,
                    summary = summary,
                    artist = summary
                )
            )
        
        elif media_type == 'images':
            oc.add(
                PhotoAlbumObject(
                    url = url,
                    title = title,
                    thumb = thumb,
                    summary = summary
                )
            )

    if len(oc) < 1:
        oc.header  = "Sorry"
        oc.message = "Could not find any content"
    
    elif len(oc) >= ITEMS_PER_PAGE:
        oc.add(
            NextPageObject(
                key =
                    Callback(
                        Items,
                        url = org_url,
                        title = org_title,
                        thumb = org_thumb,
                        media_type = media_type,
                        sort = sort,
                        page = page + 1
                    ),
                thumb = org_thumb
            )
        )

    return oc

##########################################################################################
@route(PREFIX + '/Search', video = bool, offset = int)
def Search(query, title):
    
    return BrowseChoice(
        url = BASE_URL + '/search.php?query=' + String.Quote(query),
        title = "Results for '%s'" % query,
        thumb = R(ICON)
    )

