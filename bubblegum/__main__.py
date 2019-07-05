import click
import pyperclip

from bubblegum.config import CONFIG_FILE, conf
from bubblegum.database import db
from bubblegum.hosts import HOSTS, upload_images, validate_image


@click.group()
def commands():
    pass


@commands.command()
@click.argument(
    'images',
    type=click.STRING,
    nargs=-1,
    callback=lambda ctx, param, value: (  # yapf: disable
        validate_image(ctx, param, v) for v in value
    ),
)
@click.option(
    '--host',
    type=click.Choice(HOSTS.keys()),
    help='Image host to upload the image to.',
    default=conf.default_host,
    callback=lambda ctx, param, value: HOSTS[value](),
)
def upload(images, host):
    """Upload an image file or rehost an image URL."""
    uploaded_urls = []
    for img_url, del_url in upload_images(images, host):
        uploaded_urls.append(img_url)
        click.echo(f'{img_url}', nl=False)
        click.echo(f' | Delete: {del_url}' if del_url else '')
    if conf.copy_to_clipboard:
        pyperclip.copy(' '.join(uploaded_urls))


@commands.command()
def config():
    """Edit the configuration file."""
    click.edit(filename=str(CONFIG_FILE))


@commands.command()
@click.option(
    '--sort',
    type=click.Choice(['asc', 'desc']),
    default='asc',
    help='Method of sorting the history',
)
@click.option(
    '--limit',
    type=click.INT,
    default=25,
    help='Number of images in history to list',
)
@click.option(
    '--offset',
    type=click.INT,
    default=0,
    help='Number of images to offset history by',
)
def history(sort, limit, offset):
    """View a list of uploaded images and associated deletion URLs."""
    for id_, time, url, del_ in db.fetch_history(sort, limit, offset):
        click.echo(f'{id_}. {time} - {url}', nl=False)
        click.echo(f' | Delete: {del_}' if del_ else '')


if __name__ == '__main__':
    commands()
