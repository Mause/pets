import json
import re
from dataclasses import asdict, dataclass
from functools import lru_cache
from typing import Callable, Iterable, Iterator, List, Optional, Tuple, TypeVar
from urllib.parse import urljoin

import arrow
import attr
import requests
from cssselect import HTMLTranslator
from lxml.html import fromstring
from requests import Session
from robobrowser import RoboBrowser
from tqdm import tqdm

_ctx = lru_cache()(HTMLTranslator().css_to_xpath)
parser = arrow.parser.DateTimeParser('en_au', 100)
T = TypeVar('T')


def ctx(el, selector):
    return el.xpath(_ctx(selector))


def parse(string, fmt=None):
    if fmt is None:
        t = parser.parse_iso(string)
    else:
        t = parser.parse(string, fmt)
    return arrow.Arrow.fromdatetime(t)


@dataclass
class Pet:
    location: Optional[str]
    image: Optional[str]
    breed: Optional[str]
    color: Optional[str]
    gender: Optional[str]
    found_on: arrow.Arrow
    source: str
    url: str


def get(session: Session, url: str, *args, **kwargs):
    r = session.get(url, *args, **kwargs)
    r.raise_for_status()
    return fromstring(r.text)


def wanneroo(session):
    yield from _wanneroo(session, 'dogs')
    yield from _wanneroo(session, 'cats')


def _wanneroo(session, subsection):
    url = f'http://www.wanneroo.wa.gov.au/animals/{subsection}'
    html = get(session, url)
    items = html.xpath('.//a[@class="item-list__article boxed"]/@href')
    for item in items:
        actual_url = urljoin(url, item)
        item = get(session, actual_url)
        els = ctx(item, '.container > .main-image')
        image = urljoin(url, els[0].attrib['src']) if els else None
        item = ctx(item, '.container > .item-list')[0]
        item = {li.text.strip(): li[0].text.strip() for li in item}

        yield Pet(
            found_on=parse(item['Admission date:'], 'DD/MM/YYYY'),
            gender=item.get('Sex:'),
            color=item['Colour:'],
            breed=item['Breed:'],
            location=item.get('Admitted from:'),
            image=image,
            source='wanneroo',
            url=actual_url,
        )


def victoriapark(session):
    url = 'https://www.victoriapark.wa.gov.au/Found-animals'
    html = get(session, url)
    items = html.xpath('.//*[@class="list-item-container"]/article/div')
    for item in items:

        def g(key):
            items = ctx(item, f'.{key} > .field-value')
            return items[0].text if items else None

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


def armadale(session):
    url = 'https://www.armadale.wa.gov.au/lost-cats-and-dogs-animal-management-facility'
    html = get(session, url)
    items = ctx(html, '.view-impounded-animals > .view-content > .views-row')
    for item in items:
        color = ctx(item, '.animal-color')
        if not color:
            continue

        color = color[0][0].tail.strip()
        image = (ctx(item, '.animal-image > a > img'))[0].attrib['src']
        breed = (ctx(item, '.breed'))[0][0].tail.strip()
        location = ctx(item, '.location-found')[0][0].tail.strip()
        found_on = (ctx(item, '.date-found > span'))[0].attrib['content']
        gender, species = (ctx(item, '.species'))[0].text.split('\u00a0')

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


def kwinana(session):
    cats = session.get(
        'http://rtcdn.cincopa.com/jsonv2.aspx', params={'fid': 'AcCALWejDppN'}
    ).json()['items']

    for cat in cats:
        # "Male Shih-Tzu found on Gilmore Ave Leda",
        # "Male DLH Grey and white - Handed in to Vet"
        match = re.match(
            r"(?P<gender>[^ ]*) (?P<breed>.*) found [io]n (?P<location>.*)",
            cat['description'],
        )
        description = match.groupdict() if match else {}

        yield Pet(
            color=None,
            found_on=parse(cat['modified']),
            gender=description.get('gender'),
            breed=description.get('breed'),
            location=description.get('location'),
            image=cat['versions']['original']['url'],
            source='kwinana',
            url=(
                'https://www.kwinana.wa.gov.au/our-services/'
                'animal-services/lostanimals/Pages/default.aspx'
            ),
        )


def swan(session):
    yield from _swan(session, 'dogs')
    yield from _swan(session, 'cats')


def _swan(session, subsection):
    url = f'http://www.swanamf.com.au/{subsection}'
    r = session.get(url).text
    match = re.search(r"var preload_data = '([^']+)';", r)
    if not match:
        return []

    pets = json.loads(json.loads('"{}"'.format(match.group(1))))
    for pet in pets:
        yield Pet(
            breed=pet["breed"],
            color=pet["colour"],
            found_on=parse(pet["impounded_at"]),
            gender=pet["sex"],
            location=pet["suburb"],
            image=urljoin(url, pet["photo_url"]),
            source='swan',
            url=url,
        )


def cat_haven(session):
    url = 'https://www.cathavenlostandfound.com/incoming-cats'
    html = session.get(url).text
    match = re.search(r'var warmupData = (.*);', html)
    if not match:
        return []

    warmup_data = json.loads(match.group(1))

    cats = (
        warmup_data['wixappsCoreWarmup']['appbuilder']['items'][
            'NewsPosts_i7ezjf6v55_2'
        ]
    ).values()

    for cat in cats:
        image = 'https://static.wixstatic.com/media/' + cat['image']['src']
        lines = fromstring(cat['wxRchTxt_sTxt0']['text']).xpath('./p/text()')
        lines = (line.strip('\u200b\n\xa0\n') for line in lines)
        lines = filter(None, lines)
        lines = dict(re.split(r': ?', line) for line in lines if ':' in line)

        found_on = lines.get('Date Found', lines.get('Date In'))
        assert found_on, lines
        yield Pet(
            found_on=parse(found_on, ['D/M/YYYY', 'D/M/YY']),
            gender=lines['Gender'],
            location=lines['Location Found'],
            color=lines.get('Description', lines.get('Descrption')),  # sic
            breed=None,
            image=image,
            source='cat_haven',
            url=url,
        )


