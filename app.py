from flask import Flask
from flask import jsonify
from google.cloud import storage
from google.oauth2 import service_account
from PIL import Image
import os
import mimetypes
import tempfile
import json

GOOGLE_STORAGE_PROJECT = os.environ['GOOGLE_STORAGE_PROJECT']
GOOGLE_STORAGE_BUCKET = os.environ['GOOGLE_STORAGE_BUCKET']

app = Flask(__name__)

BASES = ['jellyfish', 'starfish', 'crab', 'narwhal', 'tealfish', 'goldfish']
EYES = ['big', 'joy', 'wink', 'sleepy', 'content']
MOUTH = ['happy', 'surprised', 'pleased', 'cute']


INT_ATTRIBUTES = [5, 2, 3, 4, 8]
FLOAT_ATTRIBUTES = [1.4, 2.3, 11.7, 90.2, 1.2]
STR_ATTRIBUTES = [
    'happy',
    'sad',
    'sleepy',
    'boring'
]
BOOST_ATTRIBUTES = [10, 40, 30]
PERCENT_BOOST_ATTRIBUTES = [5, 10, 15]
NUMBER_ATTRIBUTES = [1, 2, 1, 1]


@app.route('/api/element/<token_id>')
def element(token_id):
    token_id = int(token_id)
    element_name = "element ""%s" % token_id

    base = BASES[token_id % len(BASES)]
    eyes = EYES[token_id % len(EYES)]
    mouth = MOUTH[token_id % len(MOUTH)]
    # image_url = _compose_image(['images/bases/base-%s.png' % base,
    #                             'images/eyes/eyes-%s.png' % eyes,
    #                             'images/mouths/mouth-%s.png' % mouth],
    #                            token_id, "element")
    image_url = _get_element_image(token_id)

    attributes = []
    # _add_attribute(attributes, 'base', BASES, token_id)
    # _add_attribute(attributes, 'eyes', EYES, token_id)
    # _add_attribute(attributes, 'mouth', MOUTH, token_id)
    # _add_attribute(attributes, 'level', INT_ATTRIBUTES, token_id)
    # _add_attribute(attributes, 'stamina', FLOAT_ATTRIBUTES, token_id)
    # _add_attribute(attributes, 'personality', STR_ATTRIBUTES, token_id)
    # _add_attribute(attributes, 'aqua_power', BOOST_ATTRIBUTES, token_id, display_type="boost_number")
    # _add_attribute(attributes, 'stamina_increase', PERCENT_BOOST_ATTRIBUTES, token_id, display_type="boost_percentage")
    # _add_attribute(attributes, 'generation', NUMBER_ATTRIBUTES, token_id, display_type="number")

    ELEMENTS = [
        {
            'trait_type': 'base',
            'value': ['jellyfish', 'starfish', 'crab', 'narwhal', 'tealfish', 'goldfish']
        },
        {
            'trait_type': 'eyes',
            'value': ['big', 'joy', 'wink', 'sleepy', 'content', 'watery']
        },
        {
            'trait_type': 'mouth',
            'value': ['happy', 'surprised', 'pleased', 'cute', 'sad', 'furious']
        },
        {
            'trait_type': 'arms',
            'value': ['long', 'short', 'bulky', 'slim', 'X long', 'x short']
        },
        {
            'trait_type': 'legs',
            'value': ['long', 'short', 'bulky', 'slim', 'X long', 'x short']
        },
        {
            'trait_type': 'background',
            'value': ['red', 'yellow', 'green', 'blue', 'white', 'purple']
        },
    ]

    _get_element_attribute(attributes, token_id)

    # _add_attribute(attributes, ELEMENTS[token_id % len(
    #     ELEMENTS)]['trait_type'], ELEMENTS[token_id % len(ELEMENTS)]['value'], token_id)

    return jsonify({
        'name': element_name,
        'description': "One of the Poo's basic elements",
        'image': image_url,
        'attributes': attributes
    })


