TITLE  = 'Internet Archive'
ART    = 'art-default.jpg'
ICON   = 'icon-default.png'
PREFIX = '/video/internetarchive'

BASE_URL = "http://archive.org"

MAX_KEYWORDS_PER_PAGE = 1500

##########################################################################################
def Start():
    # Setup the default attributes for the ObjectContainer
    ObjectContainer.title1 = TITLE
    ObjectContainer.art    = R(ART)

    HTTP.CacheTime = CACHE_1HOUR
    
##########################################################################################
@handler(PREFIX, TITLE, thumb = ICON, art = ART)
def MainMenu():
    oc = ObjectContainer()
    
    title = "Moving Image Archive"
    oc.add(
        DirectoryObject(
            key = 
                Callback(
                    Subcollections,
                    url = BASE_URL + '/details/movies',
                    title = title,
                    video = True,
                    thumb = R(ICON)
                ),
            title = title,
            thumb = R(ICON),
            summary = "Welcome to the Archive's Moving Images library of free movies, films, and videos. This library contains over a million digital movies uploaded by Archive users which range from classic full-length films, to daily alternative news broadcasts, to cartoons and concerts."
        )
    )

    title = "Audio Archive"
    oc.add(
        DirectoryObject(
            key = 
                Callback(
                    Subcollections,
                    url = BASE_URL + '/details/audio',
                    title = title,
                    video = False,
                    thumb = R(ICON)
                ),
            title = title,
            thumb = R(ICON),
            summary = "Welcome to the Archive's audio and MP3 library. This library contains over two hundred thousand free digital recordings ranging from alternative news programming, to Grateful Dead concerts, to Old Time Radio shows, to book and poetry readings, to original music uploaded by our users."                    
        )
    )
    
    title = "Favorites"
    oc.add(
        DirectoryObject(
            key = 
                Callback(
                    Favorites
                ),
            title = title,
            thumb = R(ICON),
            summary = "All your favorites gathered for fast access"                    
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
@route(PREFIX + '/Favorites')
def Favorites():
    if not Dict:
        return ObjectContainer(
            header = "No favorites found",
            message = "After adding favorites, they will show up here"
        )
    
    oc = ObjectContainer(title2 = 'Favorites', no_cache = True)
    
    title = "Manage Favorites"
    oc.add(
        DirectoryObject(
            key = 
                Callback(
                    ManageFavorites
                ),
            title = title,
            thumb = R(ICON),
            summary = "Delete or rename your favorites"                    
        )
    )
    
    for key in Dict:
        item = Dict[key]

        if item['type'] == 0:
           oc.add(
                DirectoryObject(
                    key =
                        Callback(
                            Subcollections,
                            url = item['url'],
                            title = item['title'],
                            video = item['video'],
                            thumb = item['thumb'],
                            summary = item['summary']
                        ),
                    title = item['title'],
                    thumb = item['thumb'],
                    summary = item['summary']
                )
            )
        elif item['type'] == 1:
            oc.add(
                DirectoryObject(
                    key =
                        Callback(
                            Items,
                            url = item['url'],
                            title = item['title'],
                            video = item['video'],
                            thumb = item['thumb'],
                            summary = item['summary']
                        ),
                    title = item['title'],
                    thumb = item['thumb'],
                    summary = item['summary']
                )
            )
        elif item['type'] == 2:
            if item['video']:   
                oc.add(
                    VideoClipObject(
                        url = item['url'],
                        title = item['title'],
                        summary = item['summary'],
                        thumb = item['thumb']
                    )
                )
            else:
                oc.add(
                    AlbumObject(
                        url = item['url'],
                        title = item['title'],
                        summary = item['summary'],
                        thumb = item['thumb']                 
                    )
                )
        
    return oc
    
##########################################################################################
@route(PREFIX + '/ManageFavorites')
def ManageFavorites():
    if not Dict:
        return ObjectContainer(
            header = "No favorites found",
            message = "Nothing to manage"
        )
    
    oc = ObjectContainer(title2 = 'Manage Favorites', no_cache = True)
    
    for key in Dict:
        item = Dict[key]

        oc.add(
            DirectoryObject(
                key =
                    Callback(
                        ManageChoice,
                        key = key
                    ),
                title = item['title'],
                thumb = R(ICON),
                summary = "Delete or rename " + item['title']
            )
        )
    
    return oc

##########################################################################################
@route(PREFIX + '/Search', video = bool, offset = int)
def Search(query, title):
    oc = ObjectContainer(title2 = title)
    
    searchURLMovies = BASE_URL + '/search.php?query=' + String.Quote(query) + '%20AND%20mediatype%3Amovies'
    searchURLAudio  = BASE_URL + '/search.php?query=' + String.Quote(query) + '%20AND%20mediatype%3Aaudio'
    
    title = "Results for '%s' in Moving Image Archive" % query
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Items,
                    url = searchURLMovies,
                    title = title, 
                    video = True
                ),
            title = title,
            thumb = R(ICON)
        )
    )
    
    title = "Results for '%s' in Audio Archive" % query
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Items,
                    url = searchURLAudio,
                    title = title, 
                    video = False
                ),
            title = title,
            thumb = R(ICON)
        )
    )
    
    return oc

