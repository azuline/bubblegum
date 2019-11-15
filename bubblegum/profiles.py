# flake8: noqa
# yapf: disable

from bubblegum.config import conf

profiles = conf.profiles + [
    {
        'image_host_name': 'vgy.me',
        'image_host_url': 'https://vgy.me/upload',
        'request_headers': {},
        'upload_form_file_argument': 'file',
        'upload_form_data_argument': {'userkey': conf.vgyme_userkey},
        'rehost_form_url_argument': None,
        'rehost_form_data_argument': {'userkey': conf.vgyme_userkey},
        'json_response': True,
        'image_url_template': "f'{data[\"image\"]}'",
        'deletion_url_template': "f'{data[\"delete\"]}'",
    },
    {
        'image_host_name': 'imgur.com',
        'image_host_url': 'https://api.imgur.com/3/image',
        'request_headers': {'Authorization': f'Client-ID {conf.imgur_client_id}'},
        'upload_form_file_argument': 'image',
        'upload_form_data_argument': {
            'album_id': None,
            'title': None,
            'description': None,
        },
        'rehost_form_url_argument': 'image',
        'rehost_form_data_argument': {
            'album_id': None,
            'title': None,
            'description': None,
        },
        'json_response': True,
        'image_url_template': "f'{data[\"data\"][\"link\"]}'",
        'deletion_url_template': "f'https://imgur.com/delete/{data[\"data\"][\"deletehash\"]}'",
    }
]