def cockburn(session):
    url = (
        'https://www.cockburn.wa.gov.au/Health-and-Safety/Dogs-and-Cats/'
        'Animal-Pound-Dogs-and-Cats'
    )
    html = get(session, url)

    for pet in ctx(html, '.uk-grid > div > .textimage'):
        text = ctx(pet, '.textimage-text')[0]
        image = ctx(pet, '.textimage-image > img')[0].attrib['src']

        bits = filter(None, map(str.strip, text.itertext()))
        bits = list(bits)
        details = dict(adjacent(bits))

        yield Pet(
            found_on=parse(details['Impound date:'], ['D MMMM YYYY']),
            gender=details['Gender:'],
            location=details['Location found:'],
            color=details['Colour:'],
            breed=details['Breed:'],
            image=urljoin(url, image),
            source='cockburn',
            url=url,
        )


def canning(session):
    url = (
        'https://www.canning.wa.gov.au/Community/'
        'Ranger-and-Community-Safety-Services/'
        'Animal-Control/Impounded-Animals'
    )
    html = get(session, url)

    pets = ctx(html, '.main-content-field > table > tbody > tr')

    for pet in pets:
        good = any(len(tr) for tr in ctx(pet, 'tr > td'))
        if not good:
            continue

        els = ctx(pet, 'td > img')
        image = els[0].attrib['src'] if els else None
        details = {p.text.split(':')[0]: p.tail for p in ctx(pet, 'td > p > strong')}

        desc = details.get('Description', '').lower()
        gender = (
            'Female' if 'female' in desc else ('Male' if 'male' in desc else 'Unknown')
        )

        yield Pet(
            found_on=parse(details['Found'].replace('\xa0', ' '), 'D MMMM YYYY'),
            location=details['Location'],
            color=details['Colour'],
            breed=None,
            gender=gender,
            image=urljoin(url, image),
            source='canning',
            url=url,
        )


def gosnells(session):
    url = 'https://eservices.gosnells.wa.gov.au/data/impounds'
    html = get(session, url)
    rows = ctx(html, 'table > tbody > tr')

    for row in rows:
        _, date, gender, photo = ctx(row, 'td')

        image = urljoin(url, ctx(photo, 'a > img')[0].attrib['src']).replace(
            'width=200', 'width=800'
        )

        yield Pet(
            found_on=parse(date.text.strip(), 'D MMMM YYYY'),
            location=None,
            color=None,
            breed=None,
            gender=None if gender.text is None else gender.text.strip(),
            image=image,
            source='gosnells',
            url=url,
        )


def adjacent(iterable: List[T]) -> Iterator[Tuple[T, T]]:
    i = iter(iterable)
    try:
        while True:
            yield (next(i), next(i))
    except StopIteration:
        pass


def rockingham(session):
    rb = RoboBrowser(parser='lxml', session=session)
    rb.open('https://rockingham.wa.gov.au/your-services/pets-and-animals/animal-pound')
    yield from _rockingham(rb)


def _rockingham(rb):
    html = fromstring(rb.response.content)
    yield from _rockingham_page(rb.url, html)
    r"""
    index = ctx(html, '.DogIndex')[0].text
    current, total = re.match(r' You are viewing page (\d+) of (\d+) ', index).groups()
    if current == total:
        return

    form = rb.get_form()
    key = (
        'ctl00$ctl00$TemplateRegion$ContentInternal$'
        'CMSPagePlaceholder1$lt$ContentZone$'
        'AnimalPound_1$NextPage'
    )
    form[key].value = 'Next'
    rb.submit_form(form, submit=form.submit_fields[key])
    yield from _rockingham(rb)
    """


def _rockingham_page(url, html):
    for pet in ctx(html, '.uk-grid > div > .hotbox'):
        text = ctx(pet, '.hotbox-content')[0]
        image = ctx(pet, '.hotbox-image > img')[0].attrib['data-original']

        bits = filter(None, map(str.strip, text.itertext()))
        bits = list(bits)
        details = dict(adjacent(bits))

        yield Pet(
            found_on=parse(details['Date found'], 'DD MMM YYYY'),
            location=details['Location found'],
            color=details['Colour'],
            breed=details['Breed'],
            gender=details['Sex'],
            image=urljoin(url, image),
            source='rockingham',
            url=url,
        )


sources: List[Callable[[Session], Iterable[Pet]]] = [
    wanneroo,
    victoriapark,
    armadale,
    kwinana,
    swan,
    cat_haven,
    canning,
    gosnells,
    rockingham,
    cockburn,
]


def default(obj):
    if isinstance(obj, arrow.Arrow):
        return obj.isoformat()
    else:
        return asdict(obj)


def main():
    i = tqdm(sources)
    for source in i:
        i.set_description(source.__name__)
        try:
            data = list(source())

            with open(f'sources/{source.__name__}.json', 'w') as fh:
                json.dump(data, fh, indent=2, default=default)
        except Exception as e:
            print(source, 'failed with', e)


if __name__ == '__main__':
    main()