##########################################################################################
@route(PREFIX + '/Subcollections', video = bool)
def Subcollections(url, title, video, summary = None, thumb = None):
    oc = ObjectContainer(title2 = title, no_cache = True)
    
    orgTitle = title
    orgUrl   = url
    orgThumb = thumb
    orgDesc  = summary
    
    pageElement = HTML.ElementFromURL(url)
    
    # Add spotlight item
    try:
        for item in pageElement.xpath("//*[@id='spotlight']"):
            link = BASE_URL + item.xpath(".//a/@href")[0]
            
            name = "Spotlight Item"
            try:
                 name = name + " - '" + item.xpath(".//a/text()")[0] + "'"
            except:
                pass
            
            try:
                thumb = item.xpath(".//img/@src")[0]
            
                if not thumb.startswith("http"):
                    thumb = BASE_URL + thumb
            except:
                thumb = None
                
            try:
                desc = item.xpath(".//text()[preceding-sibling::br or following-sibling::br]")[0]
            except:
                desc = None

        oc.add(
            PopupDirectoryObject(
                key =
                    Callback(
                        PlayChoice,
                        url = link,
                        title = name,
                        summary = desc,
                        thumb = thumb,
                        video = video
                    ),
                title = name,
                summary = desc,
                thumb = thumb
            )
        )
          
    except:
        pass

    # Try to find subcollections
    anySubCollectionFound = False
    
    for item in pageElement.xpath("//*[@id='subcollections']//tr"):
        anySubCollectionFound = True
        
        url   = BASE_URL + item.xpath(".//a/@href")[0]
        title = item.xpath(".//a/text()")[0]
        
        try:
            thumb = item.xpath(".//img/@src")[0]
            
            if not thumb.startswith("http"):
                thumb = BASE_URL + thumb
        except:
            thumb = R(ICON)
        
        try:
            desc = item.xpath(".//div/text()")[0]
        except:
            desc = None
            
        try:
            itemCount = item.xpath(".//nobr/text()")[0]
            extra     = " (" + itemCount + ")"
        except:
            pass
        
        oc.add(
            DirectoryObject(
                key =
                    Callback(
                        Subcollections,
                        url = url,
                        title = title,
                        video = video,
                        summary = desc,
                        thumb = thumb
                    ),
                title = title + extra,
                summary = desc,
                thumb = thumb,
            )
        )
    
    # If no subcollections were found, try to find the browse choices
    if not anySubCollectionFound:
        for item in pageElement.xpath("//*[@id='description']//a"):
            ref = item.xpath("./@href")[0]

            if ref.startswith("/browse.php") or \
               ref.startswith("/search.php"):
               
                url = BASE_URL + ref
                choice = item.xpath("./text()")[0]

                oc.add(
                    DirectoryObject(
                        key =
                            Callback(
                                Items,
                                url = url,
                                title = title + ' ' + choice,
                                video = video,
                                thumb = orgThumb
                            ),
                        title = choice,
                        thumb = orgThumb
                    )
                )           


    if len(oc) < 1:
        oc.header  = "Sorry"
        oc.message = "Could not find any content"
    else:
        if not orgUrl in Dict:
            oc.objects.insert(
                0,
                DirectoryObject(
                    key = 
                        Callback(
                            AddFavorite,
                            url = orgUrl,
                            title = orgTitle,
                            video = video,
                            type = 0,
                            summary = orgDesc,
                            thumb = orgThumb
                        ),
                    title = 'Add to Favorites',
                    thumb = orgThumb,
                    summary = 'Add this section to Favorites'
                )
            )
        
    return oc

