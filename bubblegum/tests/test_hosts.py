import os
from contextlib import contextmanager

import mock
import pytest

from bubblegum.errors import UploadFailed
from bubblegum.hosts import (
    ImageHost,
    fix_path,
    guess_and_check_mimetype,
    host_name_to_class_name,
    validate_image,
)


@pytest.mark.parametrize(
    'mimetype, uri', [
        ('image/png', 'image.png'),
        ('image/jpeg', 'image.jpeg'),
        ('image/jpeg', 'https://i.imgur.com/image.jpg'),
    ]
)
def test_check_mimetype_success(mimetype, uri):
    assert mimetype == guess_and_check_mimetype(uri)


@pytest.mark.parametrize('uri', [
    'https://a.websi.te',
    'image.txt',
])
def test_check_mimetype_failure(uri):
    with pytest.raises(UploadFailed):
        guess_and_check_mimetype(uri)


def test_fix_path():
    assert 'image.jpeg' == fix_path('image.jpe')


def test_host_name_to_class_name():
    assert 'IMGUR_COM' == host_name_to_class_name('imgur.com')


@contextmanager
def mock_requests_contextmanager(*a, **k):
    yield type('FakeStream', (), {'iter_content': lambda *a, **k: []})()


@mock.patch('bubblegum.hosts.ImageHost.post_image')
@mock.patch('bubblegum.hosts.requests.get', mock_requests_contextmanager)
@mock.patch('bubblegum.hosts.mkstemp')
def test_rehost_image(mkstemp, post_image):
    mkstemp.return_value = (None, '/tmp/bubblegum_test.jpeg')
    host = ImageHost()
    host.rehost_image('http://127.0.0.1:65537/image.jpg')
    call_args = post_image.call_args_list[0][0]
    assert call_args[0] == '/tmp/bubblegum_test.jpeg'
    assert not os.path.isfile('/tmp/bubblegum_test.jpeg')


def test_rehost_image_invalid():
    host = ImageHost()
    with pytest.raises(UploadFailed):
        host.rehost_image('http://127.0.0.1:65537/image.blep')


@pytest.mark.parametrize(
    'input_, output', [
        ('https://hello', ('rehost_image', 'https://hello')),
        (__file__, ('upload_image', __file__)),
    ]
)
def test_validate_image(input_, output):
    assert output == validate_image(None, None, input_)


def test_validate_image_fail():
    with pytest.raises(UploadFailed):
        validate_image(None, None, '/abcdefghij/klmnopqrstuvwxyz/../hl.abcdeg')
