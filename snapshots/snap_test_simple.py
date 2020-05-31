# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot

snapshots = Snapshot()

snapshots['test_sources[kwinana] 1'] = [
    GenericRepr(
        "Pet(location=None, image='https://mediacdnl3.cincopa.com/v2/872206/1354!0kzDAYzQlDQ09D/0/C161blackandwhitekitten.JPG', breed=None, color=None, gender=None, found_on=<Arrow [2020-05-25T07:40:41+00:00]>, source='kwinana', url='https://www.kwinana.wa.gov.au/our-services/animal-services/lostanimals/Pages/default.aspx')"
    )
]

snapshots['test_sources[swan] 1'] = [
    GenericRepr(
        "Pet(location='MIDVALE', image='http://www.swanamf.com.au/images/animals/20587/photos/original.jpg?1590470590', breed='DSH Cat', color='White', gender='Unknown', found_on=<Arrow [2020-05-26T13:13:00+08:00]>, source='swan', url='http://www.swanamf.com.au/cats')"
    ),
    GenericRepr(
        "Pet(location='MIDLAND', image='http://www.swanamf.com.au/images/animals/20589/photos/original.JPG?1590554273', breed='USH Juvenile', color='White, brown/black ', gender='Unknown', found_on=<Arrow [2020-05-27T12:20:00+08:00]>, source='swan', url='http://www.swanamf.com.au/cats')"
    ),
    GenericRepr(
        "Pet(location='ELLENBROOK', image='http://www.swanamf.com.au/images/animals/20599/photos/original.jpg?1590814402', breed='DSH Cat', color='Black and White', gender='Unknown', found_on=<Arrow [2020-05-30T12:48:00+08:00]>, source='swan', url='http://www.swanamf.com.au/cats')"
    ),
]

snapshots['test_sources[cat_haven] 1'] = [
    GenericRepr(
        "Pet(location='Iluka', image='https://static.wixstatic.com/media/9fa7a0_2e999cf4a72f470cb75b3cd40439ab11~mv2.jpg', breed=None, color='DSH Black and white', gender='Male', found_on=<Arrow [2020-05-29T00:00:00+00:00]>, source='cat_haven', url='https://www.cathavenlostandfound.com/incoming-cats')"
    ),
    GenericRepr(
        "Pet(location='Iluka', image='https://static.wixstatic.com/media/9fa7a0_9faaa8892c4740879db9de0106ad6578~mv2.jpg', breed=None, color='DSH Tabby', gender='Female', found_on=<Arrow [2020-05-29T00:00:00+00:00]>, source='cat_haven', url='https://www.cathavenlostandfound.com/incoming-cats')"
    ),
    GenericRepr(
        "Pet(location='Kewdale', image='https://static.wixstatic.com/media/9fa7a0_68ec91258672459e8dec92f5037db71d~mv2.jpg', breed=None, color='DMH Tabby and White', gender='Unknown', found_on=<Arrow [2020-05-28T00:00:00+00:00]>, source='cat_haven', url='https://www.cathavenlostandfound.com/incoming-cats')"
    ),
    GenericRepr(
        "Pet(location='Unknown', image='https://static.wixstatic.com/media/9fa7a0_a23f299a83e147fc909ea85b1248ac4b~mv2.jpg', breed=None, color='DMH Black\\xa0and White', gender='Female', found_on=<Arrow [2020-05-28T00:00:00+00:00]>, source='cat_haven', url='https://www.cathavenlostandfound.com/incoming-cats')"
    ),
    GenericRepr(
        "Pet(location='Haynes', image='https://static.wixstatic.com/media/9fa7a0_df6eba4d95694f42b3a369dd0f611bfc~mv2.jpg', breed=None, color='DMH Torti and White', gender='Female', found_on=<Arrow [2020-05-29T00:00:00+00:00]>, source='cat_haven', url='https://www.cathavenlostandfound.com/incoming-cats')"
    ),
    GenericRepr(
        "Pet(location='Southern River', image='https://static.wixstatic.com/media/9fa7a0_e9ed1c6ff26f4273a76c2cfe9206cd5c~mv2.jpg', breed=None, color='DSH Tabby', gender='Male', found_on=<Arrow [2020-05-27T00:00:00+00:00]>, source='cat_haven', url='https://www.cathavenlostandfound.com/incoming-cats')"
    ),
    GenericRepr(
        "Pet(location='Como', image='https://static.wixstatic.com/media/9fa7a0_f8f8b54bc3c6470b956ead8a364c3ec2~mv2.jpg', breed=None, color='DMH Grey Tabby', gender='Male', found_on=<Arrow [2020-05-28T00:00:00+00:00]>, source='cat_haven', url='https://www.cathavenlostandfound.com/incoming-cats')"
    ),
]