@app.route('/api/merged/<token_id>')
def merged(token_id):
    tokenId = token_id
    token_ids = []
    
    while tokenId:
        if int(tokenId[(len(tokenId)-4):]) > 0:
            token_ids.append(int(tokenId[(len(tokenId)-4):]))        
        tokenId = tokenId[:(len(tokenId)-4)]
    token_ids = list(set(token_ids))
    token_ids = sorted(token_ids, key=lambda a : (a-1) % 10)
    print(token_ids)
    uniqueId = ''
    for id in reversed(token_ids):
        paddedId = str(id).zfill(4)
        uniqueId += paddedId
    
    merged_name = "merged ""%s" % uniqueId
    bucket = _get_bucket()
    filename = f'merged/{uniqueId}.json'
    stats = storage.Blob(bucket=bucket, name=filename).exists()
    if stats:
        blobIn = bucket.blob(f"merged/{uniqueId}.json")
        data = json.loads(blobIn.download_as_string(client=None))
        return data
    else:


    
        image_url = _compose_image(token_ids, uniqueId, "merged")
    
        attributes = []
    
        _add_attribute(attributes, token_ids)

        dataServed = json.dumps({
            'name': merged_name,
            'description': "Merged Poo",
            'image': image_url,
            'attributes': attributes
        })
        print("dataServed is ""%s" % dataServed)

        blobOut = bucket.blob(f"merged/{uniqueId}.json")
        blobOut.upload_from_string(dataServed)
        # with tempfile.NamedTemporaryFile(suffix='.json') as tempOut:
        #     dataServed.save(tempOut.name)
        #     blobOut = bucket.blob(f"merged/{token_id}.json")
        #     blobOut.upload_from_filename(filename=tempOut.name)
    
        return jsonify({
            'name': merged_name,
            'description': "Merged Poo",
            'image': image_url,
            'attributes': attributes
        })


@app.route('/api/box/<token_id>')
def box(token_id):
    token_id = int(token_id)
    image_url = _compose_image(['images/box/lootbox.png'], token_id, "box")

    attributes = []
    _add_attribute(attributes, 'number_inside', [3], token_id)

    return jsonify({
        'name': "Creature Loot Box",
        'description': "This lootbox contains some OpenSea Creatures! It can also be traded!",
        'image': image_url,
        'external_url': 'https://example.com/?token_id=%s' % token_id,
        'attributes': attributes
    })


def _get_element_attribute(existing, token_id):
    bucket = _get_bucket()
    filename = f'element/{token_id}.json'
    stats = storage.Blob(bucket=bucket, name=filename).exists()
    if stats:
        blobIn = bucket.blob(f"element/{token_id}.json")
        data = json.loads(blobIn.download_as_string(client=None))
    else:
        data = {
            "trait_type": "not revealed yet",
            "value": "not revealed yet"
        }
    existing.append(data)


def _get_element_image(token_id):
    bucket = _get_bucket()
    filename = f'element/{token_id}.png'
    stats = storage.Blob(bucket=bucket, name=filename).exists()
    if stats:
        blobIn = bucket.blob(f"element/{token_id}.png")
        return blobIn.public_url
    else:
        blobUnrevealed = bucket.blob(f"element/unrevealed.png")
        return blobUnrevealed.public_url


def _add_attribute(existing, token_ids, display_type=None):
    for id in token_ids:
        bucket = _get_bucket()
        filename = f'element/{id}.json'
        stats = storage.Blob(bucket=bucket, name=filename).exists()
        if stats:
            blobIn = bucket.blob(f"element/{id}.json")
            data = json.loads(blobIn.download_as_string(client=None))
        else:
            data = {
                "trait_type": "not revealed yet",
                "value": "not revealed yet"
            }
        existing.append(data)


def _compose_image(token_ids, token_id, path):
    bucket = _get_bucket()

    composite = None
    for id in token_ids:
        filename = f'element/{id}.png'
        stats = storage.Blob(bucket=bucket, name=filename).exists()
        if stats:
            blobIn = bucket.blob(f"element/{id}.png")
        else:
            blobIn = bucket.blob(f"element/unrevealed.png")
        with tempfile.NamedTemporaryFile() as tempIn:
            blobIn.download_to_filename(tempIn.name)
            foreground = Image.open(tempIn.name).convert("RGBA")
            # foreground = Image.open(tempIn.name)

        if composite:
            composite = Image.alpha_composite(composite, foreground)
        else:
            composite = foreground

        # blobOut = bucket.blob(f"{path}/{token_id}.png")
        # blobOut.upload_from_file(composite)
    with tempfile.NamedTemporaryFile(suffix='.png') as tempOut:
        composite.save(tempOut.name)
        blobOut = bucket.blob(f"{path}/{token_id}.png")
        blobOut.upload_from_filename(filename=tempOut.name)

    # output_path = "images/output/%s.png" % token_id
    # composite.save(output_path)

    return blobOut.public_url


def _get_bucket():
    credentials = service_account.Credentials.from_service_account_file(
        'credentials/google-storage-credentials.json')
    if credentials.requires_scopes:
        credentials = credentials.with_scopes(
            ['https://www.googleapis.com/auth/devstorage.read_write'])
    client = storage.Client(
        project=GOOGLE_STORAGE_PROJECT, credentials=credentials)
    return client.get_bucket(GOOGLE_STORAGE_BUCKET)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
