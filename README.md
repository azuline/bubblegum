# bubblegum

[![Build Status](https://travis-ci.org/dzlr/bubblegum.svg?branch=master)](https://travis-ci.org/dzlr/bubblegum)

bubblegum is a script to make and manage uploads to image hosts. Several image
hosts are supported, to which one can directly upload images or rehost images
by URL.

## Usage

Basic image uploading can be done via the `bubblegum upload` command. To upload
a local image file, run `bubblegum upload /path/to/image.png`. To rehost a URL,
run `bubblegum upload https://this.url.serves.an/image.png`.

The default image host is https://vgy.me, as it does not require client
authorization. The image host that will be used can be changed with the
`--host` flag in the upload command, e.g. `bubblegum upload --host=imgur.com
/path/to/image.png`. The default image host can also be changed in the config
file. Host options can be viewed with the `bubblegum upload --help` command.

Uploading/rehosting multiple images simultaneously is also supported, via
multiple arguments to the `upload` command. `bubblegum upload a.jpg b.png` will
upload both images simultaneously. By default, 4 workers are spawned for image
uploading. The number of workers can be increased or decreased in the config.

A history of uploaded images can be viewed with `bubblegum history`. The
outputted list can be manipulated with the `--sort`, `--limit` and `--offset`
options.

### Config

The configuration is serialized to JSON and stored at
`~/.bubblegum-config.json`. It can be edited with the `bubblegum config`
command. A default configuration file is created when the script first runs.

#### Image Host Profiles

bubblegum includes loaded profiles for the following two hosts by default:

- `imgur.com` (https://imgur.com)
- `vgy.me` (https://vgy.me)

Other image host profiles can be found in the `extra_profiles/` directory.

Image host profiles can be created/added to the application by adding a profile
dictionary to the list of `profiles` in your config file. Each profile must
contain 8 key/value pairs:

- `image_host_name` - The name of the image host, for use with the `--host=`
  option.
- `image_host_url` - The URL of the host's image uploading endpoint.
- `request_headers` - Extra headers to include in the upload request.
- `upload_form_file_argument` - The name of the key for the image file in the
  form.
- `upload_form_data_argument` - A dictionary sent as the form data in a file
  upload.
- `rehost_form_url_argument` - If the host supports URL rehosting, the name of
  the key for the URL in the form. Otherwise, set it to `null`.
- `rehost_form_data_argument` - A dictionary sent as the form data in a URL
  rehost.
- `json_response` - A boolean indicating whether or not the returned data is
  JSON or not. If True, the `data response` variable will be the deserialized
  JSON. If False, the `data` request response variable will be the response
  text.
- `image_url_template` - A string of an f-string (yeah, sounds confusing) for
  the image URL. Can access the request response via the `data` variable.
- `deletion_url_template` - A string of an f-string for the deletion URL. Can
  access the request response via the `data` variable.

### Imgur

To upload to imgur, a Client ID must be created and supplied. Details on
creating a Client ID can be found at
https://apidocs.imgur.com/#authorization-and-oauth. Once created, the Client ID
can be added to the config, as the `imgur_client_id`.