snapshots['test_sources[wanneroo] 1'] = [
    GenericRepr(
        "Pet(location='Clarkson - 6030', image='http://www.wanneroo.wa.gov.au/lost-animals/images/5ed2005883946.jpg', breed='Koolie x Kelpie', color='White', gender='Female', found_on=<Arrow [2020-05-28T00:00:00+00:00]>, source='wanneroo', url='http://www.wanneroo.wa.gov.au/animals/dogs/6245-white-female-koolie-x-kelpie')"
    ),
    GenericRepr(
        "Pet(location='Sinagra - 6065', image='http://www.wanneroo.wa.gov.au/lost-animals/images/5ed222b185d3a.jpg', breed='Husky', color='Black & white', gender='Female', found_on=<Arrow [2020-05-30T00:00:00+00:00]>, source='wanneroo', url='http://www.wanneroo.wa.gov.au/animals/dogs/6246-black-white-female-husky')"
    ),
    GenericRepr(
        "Pet(location='Sinagra - 6065', image='http://www.wanneroo.wa.gov.au/lost-animals/images/5ed221b7e64ec.jpg', breed='Husky', color='Black & white', gender='Female', found_on=<Arrow [2020-05-30T00:00:00+00:00]>, source='wanneroo', url='http://www.wanneroo.wa.gov.au/animals/dogs/6247-black-white-female-husky')"
    ),
]

snapshots['test_sources[victoriapark] 1'] = []

snapshots['test_sources[armadale] 1'] = [
    GenericRepr(
        "Pet(location='Foothills Vet', image='https://www.armadale.wa.gov.au/sites/default/files/assets/styles/event_feature__640x408_/public/images/animal/206_1.JPG?itok=gOHFbeAe', breed='Dsh', color='Grey', gender='Male', found_on=<Arrow [2020-05-28T00:00:00+08:00]>, source='armadale', url='https://www.armadale.wa.gov.au/lost-cats-and-dogs-animal-management-facility')"
    )
]

snapshots['test_sources[gosnells] 1'] = [
    GenericRepr(
        "Pet(location=None, image='https://eservices.gosnells.wa.gov.au/Data/remote.axd/eservices.gosnells.wa.gov.au/ImpoundImgs//74039_$P1RAMAP_Tibetan Mastiff x.jpg?width=800', breed=None, color=None, gender='Female', found_on=<Arrow [2020-05-30T00:00:00+00:00]>, source='gosnells', url='https://eservices.gosnells.wa.gov.au/data/impounds')"
    ),
    GenericRepr(
        "Pet(location=None, image='https://eservices.gosnells.wa.gov.au/Data/remote.axd/eservices.gosnells.wa.gov.au/ImpoundImgs//74035_$P1RAMAP_Kx86zUV0kUK_MUs6CXCyHw.jpg?width=800', breed=None, color=None, gender='Male', found_on=<Arrow [2020-05-30T00:00:00+00:00]>, source='gosnells', url='https://eservices.gosnells.wa.gov.au/data/impounds')"
    ),
    GenericRepr(
        "Pet(location=None, image='https://eservices.gosnells.wa.gov.au/Data/remote.axd/eservices.gosnells.wa.gov.au/ImpoundImgs//73748_$P1RAMAP_1aqLXPH-x06txGHzeXjL7g.jpg?width=800', breed=None, color=None, gender='Male', found_on=<Arrow [2020-05-27T00:00:00+00:00]>, source='gosnells', url='https://eservices.gosnells.wa.gov.au/data/impounds')"
    ),
]

snapshots['test_sources[canning] 1'] = []

