import re
import json
import arrow
import requests
from tqdm import tqdm
from urllib.parse import urljoin
from robobrowser import RoboBrowser
from lxml.html import fromstring
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
    yield from _wanneroo('dogs')
    yield from _wanneroo('cats')


def _wanneroo(subsection):
    url = f'http://www.wanneroo.wa.gov.au/animals/{subsection}'
    html = get(url)
    items = html.xpath('.//a[@class="item-list__article boxed"]/@href')
    for item in items:
        actual_url = urljoin(url, item)
        item = get(actual_url)
        els = ctx(item, '.container > .main-image')
        image = urljoin(
            url,
            els[0].attrib['src']
        ) if els else None
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


def victoriapark():
    url = 'https://www.victoriapark.wa.gov.au/Found-animals'
    html = get(url)
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


def armadale():
    url = 'https://www.armadale.wa.gov.au/lost-cats-and-dogs-animal-management-facility'
    html = get(url)
    items = (ctx(
        html,
        '.view-impounded-animals > .view-content > .views-row'))
    for item in items:
        color = (ctx(item, '.animal-color'))
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


def kwinana():
    cats = requests.get(
        'http://rtcdn.cincopa.com/jsonv2.aspx',
        params={'fid': 'AcCALWejDppN'}
    ).json()['items']

    for cat in cats:
        # "Male Shih-Tzu found on Gilmore Ave Leda",
        # "Male DLH Grey and white - Handed in to Vet"
        match = re.match(
            r"(?P<gender>[^ ]*) (?P<breed>.*) found [io]n (?P<location>.*)",
            cat['description']
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


def swan():
    yield from _swan('dogs')
    yield from _swan('cats')


def _swan(subsection):
    url = f'http://www.swanamf.com.au/{subsection}'
    pets = requests.get(url).text
    match = re.search(r"var preload_data = '([^']+)';", pets)
    if not match:
        return []

    pets = json.loads(
        json.loads(
            '"{}"'.format(
                match.group(1)
            )
        )
    )
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


def cat_haven():
    url = 'https://www.cathavenlostandfound.com/incoming-cats'
    html = requests.get(url).text
    match = re.search(r'var warmupData = (.*);', html)
    if not match:
        return []

    warmup_data = json.loads(match.group(1))

    cats = (
        warmup_data['wixappsCoreWarmup']['appbuilder']
        ['items']['NewsPosts_i7ezjf6v55_2']
    ).values()

    for cat in cats:
        image = 'https://static.wixstatic.com/media/' + cat['image']['src']
        lines = fromstring(cat['wxRchTxt_sTxt0']['text']).xpath('./p/text()')
        lines = (line.strip('\u200b\n\xa0\n') for line in lines)
        lines = filter(None, lines)
        lines = dict(
            re.split(r': ?', line)
            for line in lines
            if ':' in line
        )

        found_on = lines.get('Date Found', lines.get('Date In'))
        assert found_on, lines
        yield Pet(
            found_on=parse(found_on, ['D/M/YYYY', 'D/M/YY']),
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


def cockburn():
    url = (
        'https://www.cockburn.wa.gov.au/Health-and-Safety/Dogs-and-Cats/'
        'Animal-Pound-Dogs-and-Cats'
    )
    html = get(url)

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


def canning():
    url = (
        'https://www.canning.wa.gov.au/Community/'
        'Ranger-and-Community-Safety-Services/'
        'Animal-Control/Impounded-Animals'
    )
    html = get(url)

    pets = ctx(html, '.main-content-field > table > tbody > tr')

    for pet in pets:
        good = any(len(tr) for tr in ctx(pet, 'tr > td'))
        if not good:
            continue

        els = ctx(pet, 'td > img')
        image = els[0].attrib['src'] if els else None
        details = {
            p.text.split(':')[0]: p.tail
            for p in ctx(pet, 'td > p > strong')
        }

        desc = details.get('Description', '').lower()
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
            found_on=parse(
                details['Found'].replace('\xa0', ' '),
                'D MMMM YYYY'
            ),
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

        image = urljoin(
            url,
            ctx(photo, 'a > img')[0].attrib['src']
        ).replace('width=200', 'width=800')

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


def adjacent(iterable):
    iterable = iter(iterable)
    try:
        while True:
            yield (next(iterable), next(iterable))
    except StopIteration:
        pass


def rockingham():
    rb = RoboBrowser(parser='lxml')
    url = (
        'http://rockingham.wa.gov.au/Services/'
        'Ranger-services/Animal-pound.aspx'
    )
    rb.open(url)
    yield from _rockingham(rb)


def _rockingham(rb):
    html = fromstring(rb.response.content)
    yield from _rockingham_page(rb.url, html)
    index = ctx(html, '.DogIndex')[0].text
    current, total = re.match(
        r' You are viewing page (\d+) of (\d+) ',
        index
    ).groups()
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


def _rockingham_page(url, html):
    for pet in ctx(html, '.landing-box'):
        image = ctx(pet, '.landing-image > img')[0].attrib['src']

        bits = ctx(pet, '.landing-details > p')[0].itertext()
        bits = filter(None, map(str.strip, bits))
        bits = list(bits)
        details = dict(adjacent(bits))

        yield Pet(
            found_on=parse(details['Date Found:'], 'DD MMM YYYY'),
            location=details['Location Found:'],
            color=details['Colour:'],
            breed=details['Breed:'],
            gender=details['Sex:'],
            image=urljoin(url, image),
            source='rockingham',
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
    rockingham,
    cockburn,
]


def default(obj):
    if isinstance(obj, arrow.Arrow):
        return obj.isoformat()
    else:
        return attr.asdict(obj)


def main():
    for source in tqdm(sources):
        data = list(source())

        with open(f'sources/{source.__name__}.json', 'w') as fh:
            json.dump(
                data, fh, indent=2,
                default=default
            )


if __name__ == '__main__':
    main()
