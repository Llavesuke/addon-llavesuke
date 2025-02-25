# -*- coding: utf-8 -*-
#------------------------------------------------------------
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import httptools
from core import urlparse
from bs4 import BeautifulSoup


canonical = {
             'channel': 'muchoporno', 
             'host': config.get_setting("current_host", 'muchoporno', default=''), 
             'host_alt': ["https://www.pornburst.xxx/"], 
             'host_black_list': ["https://www.muchoporno.xxx/"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title="Nuevas" , action="lista", url=host))
    itemlist.append(item.clone(title="Pornstars" , action="categorias", url=host + "pornstars/"))
    itemlist.append(item.clone(title="Canal" , action="categorias", url=host + "sites/"))
    itemlist.append(item.clone(title="Categorias" , action="categorias", url=host + "categories/"))
    itemlist.append(item.clone(title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch/?q=%s" % (host, texto)
    try:
        return lista(item)
    except Exception:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def categorias(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('div', class_='contenido').find_all(attrs={"class": "muestra-escena"})
    for elem in matches:
        if "/sites/" in item.url:
            url = elem.a['href']
        else:
            url = elem['href']
        title = elem.h2.text.strip()
        thumbnail = elem.img['data-src']
        thumbnail = thumbnail.replace("/model2-", "/model")
        cantidad = elem.find('span', class_='videos')
        if cantidad:
            title = "%s (%s)" %(title, cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        itemlist.append(item.clone(action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail ) )
    next_page = soup.find('link', rel='next')
    if next_page:
        next_page = next_page['href']
        itemlist.append(item.clone(action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='box-link-productora')
    for elem in matches:
        logger.debug(elem)
        url = elem.a['href']
        title = elem.a['data-stats-video-name']
        thumbnail = elem.img['data-src']
        time = elem.find('span', class_='minutos')
        if time:
            time = time.text.strip()
            title = "[COLOR yellow]%s[/COLOR] %s" % (time, title)
        url = urlparse.urljoin(item.url,url)
        plot = ""
        action = "play"
        if logger.info() is False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('li', class_='pagination_item--next')
    if next_page:
        next_page = next_page.a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    url = soup.find('video').source['src']
    itemlist.append(item.clone(action="play", title="Directo", contentTitle=item.contentTitle, url=url))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    url = soup.find('video').source['src']
    itemlist.append(item.clone(action="play", contentTitle=item.contentTitle, url=url))
    return itemlist