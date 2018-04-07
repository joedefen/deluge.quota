#
# core.py
#
# Copyright (C) 2018 J D <joedefen>
#
# Basic plugin template created by:
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
# Copyright (C) 2007-2009 Andrew Resch <andrewresch@gmail.com>
# Copyright (C) 2009 Damien Churchill <damoxc@gmail.com>
#
# Deluge is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
#       The Free Software Foundation, Inc.,
#       51 Franklin Street, Fifth Floor
#       Boston, MA  02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception
#    statement from all source files in the program, then also delete it here.
#

from deluge.log import LOG as log
from deluge.plugins.pluginbase import CorePluginBase
import deluge.component as component
import deluge.configmanager
from deluge.core.rpcserver import export

from twisted.internet.task import LoopingCall
import subprocess
import time

DEFAULT_PREFS = {
    'speedy': False   # not used
}

class Core(CorePluginBase):
    enabled = False

    def enable(self):
        if self.enabled: return
        else: enabled = True
        self.blocks_gb = 0.0
        self.quota_gb = 0.0
        self.last_char = '*' # or '|' # used to indicate change
        self.last_time = 0 # used to prevent overly rapid updates

        self.config = deluge.configmanager.ConfigManager(
            "quota.conf", DEFAULT_PREFS)

        # Periodically update use and quota for GUI.
        self.update_timer = LoopingCall(self.update)
        self.update_timer.start(10)
        log.debug('Quota.Core.enable()')

    def disable(self):
        self.update_timer.stop()
        log.debug('Quota.Core.disable()')

    def update(self):
        now = time.time()
        if now - self.last_time < 9.5:
            # I don't understand this, but sometimes this
            # gets called at 1s intervals (not the 10s
            # that is desired)
            # log.debug('Quota.Core.update() TOO EARLY!')
            return
        self.last_time = now
        # Status comes from quota command
        output = subprocess.check_output(['quota'])
        beauty_output = None
        if output:
            # use only the second line, this is util info
            beauty_output = output.split('\n')[2].split()
        if beauty_output:
            self.blocks_gb = float(beauty_output[1]) / (1024.0 * 1024.0)
            self.quota_gb = float(beauty_output[2]) / (1024.0 * 1024.0)
        else:
            self.blocks_gb = -1.0
            self.quota_gb = -1.0
        self.last_char = '*' if self.last_char == '|' else '|'
        log.debug('Quota.Core.update() B=%.1f Q=%.1f'
                %(self.blocks_gb, self.quota_gb))

    # @export
    # def set_config(self, config):
        # """Sets the config dictionary"""
        # if False:
            # for key in config.keys():
                # self.config[key] = config[key]
            # self.config.save()

    # @export
    # def get_config(self):
        # """Returns the config dictionary"""
        # return self.config.config

    @export
    def get_use_and_quota_GiB(self):
        return (self.blocks_gb, self.quota_gb, self.last_char)