##########################################################################################
@route(PREFIX + '/Items', video = bool, offset = int)
def Items(url, title, video, offset = 0, summary = None, thumb = None):
    oc = ObjectContainer(title2 = title, no_cache = True)
    
    orgTitle = title
    orgUrl   = url
    orgDesc  = summary
    orgThumb = thumb
    
    pageElement = HTML.ElementFromURL(url)
        
    for item in pageElement.xpath("//*[@class='hitRow']"):
        url = BASE_URL + item.xpath(".//a[@class='titleLink']/@href")[0]
        
        title = ''
        for text in item.xpath(".//a[@class='titleLink']//text()"):
            title = title + ' ' + text
        
        try:
            thumb = item.xpath(".//td[@class='thumbCell']//img/@src")[0]
            
            if not thumb.startswith("http"):
                thumb = BASE_URL + thumb

        except:
            thumb = R(ICON)
            
        try:
            summary = ''
            for text in item.xpath(".//td[@class='hitCell']//text()"):
                summary = summary + ' ' + text
        
            summary = summary.replace(title, '')
        
        except:
            summary = None
        
        title = title.strip().lstrip("[").rstrip("]")
        
        oc.add(
            PopupDirectoryObject(
                key =
                    Callback(
                        PlayChoice,
                        url = url,
                        title = title,
                        summary = summary,
                        thumb = thumb,
                        video = video
                    ),
                title = title,
                summary = summary,
                thumb = thumb
            )
        )

    # If no videoclips or audiotracks were found
    # search for browse items(usually originating from "Browse by Subject/Keyword")
    if len(oc) < 1:
        counter = 0
        
        for item in pageElement.xpath("//*[@id='browse']//li"):
            try:
                ref = item.xpath(".//a/@href")[0]
            except:
                continue
            
            if ref.startswith("/search.php"):
                try:
                    title = item.xpath(".//a/text()")[0]
                except:
                    continue
                    
                counter = counter + 1
                if counter <= offset:
                    continue
                    
                try:
                    title = title + " " + item.xpath("./text()")[0]
                except:
                    pass
            
                oc.add(
                    DirectoryObject(
                        key =
                            Callback(
                                Items,
                                url = BASE_URL + ref,
                                title = title,
                                video = video
                            ),
                        title = title
                    )
                )
                
                if counter - offset >= MAX_KEYWORDS_PER_PAGE:
                    oc.add(
                        NextPageObject(
                            key = 
                                Callback(
                                    Items,
                                    url = url,
                                    title = oc.title2,
                                    video = video,
                                    offset = counter
                                ),
                            title = "Next..."
                        )
                    )
                    break
    
    else:    
        # Check for pagination
        try:
            for item in pageElement.xpath("//*[@class='pageRow']//a"):
                if 'next' in item.xpath("./text()")[0].lower():
                    url = BASE_URL + item.xpath("./@href")[0]
                    oc.add(
                        NextPageObject(
                            key = 
                                Callback(
                                    Items,
                                    url = url,
                                    title = oc.title2,
                                    video = video
                                ),
                            title = "Next..."
                        )
                    )
                    break
        except:
            pass
    
    if len(oc) < 1:
        oc.header  = "Sorry"
        oc.message = "Could not find any content"
    elif len(oc) > 1:
        if not orgUrl in Dict and offset == 0:            
            oc.objects.insert(
                0,
                DirectoryObject(
                    key = 
                        Callback(
                            AddFavorite,
                            url = orgUrl,
                            title = orgTitle,
                            video = video,
                            type = 1,
                            summary = orgDesc,
                            thumb = orgThumb
                        ),
                    title = 'Add to Favorites',
                    thumb = orgThumb,
                    summary = 'Add this section to Favorites'
                )
            )

    return oc

