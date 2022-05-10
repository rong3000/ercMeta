from flask import Flask
from flask import jsonify
from google.cloud import storage
from google.oauth2 import service_account
from PIL import Image
import os
import mimetypes
import tempfile

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
    image_url = _compose_image(['element/bases/base-crab.png',
                                'element/eyes/eyes-big.png',
                                'element/mouths/mouth-pleased.png'],
                               token_id, "element")

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

    _add_attribute(attributes, ELEMENTS[token_id % len(
        ELEMENTS)]['trait_type'], ELEMENTS[token_id % len(ELEMENTS)]['value'], token_id)

    return jsonify({
        'name': element_name,
        'description': "One of the Poo's basic elements",
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


@app.route('/api/factory/<token_id>')
def factory(token_id):
    token_id = int(token_id)
    if token_id == 0:
        name = "One OpenSea creature"
        description = "When you purchase this option, you will receive a single OpenSea creature of a random variety. " \
                      "Enjoy and take good care of your aquatic being!"
        image_url = _compose_image(
            ['images/factory/egg.png'], token_id, "factory")
        num_inside = 1
    elif token_id == 1:
        name = "Four OpenSea creatures"
        description = "When you purchase this option, you will receive four OpenSea creatures of random variety. " \
                      "Enjoy and take good care of your aquatic beings!"
        image_url = _compose_image(
            ['images/factory/four-eggs.png'], token_id, "factory")
        num_inside = 4
    elif token_id == 2:
        name = "One OpenSea creature lootbox"
        description = "When you purchase this option, you will receive one lootbox, which can be opened to reveal three " \
                      "OpenSea creatures of random variety. Enjoy and take good care of these cute aquatic beings!"
        image_url = _compose_image(
            ['images/box/lootbox.png'], token_id, "factory")
        num_inside = 3

    attributes = []
    _add_attribute(attributes, 'number_inside', [num_inside], token_id)

    return jsonify({
        'name': name,
        'description': description,
        'image': image_url,
        'external_url': 'https://example.com/?token_id=%s' % token_id,
        'attributes': attributes
    })


def _add_attribute(existing, attribute_name, options, token_id, display_type=None):
    trait = {
        'trait_type': attribute_name,
        'value': options[token_id % len(options)]
    }
    if display_type:
        trait['display_type'] = display_type
    existing.append(trait)


def _compose_image(filenames, token_id, path):
    bucket = _get_bucket()

    composite = None
    for filename in filenames:

        blobIn = bucket.blob(f"{filename}")
        with tempfile.NamedTemporaryFile() as tempIn:
          blobIn.download_to_filename(tempIn.name)
          foreground = Image.open(tempIn.name).convert("RGBA")

        if composite:
            composite = Image.alpha_composite(composite, foreground)
        else:
            composite = foreground

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
