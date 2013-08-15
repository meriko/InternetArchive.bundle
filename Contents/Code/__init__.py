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
                    video = True
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
                    video = False
                ),
            title = title,
            thumb = R(ICON),
            summary = "Welcome to the Archive's audio and MP3 library. This library contains over two hundred thousand free digital recordings ranging from alternative news programming, to Grateful Dead concerts, to Old Time Radio shows, to book and poetry readings, to original music uploaded by our users."                    
        )
    )
    
    title = "Search"
    oc.add(
        InputDirectoryObject(
            key = Callback(Search, title = title),
            title  = title,
            prompt = title,
            thumb = R(ICON)
        )
    )
    
    return oc
    
##########################################################################################
@route(PREFIX + '/Subcollections', video = bool)
def Subcollections(url, title, video):
    oc = ObjectContainer(title2 = title)
    
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

        if video:   
            oc.add(
                VideoClipObject(
                    url = link + "#video",
                    title = name,
                    summary = desc,
                    thumb = thumb
                )
            )
        else:
            oc.add(
                AlbumObject(
                    url = link,
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
            title     = title + " (" + itemCount + ")"
        except:
            pass
        
        oc.add(
            DirectoryObject(
                key =
                    Callback(
                        Subcollections,
                        url = url,
                        title = title,
                        video = video
                    ),
                title = title,
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
                                Objects,
                                url = url,
                                title = title,
                                video = video,
                            ),
                        title = choice,
                        thumb = R(ICON)
                    )
                )           


    if len(oc) < 1:
        oc.header  = "Sorry"
        oc.message = "Could not find any content"
        
    return oc

##########################################################################################
@route(PREFIX + '/Objects', video = bool, offset = int)
def Objects(url, title, video, offset = 0):
    oc = ObjectContainer(title2 = title)
    
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
                                Objects,
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
                                    Objects,
                                    url = url,
                                    title = oc.title2,
                                    video = video,
                                    offset = counter
                                ),
                            title = "Next..."
                        )
                    )
                    return oc
    
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
                                    Objects,
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
                    Objects,
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
                    Objects,
                    url = searchURLAudio,
                    title = title, 
                    video = False
                ),
            title = title,
            thumb = R(ICON)
        )
    )
    
    return oc


