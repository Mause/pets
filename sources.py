import re
import json
import arrow
import requests
from tqdm import tqdm
from urllib.parse import urljoin
from lxml.html import fromstring, tostring
from cssselect import HTMLTranslator
from functools import lru_cache
import attr

_ctx = lru_cache()(HTMLTranslator().css_to_xpath)
parser = arrow.parser.DateTimeParser('en_au', 100)


def ctx(el, selector):
    return el.xpath(_ctx(selector))


def parse(string, fmt=None):
    if fmt is None:
        t = parser.parse_iso(string)
    else:
        t = parser.parse(string, fmt)
    return arrow.Arrow.fromdatetime(t)


@attr.s
class Pet(object):
    location = attr.ib()
    image = attr.ib()
    breed = attr.ib()
    color = attr.ib()
    gender = attr.ib()
    found_on = attr.ib()
    source = attr.ib()
    url = attr.ib()

    @found_on.validator
    def validate(self, attr, value):
        assert isinstance(value, arrow.Arrow)


def get(*args, **kwargs):
    r = requests.get(*args, **kwargs)
    r.raise_for_status()
    return fromstring(r.text)


def wanneroo():
    url = 'http://www.wanneroo.wa.gov.au/animals/cats'
    html = get(url)
    items = html.xpath('.//a[@class="item-list__article boxed"]/@href')
    for item in items:
        actual_url = urljoin(url, item)
        item = get(actual_url)
        image = urljoin(
            url,
            ctx(item, '.container > .main-image')[0].attrib['src']
        )
        item = ctx(item, '.container > .item-list')[0]
        item = dict(li.itertext() for li in item)

        yield Pet(
            found_on=parse(item['Admission date: '], 'DD/MM/YYYY'),
            gender=item['Sex: '],
            color=item['Colour: '],
            breed=item['Breed: '],
            location=item['Admitted from: '],
            image=image,
            source='wanneroo',
            url=actual_url,
        )


def victoriapark():
    url = 'https://www.victoriapark.wa.gov.au/Found-animals'
    html = get(
        url,
        params='dlv_OC CL Public Lost Animals=(dd_OC Animal Type=Cat)'
    )
    items = html.xpath('.//*[@class="list-item-container"]/article/div')
    for item in items:
        def g(key):
            return ctx(item, f'.{key} > .field-value')[0].text
        image = item.xpath(
            '*[contains(@class,"image-gallery-container")]/span/a/img/@src'
        )[0]
        image = urljoin(url, image)
        location = g('item-location')
        breed = g("item-breed")
        color = g("item-color")
        gender = g("item-gender")
        found_on = ctx(item, '.published-on')[0].text
        found_on = parse(found_on, '[Found on] D MMMM YYYY')
        yield Pet(
            image=image,
            location=location,
            breed=breed,
            color=color,
            gender=gender,
            found_on=found_on,
            source='victoriapark',
            url=url,
        )


def armadale():
    url = 'https://www.armadale.wa.gov.au/animal-management-facility'
    html = get(url)
    items = (ctx(
        html,
        '.view-impounded-animals > .view-content > .views-row'))
    for item in items:
        color = (ctx(item, '.animal-color'))
        if not color:
            continue

        color = color[0].text
        image = (ctx(item, '.animal-image > a > img'))[0].attrib['src']
        breed = (ctx(item, '.breed'))[0].text
        location = (ctx(item, '.location-found'))[0].text
        found_on = (ctx(item, '.date-found > span'))[0].attrib['content']
        gender, species = (ctx(item, '.species'))[0].text.split('\u00a0')
        if species != 'cat':
            print(species)
            continue

        yield Pet(
            gender=gender,
            color=color,
            image=image,
            breed=breed,
            location=location,
            found_on=parse(found_on),
            source='armadale',
            url=url,
        )


