from __future__ import (unicode_literals, division, absolute_import, print_function)

from calibre import browser
from calibre.customize import StoreBase
from calibre.devices.usbms.driver import debug_print
from calibre.gui2 import open_url
from calibre.gui2.store import StorePlugin
from calibre.gui2.store.search_result import SearchResult
from calibre.gui2.store.web_store_dialog import WebStoreDialog
from PyQt5.Qt import QUrl

from .libgen_client import LibgenFictionClient

store_version = 5  # Needed for dynamic plugin loading

__license__ = 'MIT'
__copyright__ = 'fallaciousreasoning'
__docformat__ = 'restructuredtext en'

PLUGIN_NAME = 'Libgen Fiction'
PLUGIN_DESCRIPTION = 'Adds a Libgen Fiction search provider to Calibre'
PLUGIN_AUTHORS = "fallaciousreasoning (https://github.com/fallaciousreasoning/CalibreLibgenStore)"
PLUGIN_VERSION = (0, 2, 0)

class LibgenStore(StorePlugin):
    def genesis(self):
        '''
        Initialize the Libgen Client
        '''
        debug_print('Libgen Fiction::__init__.py:LibgenStore:genesis')

        self.libgen = LibgenFictionClient()

    def search(self, query, max_results=10, timeout=60):
        '''
        Searches LibGen for Books. Since the mirror links are not direct
        downloads, it should not provide these as `s.downloads`.
        '''

        debug_print('Libgen Fiction::__init__.py:LibgenStore:search:query =',
                    query)

        libgen_results = self.libgen.search(query)

        for result in libgen_results.results[:min(max_results, len(libgen_results.results))]:
            debug_print('Libgen Fiction::__init__.py:LibgenStore:search:'
                        'result.title =',
                        result.title)

            for mirror in result.mirrors[0:1]:  # Calibre only shows 1 anyway
                debug_print('Libgen Fiction::__init__.py:LibgenStore:search:'
                            'result.mirror.url =', mirror.url)

                s = SearchResult()

                s.store_name = PLUGIN_NAME
                s.cover_url = result.image_url
                s.title = '{} ({}, {}{})'.format(
                    result.title, result.language, mirror.size, mirror.unit)
                s.author = result.authors
                s.price = '0.00'
                s.detail_item = result.md5
                s.drm = SearchResult.DRM_UNLOCKED
                s.formats = mirror.format
                s.plugin_author = PLUGIN_AUTHORS

                debug_print('Libgen Fiction::__init__.py:LibgenStore:search:s =',
                            s)

                yield s

    def open(self, parent=None, detail_item=None, external=False):
        '''
        Open the specified item in the external, or Calibre's browser
        '''

        debug_print('Libgen Fiction::__init__.py:LibgenStore:open:locals() =',
                    locals())

        detail_url = (
            self.libgen.get_detail_url(detail_item)
            if detail_item
            else self.libgen.base_url
        )

        debug_print('Libgen Fiction::__init__.py:LibgenStore:open:detail_url =',
                    detail_url)

        if external or self.config.get('open_external', False):
            open_url(QUrl(detail_url))
        else:
            d = WebStoreDialog(
                self.gui, self.libgen.base_url, parent, detail_url)
            d.setWindowTitle(self.name)
            d.set_tags(self.config.get('tags', ''))
            d.exec_()

    def get_details(self, search_result, details):
        url = self.libgen.get_detail_url(search_result.detail_item)

        download = self.libgen.get_download_url(search_result.detail_item)
        search_result.downloads[search_result.formats] = download
        
class LibgenStoreWrapper(StoreBase):
    name                    = PLUGIN_NAME
    description             = PLUGIN_DESCRIPTION
    supported_platforms     = ['windows', 'osx', 'linux']
    author                  = PLUGIN_AUTHORS
    version                 = PLUGIN_VERSION
    minimum_calibre_version = (1, 0, 0)
    affiliate               = False
    drm_free_only           = True

    def load_actual_plugin(self, gui):
        '''
        This method must return the actual interface action plugin object.
        '''
        self.actual_plugin_object  = LibgenStore(gui, self.name)
        return self.actual_plugin_object
