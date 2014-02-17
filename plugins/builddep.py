# builddep.py
# Install all the deps needed to build this package.
#
# Copyright (C) 2013  Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# the GNU General Public License v.2, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the
# GNU General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.  Any Red Hat trademarks that are incorporated in the
# source code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission of
# Red Hat, Inc.
#

import dnf
import dnf.cli
import logging
import os
import rpm

logger = logging.getLogger('dnf.plugin')

class BuildDep(dnf.Plugin):

    name = 'builddep'

    def __init__(self, base, cli):
        if cli:
            cli.register_command(BuildDepCommand)
        logger.debug('initialized BuildDep plugin')

class BuildDepCommand(dnf.cli.Command):

    activate_sack = True
    aliases = ('builddep',)
    resolve = True
    writes_rpmdb = True

    @staticmethod
    def _rpm_dep2reldep_str(rpm_dep):
        return rpm_dep.DNEVR()[2:]

    def _src_deps(self, rpm_ts, src_fn):
        fd = os.open(src_fn, os.O_RDONLY)
        h = rpm_ts.hdrFromFdno(fd)
        os.close(fd)
        ds = h.dsFromHeader('requirename')
        for dep in ds:
            reldep_str = self._rpm_dep2reldep_str(dep)
            if reldep_str.startswith('rpmlib('):
                continue
            self.base.install(reldep_str)

    def _spec_deps(self, rpm_ts, spec_fn):
        spec = rpm.spec(spec_fn)
        for dep in rpm.ds(spec.sourceHeader, 'requires'):
            reldep_str = self._rpm_dep2reldep_str(dep)
            self.base.install(reldep_str)

    def run(self, args):
        rpm_ts = rpm.TransactionSet()
        for fn in args:
            if fn.endswith('.src.rpm'):
                self._src_deps(rpm_ts, fn)
            else:
                self._spec_deps(rpm_ts, fn)
