import mimetypes
import os
import re
from concurrent import futures
from contextlib import contextmanager
from tempfile import mkstemp

import requests

from bubblegum import __version__
from bubblegum.config import conf
from bubblegum.database import db
from bubblegum.errors import BubblegumError, UploadFailed
from bubblegum.profiles import profiles

mimetypes.init()


def guess_and_check_mimetype(uri):
    """
    Guess the mimetype from the URI. If the mimetype is not that of
    an image, raise an error. Otherwise, return the guessed mimetype.
    """
    mimetype, _ = mimetypes.guess_type(uri)
    if not mimetype or not mimetype.startswith('image/'):
        raise UploadFailed(f'Invalid file type: {mimetype}')
    return mimetype


def fix_path(path):
    """
    Edit the filename that gets sent to image hosts. Some
    filehosts are picky with the filenames that get sent. For
    example, vgy.me does not accept `.jpe` as a valid file
    extension.
    """
    return re.sub(r'jpe$', 'jpeg', path)


def host_name_to_class_name(name):
    """
    Turn an image host name into the class name. This uppercases the
    image host name and replaces periods with underscores, to create
    a proper class name.
    """
    return name.upper().replace('.', '_')


@contextmanager
def image(path):
    """
    A context manager that opens the image, gets its mimetype,
    and yields both in respective order.
    """
    mimetype = guess_and_check_mimetype(path)
    with open(path, 'rb') as img:
        yield img, mimetype


class ImageHost:
    """A base class for image hosts."""

    headers = {
        'User-Agent':
            conf.ua_override or f'bubblegum image uploader, v{__version__}',
        'Accept':
            'application/json',
    }

    @property
    def name(self):
        raise NotImplementedError

    def upload_image(self, path):
        """
        Open the image file and call `self.post_image`. Return the
        image link and the deletion link.
        """
        with image(path) as (img, mimetype):
            return self.post_image(path, img, mimetype)

    def rehost_image(self, url):
        """
        This is the default `rehost_image` method. It will download
        the image and then upload it to the new image host via POST
        request. If the image host supports uploading via URL, this
        method should be overwritten in favor of a custom POST.
        """
        mimetype = guess_and_check_mimetype(url)
        _, path = mkstemp(suffix=mimetypes.guess_extension(mimetype))

        try:
            with open(path, 'w+b') as temp:
                with requests.get(url, stream=True) as stream:
                    for chunk in stream.iter_content(chunk_size=2048):
                        temp.write(chunk)

                temp.seek(0)
                return self.post_image(fix_path(path), temp, mimetype)
        finally:
            os.remove(path)

    def post_image(self, path, img, mimetype):
        """
        Make a POST request to the image host, containing the image
        and other required variables. Should be implemented by each
        subclass.
        """
        raise NotImplementedError


def image_host_factory(profile, class_name):
    """
    This function dynamically creates an image host class, subclasing
    the ImageHost base class, using a dictionary of information that
    details how the host accepts image uploads.
    """

    def make_urls(profile, response):
        try:
            if profile['json_response']:
                data = response.json()
            else:
                data = response.text  # noqa: F841

            return (
                eval(profile['image_url_template'] or "f''"),
                eval(profile['deletion_url_template'] or "f''"),
            )
        except Exception:
            raise UploadFailed

    def post_image(self, path, img, mimetype):
        return make_urls(
            profile,
            requests.post(
                profile['image_host_url'],
                headers={
                    **self.headers,
                    **profile['request_headers']
                },
                files={
                    profile['upload_form_file_argument']: (
                        path, img, mimetype
                    )
                },
                data=profile['upload_form_data_argument'],
            ),
        )

    def rehost_image(self, url):
        if not profile['rehost_form_url_argument']:
            return super(self.__class__, self).rehost_image(url)
        return make_urls(
            profile,
            requests.post(
                profile['image_host_url'],
                headers={
                    **self.headers,
                    **profile['request_headers']
                },
                data={
                    profile['rehost_form_url_argument']: url,
                    **profile['rehost_form_data_argument'],
                },
            ),
        )

    return type(
        class_name, (ImageHost, ), {
            'name': profile['image_host_name'],
            'post_image': post_image,
            'rehost_image': rehost_image,
        }
    )


# Dynamically generate image host objects from profiles.
try:
    for profile in profiles:
        class_name = host_name_to_class_name(profile['image_host_name'])
        globals()[class_name] = image_host_factory(profile, class_name)
except Exception:
    raise BubblegumError(
        'Invalid image host profile. Host name: '
        f'{profile.get("image_host_name", "not set")}.'
    )


def validate_image(ctx, param, value):
    """
    Determine whether the parameter is a valid filepath or a URL.
    If it is a filepath, check to see that the filepath exists.
    """
    if re.match(r'https?://', value):
        return 'rehost_image', value
    elif os.path.exists(value):
        return 'upload_image', value
    raise UploadFailed(f'{value} does not exist.')


def upload_images(images, host):
    """
    Upload a list of images to the passed ImageHost. Images must be
    a list of (method, image) tuples, where method is `upload_image`
    or `rehost_image` and image is a path or a URL.
    """
    with futures.ThreadPoolExecutor(max_workers=conf.max_workers) as executor:
        future_uploads = {
            executor.submit(
                lambda method=method, image=image: getattr(host, method)(image)
            )
            for method, image in images
        }
        for future in futures.as_completed(future_uploads):
            img_url, del_url = future.result()
            db.log_upload(img_url, del_url)
            yield img_url, del_url


HOSTS = {h.name: h for h in ImageHost.__subclasses__()}
