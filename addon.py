# coding=utf-8
# -*- coding: utf-8 -*-
#
# plugin.video.proximusTV, Kodi add-on
# Copyright (C) 2017  koying
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
from xbmcswift2 import Plugin

import requests
import logging

logging.basicConfig(level=logging.DEBUG)

plugin = Plugin()

source_url = 'https://github.com/google/ExoPlayer/raw/dev-v2/demo/src/main/assets/media.exolist.json'
g_source_json = ''
g_storage = plugin.get_storage('storage', TTL=60*24)

def load_json(url, params=None, headers=None):
  r = requests.get(url, params=params, headers=headers)
  return r.json()

def check_source():
  global g_source_json

  if g_source_json is None and 'source_json' in g_storage:
    return

  g_source_json = load_json(source_url)
  g_storage['source_json'] = g_source_json
  g_storage.sync()

@plugin.route('/samples/<catidx>')
def samples(catidx):
  check_source()

  items = []
  for idx, obj in enumerate(g_source_json[int(catidx)]['samples']):
    item = {
        'label': obj['name'],
        'path': obj['uri'],
        'is_playable': True,
        'info_type': 'video',
        'properties': {
            'inputstream.adaptive.license_type': '',
            'inputstream.adaptive.license_key': '',
            'inputstream.adaptive.manifest_type': ''
        }
    }

    if ('extension' in obj):
      if (obj['extension']) == 'mpd':
        item['properties']['inputstreamaddon'] = 'inputstream.adaptive'
        item['properties']['inputstream.adaptive.manifest_type'] = 'mpd'
      elif (obj['drm_scheme']) == 'ism':
        item['properties']['inputstreamaddon'] = 'inputstream.adaptive'
        item['properties']['inputstream.adaptive.manifest_type'] = 'ism'

    if ('drm_scheme' in obj):
      if (obj['drm_scheme']) == 'widevine':
        item['properties']['inputstream.adaptive.license_type'] = 'com.widevine.alpha'
      elif (obj['drm_scheme']) == 'playready':
        item['properties']['inputstream.adaptive.license_type'] = 'com.microsoft.playready'

    if ('drm_license_url' in obj):
      item['properties']['inputstream.adaptive.license_key'] = obj['drm_license_url']

    items.append(item)

  return plugin.finish(items)

@plugin.route('/')
def index():
  check_source()

  items = []
  for idx, obj in enumerate(g_source_json):
    item = {
        'label': obj['name'],
        'path': plugin.url_for('samples', catidx=idx),
        #'is_playable': True
    }
    items.append(item)

  return plugin.finish(items)


if __name__ == '__main__':
    plugin.run()