snapshots['test_sources[rockingham] 1'] = [
    GenericRepr(
        "Pet(location='Shoalwater', image='https://rockingham.wa.gov.au/getattachment/9a407892-8a20-4f9c-a99d-2f3424a004b7/342-20.JPG?lang=en-AU', breed='Domestic Short Haired (cat)', color='Tortoise Shell', gender='Female', found_on=<Arrow [2020-05-22T00:00:00+00:00]>, source='rockingham', url='https://rockingham.wa.gov.au/your-services/pets-and-animals/animal-pound')"
    ),
    GenericRepr(
        "Pet(location='Secret Harbour', image='https://rockingham.wa.gov.au/getattachment/b2dad3dd-8535-4fda-8b0f-e95699f5e3d0/346-20.JPG?lang=en-AU', breed='Ragdoll (cat)', color='Seal Point', gender='Male', found_on=<Arrow [2020-05-24T00:00:00+00:00]>, source='rockingham', url='https://rockingham.wa.gov.au/your-services/pets-and-animals/animal-pound')"
    ),
    GenericRepr(
        "Pet(location='Elanora Drive, Rockingham', image='https://rockingham.wa.gov.au/getattachment/f31283b0-6ff2-4330-a4d0-7f789d649387/348-20.JPG?lang=en-AU', breed='Domestic Short Haired (cat)', color='Tabby', gender='Male', found_on=<Arrow [2020-05-25T00:00:00+00:00]>, source='rockingham', url='https://rockingham.wa.gov.au/your-services/pets-and-animals/animal-pound')"
    ),
    GenericRepr(
        "Pet(location='Port Kennedy Vets', image='https://rockingham.wa.gov.au/getattachment/65a560f8-ea6f-4991-9a23-3dbc4ad72fca/351-2020.JPG?lang=en-AU', breed='Domestic Long Hair (cat)', color='Tabby', gender='Female', found_on=<Arrow [2020-05-26T00:00:00+00:00]>, source='rockingham', url='https://rockingham.wa.gov.au/your-services/pets-and-animals/animal-pound')"
    ),
    GenericRepr(
        "Pet(location='Waikiki', image='https://rockingham.wa.gov.au/getattachment/b538cdd2-d18c-432e-b132-f7cbb48b30df/354-20.JPG?lang=en-AU', breed='Staffy X', color='Tan/White', gender='Female', found_on=<Arrow [2020-05-27T00:00:00+00:00]>, source='rockingham', url='https://rockingham.wa.gov.au/your-services/pets-and-animals/animal-pound')"
    ),
    GenericRepr(
        "Pet(location='Port Kennedy', image='https://rockingham.wa.gov.au/getattachment/0f76afa2-c586-4285-b720-05b44bceaac8/361-20.JPG?lang=en-AU', breed='Shar Pei', color='Tan', gender='Male', found_on=<Arrow [2020-05-29T00:00:00+00:00]>, source='rockingham', url='https://rockingham.wa.gov.au/your-services/pets-and-animals/animal-pound')"
    ),
    GenericRepr(
        "Pet(location='Baldivis', image='https://rockingham.wa.gov.au/getattachment/8d9c4c9a-c259-43f0-b368-e0dadd9d4462/358-20.jpg?lang=en-AU&height=1920&width=1440', breed='Siamese (cat)', color='Black/Grey/White', gender='Male', found_on=<Arrow [2020-05-28T00:00:00+00:00]>, source='rockingham', url='https://rockingham.wa.gov.au/your-services/pets-and-animals/animal-pound')"
    ),
    GenericRepr(
        "Pet(location='Warnbro', image='https://rockingham.wa.gov.au/getattachment/3891bf30-1fa9-4311-817d-1a86c0f0c28b/362-20.jpg?lang=en-AU&height=966&width=1288', breed='Domestic Short Haired (cat)', color='Brindle/White', gender='Female', found_on=<Arrow [2020-05-31T00:00:00+00:00]>, source='rockingham', url='https://rockingham.wa.gov.au/your-services/pets-and-animals/animal-pound')"
    ),
]

snapshots['test_sources[cockburn] 1'] = [
    GenericRepr(
        "Pet(location='HAMILTON HILL', image='https://www.cockburn.wa.gov.au/CMSPages/GetBizFormFile.aspx?filename=0f3fed5b-e5ff-4b42-9d16-a254873aee85.jpg&sitename=CityOfCockburn&mod=30May2020035013', breed='Ridgeback', color='Tan and White', gender='Male', found_on=<Arrow [2020-05-30T00:00:00+00:00]>, source='cockburn', url='https://www.cockburn.wa.gov.au/Health-and-Safety/Dogs-and-Cats/Animal-Pound-Dogs-and-Cats')"
    ),
    GenericRepr(
        "Pet(location='COOLBELLUP', image='https://www.cockburn.wa.gov.au/CMSPages/GetBizFormFile.aspx?filename=2343520a-a8d8-471d-b472-a4fdf4272f56.jpg&sitename=CityOfCockburn&mod=29May2020050621', breed='Staffordshire Bull Terrier Cross', color='Brown Brindled', gender='Male', found_on=<Arrow [2020-05-29T00:00:00+00:00]>, source='cockburn', url='https://www.cockburn.wa.gov.au/Health-and-Safety/Dogs-and-Cats/Animal-Pound-Dogs-and-Cats')"
    ),
    GenericRepr(
        "Pet(location='COOLBELLUP', image='https://www.cockburn.wa.gov.au/CMSPages/GetBizFormFile.aspx?filename=260f5576-1268-4f04-aaca-87a058909420.jpg&sitename=CityOfCockburn&mod=29May2020113631', breed='Domestic Short Hair', color='Tabby', gender='Unknown', found_on=<Arrow [2020-05-23T00:00:00+00:00]>, source='cockburn', url='https://www.cockburn.wa.gov.au/Health-and-Safety/Dogs-and-Cats/Animal-Pound-Dogs-and-Cats')"
    ),
    GenericRepr(
        "Pet(location='COOLBELLUP', image='https://www.cockburn.wa.gov.au/CMSPages/GetBizFormFile.aspx?filename=8ba4ab7f-6aeb-4f3f-be04-0bf8636a01a5.jpg&sitename=CityOfCockburn&mod=29May2020113643', breed='Domestic Short Hair', color='White', gender='Unknown', found_on=<Arrow [2020-05-23T00:00:00+00:00]>, source='cockburn', url='https://www.cockburn.wa.gov.au/Health-and-Safety/Dogs-and-Cats/Animal-Pound-Dogs-and-Cats')"
    ),
]
