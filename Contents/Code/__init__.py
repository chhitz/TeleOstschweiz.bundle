####################################################################################################

VIDEO_PREFIX = "/video/teleostschweiz"

MAIN_URL = "http://www.tvo-online.ch"
SHOW_LIST_URL = MAIN_URL + "/index.php?article_id=662"
OTHER_SHOWS_LIST_URL = MAIN_URL + "/index.php?article_id=139"
ARCHIVE_LIST_URL = MAIN_URL + "/index.php?article_id=99"

NAME = L('Title')

ART           = 'art-default.png'
ICON          = 'icon-default.png'

####################################################################################################

def Start():
    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, L('Title'), ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)


def VideoMainMenu():
    dir = MediaContainer(viewGroup="InfoList")
    shows = dict()
    
    xml = HTML.ElementFromURL(SHOW_LIST_URL)
    for show in xml.xpath("//div[@id='article-3']//div[@class='section']"):
        Log(XML.StringFromElement(show))
        title = show.xpath("div/h5/a")[0].text
        Log(title)
        description = show.xpath("div/p")[0].text
        Log(description)
        show_url = show.xpath("div/h5/a")[0].get('href')
        Log(show_url)
        thumb = MAIN_URL + show.xpath("div/a/img")[0].get('src')
        Log(thumb)

        dir.Append(
            Function(
                DirectoryItem(
                    ShowDetails,
                    title,
                    summary=description,
                    thumb=thumb,
                ),
                url = show_url,
            )
        )
        shows[title] = 1
        
    #find other tvo stations
    xml = HTML.ElementFromURL(OTHER_SHOWS_LIST_URL)
    for show in xml.xpath("//div[@id='article-3']//div[@class='section']"):
        Log(XML.StringFromElement(show))
        show_url = show.xpath("div/h5/a")[0].get('href')
        Log(show_url)
        if show_url.find("tvo-online") < 0:
            continue
        title = show.xpath("div/h5/a")[0].text
        Log(title)
        description = show.xpath("div/p")[0].text
        Log(description)
        thumb = MAIN_URL + show.xpath("div/a/img")[0].get('src')
        Log(thumb)

        dir.Append(
            Function(
                DirectoryItem(
                    ShowDetails,
                    title,
                    summary=description,
                    thumb=thumb,
                ),
                url = show_url,
            )
        )
        shows[title] = 1

    #find shows only present in archive
    archive = HTML.ElementFromURL(ARCHIVE_LIST_URL)
    for show in archive.xpath("//div[@id='article-3']//div[@class='section']"):
        title = show.xpath("h4")[0].text
        Log(title)
        if title in shows:
            continue
        thumb = MAIN_URL + show.xpath("div/a/img")[0].get('src')
        Log(thumb)
        dir.Append(
            Function(
                DirectoryItem(
                    ArchiveDetails,
                    title,
                    thumb=thumb,
                ),
                title = title
            )
        )
    # ... and then return the container
    return dir

def parseEpisode(url, title=None):
    if url.startswith("http://"):
        show_url = url
    else:
        show_url = MAIN_URL + "/" + url
    show_page = HTML.ElementFromURL(show_url)
    
    if title:
        show_title = title
    else:
        show_title = show_page.xpath("//div[@id='article-4']/h4")[0].text
    Log(show_title)
    try:
        show_decription = show_page.xpath("//div[@id='article-4']/p")[1].text
        Log(show_decription)
        flashvars = show_page.xpath("//div[@id='article-4']/script")[1].text
        for line in flashvars.splitlines():
            if line.find('image') >= 0:
                show_thumb = MAIN_URL + line.split(',')[1].strip("');")
                Log(show_thumb)
            if line.find('file') >= 0:
                video_url = MAIN_URL + line.split(',')[1].strip("');")
                Log(video_url)
        
        return VideoItem(video_url.replace(" ", "%20"), show_title, summary=show_decription, thumb=show_thumb.replace(" ", "%20"))
    except:
        return None

def ArchiveDetails(sender, title):
    dir = MediaContainer(viewGroup="InfoList", title2=title)
    
    archive = HTML.ElementFromURL(ARCHIVE_LIST_URL)
    for show in archive.xpath("//div[@id='article-3']//div[@class='section']"):
        show_title = show.xpath("h4")[0].text
        Log(title)
        if title != show_title:
            continue
        for episode in show.xpath("div[@class='subsection-2']/ul/li/a"):
            dir.Append(parseEpisode(episode.get('href'), episode.text))
    
    return dir

def ShowDetails(sender, url):
    dir = MediaContainer(viewGroup="InfoList", title2=sender.itemTitle)

    dir.Append(parseEpisode(url))
    
    dir.Extend(ArchiveDetails(None, sender.itemTitle))
    
    return dir