##########################################################################################
@route(PREFIX + '/PlayChoice', video = bool)
def PlayChoice(url, title, summary, thumb, video):
    oc = ObjectContainer()
    
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    PlayableObject,
                    url = url,
                    title = title,
                    summary = summary,
                    thumb = thumb,
                    video = video
                ),
            title = 'Play',
        )
    )
    
    oc.add(
        DirectoryObject(
            key = 
                Callback(
                    AddFavorite,
                        url = url,
                        title = title,
                        video = video,
                        type = 2,
                        summary = summary,
                        thumb = thumb
                ),
            title = 'Add to Favorites'
        )
    )
    
    return oc

##########################################################################################
@route(PREFIX + '/PlayableObject', video = bool)
def PlayableObject(url, title, summary, thumb, video):
    oc = ObjectContainer()
    
    if video:   
        oc.add(
            VideoClipObject(
                url = url + "#video",
                title = title,
                summary = summary,
                thumb = thumb
            )
        )
    else:
        oc.add(
            AlbumObject(
                url = url,
                title = title,
                summary = summary,
                thumb = thumb                   
            )
        )
    
    return oc

##########################################################################################
@route(PREFIX + '/AddFavorite', video = bool, type = int)
def AddFavorite(url, title, video, type, summary = None, thumb = None):        
    Dict[url]            = {}  
    Dict[url]['title']   = title
    Dict[url]['url']     = url
    Dict[url]['summary'] = summary
    Dict[url]['thumb']   = thumb
    Dict[url]['video']   = video
    Dict[url]['type']    = type
    
    item = Dict[url]
  
    return ObjectContainer(
        header = unicode(item['title']),
        message = 'Added to Favorites'
    )
        
##########################################################################################
@route(PREFIX + '/ManageChoice')
def ManageChoice(key):
    if not key in Dict:
        return ObjectContainer() # Fix for Plex/Web
        
    oc = ObjectContainer(no_history = True, no_cache = True)
        
    item = Dict[key]    

    oc.add(
        PopupDirectoryObject(
            key =
                Callback(
                    ConfirmDeleteFavorite,
                    key = key
                ),
            title = 'Delete ' + item['title'],
            thumb = R(ICON)
        )
    )
    
    oc.add(
        InputDirectoryObject(
            key = Callback(RenameFavorite, key = key, title = item['title']),
            title  = 'Rename ' + item['title'],
            prompt = item['title'],
            thumb = R(ICON)
        )
    )
          
    return oc
    
##########################################################################################
@route(PREFIX + '/ConfirmDeleteFavorite')
def ConfirmDeleteFavorite(key):
    if not key in Dict:
        return ObjectContainer() # Fix for Plex/Web
        
    oc = ObjectContainer(title2 = 'Delete', no_history = True, no_cache = True)
    
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    DeleteFavorite,
                    key = key
                ),
            title = 'Confirm Delete',
            thumb = R(ICON)
        )
    )
    
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    MessageBox,
                    header = 'Deletion cancelled',
                    message = 'No deletion performed'
                ),
            title = 'Cancel',
            thumb = R(ICON)
        )
    )
    
    return oc
    
##########################################################################################
@route(PREFIX + '/MessageBox')
def MessageBox(header, message):
    return ObjectContainer(
        replace_parent = True,
        header = header,
        message = message
    )

##########################################################################################
@route(PREFIX + '/RenameFavorite')
def RenameFavorite(query, key, title):
    if not key in Dict:
        return ObjectContainer() # Fix for Plex/Web

    oc = ObjectContainer()
    
    Dict[key]['title'] = query
    
    return MessageBox(
        header = 'Renamed',
        message = title + ' to ' + query
    )
    
##########################################################################################
@route(PREFIX + '/DeleteFavorite')
def DeleteFavorite(key):
    if not key in Dict:
        return ObjectContainer() # Fix for Plex/Web
        
    title = Dict[key]['title']
    del Dict[key]
        
    return MessageBox(
        header = 'Deletion completed',
        message = 'Deleted ' + title
    )