def kwinana():
    cats = requests.get(
        'http://rtcdn.cincopa.com/jsonv2.aspx',
        params={
            'wid': '_cp_0',
            'fid': 'AQKAMMeTUqs_',
            'thumb': 'large',
            'content': 'original,v:mp4_hd,a:mp3,p:xlarge',
            'details': 'all'
        }
    ).json()['items']

    for cat in cats:
        # ""Male Shih-Tzu found on Gilmore Ave Leda",
        description = re.match(
            r"(?P<gender>[^ ]*) (?P<breed>.*) found on (?P<location>.*)",
            cat['description']
        ).groupdict()

        yield Pet(
            color=None,
            found_on=parse(cat['modified']),
            gender=description['gender'],
            breed=description['breed'],
            location=description['location'],
            image=cat['versions']['original']['url'],
            source='kwinana',
            url=(
                'https://www.kwinana.wa.gov.au/our-services/'
                'animal-services/lostanimals/Pages/default.aspx'
            ),
        )


def swan():
    url = 'http://www.swanamf.com.au/cats'
    cats = requests.get(url).text
    match = re.search(r"var preload_data = '([^']+)';", cats)
    if not match:
        return []

    cats = json.loads(
        json.loads(
            '"{}"'.format(
                match.group(1)
            )
        )
    )
    for cat in cats:
        yield Pet(
            breed=cat["breed"],
            color=cat["colour"],
            found_on=parse(cat["impounded_at"]),
            gender=cat["sex"],
            location=cat["suburb"],
            image=urljoin(url, cat["photo_url"]),
            source='swan',
            url=url,
        )


def cat_haven():
    url = 'https://www.cathavenlostandfound.com/incoming-cats'
    html = requests.get(url).text
    match = re.search(r'var warmupData = (.*);', html)
    if not match:
        return []

    warmup_data = json.loads(match.group(1))

    cats = (
        warmup_data['wixapps']['appbuilder']
        ['items']['NewsPosts_i7ezjf6v55_2']
    ).values()

    for cat in cats:
        image = 'https://static.wixstatic.com/media/' + cat['image']['src']
        lines = fromstring(cat['wxRchTxt_sTxt0']['text']).xpath('./p/text()')
        lines = (line.strip('\u200b\n\xa0\n') for line in lines)
        lines = filter(None, lines)
        lines = dict(line.split(': ') for line in lines)

        yield Pet(
            found_on=parse(lines['Date Found'], ['D/M/YYYY', 'D/M/YY']),
            gender=lines['Gender'],
            location=lines['Location Found'],
            color=lines.get(
                'Description',
                lines.get('Descrption')  # sic
            ),
            breed=None,
            image=image,
            source='cat_haven',
            url=url,
        )


def canning():
    url = (
        'https://www.canning.wa.gov.au/Community/'
        'Ranger-and-Community-Safety-Services/'
        'Animal-Control/Impounded-Animals'
    )
    html = get(url)

    pets = ctx(html, '.main-content-field > table > tbody > tr')

    for pet in pets:
        image = ctx(pet, 'td > img')[0].attrib['src']
        details = {
            p.text.split(':')[0]: p.tail
            for p in ctx(pet, 'td > p > strong')
        }

        desc = details['Description'].lower()
        gender = (
            'Female'
            if 'female' in desc
            else (
                'Male'
                if 'male' in desc
                else 'Unknown'
            )
        )

        yield Pet(
            found_on=parse(details['Found'], 'D MMMM YYYY'),
            location=details['Location'],
            color=details['Colour'],
            breed=None,
            gender=gender,
            image=urljoin(url, image),
            source='canning',
            url=url,
        )


def gosnells():
    url = 'https://eservices.gosnells.wa.gov.au/data/impounds'
    html = get(url)
    rows = ctx(html, 'table > tbody > tr')

    for row in rows:
        _, date, gender, photo = ctx(row, 'td')

        yield Pet(
            found_on=parse(date.text.strip(), 'D MMMM YYYY'),
            location=None,
            color=None,
            breed=None,
            gender=None if gender.text is None else gender.text.strip(),
            image=urljoin(
                url,
                ctx(photo, 'a > img')[0].attrib['src']
            ),
            source='gosnells',
            url=url,
        )


sources = [
    wanneroo,
    victoriapark,
    armadale,
    kwinana,
    swan,
    cat_haven,
    canning,
    gosnells,
]


def main():
    def default(obj):
        if isinstance(obj, arrow.Arrow):
            return obj.isoformat()
        else:
            return attr.asdict(obj)

    for source in tqdm(sources):
        data = list(source())

        with open(f'sources/{source.__name__}.json', 'w') as fh:
            json.dump(
                data, fh, indent=2,
                default=default
            )


if __name__ == '__main__':
    main()
