#!/usr/bin/python
#coding: utf-8 -*-

# (c) 2015, Reto Gantenbein <reto.gantenbein@linuxmonk.ch>
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = """
---
module: trac_project
short_description: setup and configure a trac project
description:
   - Setup and configure a Trac project management instance
author: Reto Gantenbein
options:
   name:
     description:
        - Trac project name.
     required: true
   path:
     description:
        - Absolut file system path to the Trac project directory.
     required: true
   dbtype:
     description:
        - Type of database backend.
     choices: [ 'sqlite', 'mysql', 'postgresql' ]
     default: sqlite
   dbhost:
     description:
        - Host name of database. Only used with dbtype 'mysql' or 'postgresql'.
     default: localhost
   dbuser:
     description:
        - Database user name. Only used with dbtype 'mysql' or 'postgresql'.
          If unspecified the project name will be used as user name.
     default: Value of the project name
   dbpass:
     description:
        - Database user password. Only used with dbtype 'mysql' or 'postgresql'.
          In this case the option is required.
     default: null
   dbname:
     description:
        - Database name. Only used with dbtype 'mysql' or 'postgresql'.
          If unspecified the project name will be used as database name.
     default: Value of the project name
   config:
     description:
        - List of trac.ini configuration parameters.
          Syntax: { 'section': INI-section, 'option': option, 'value': value }
     default: []
requirements: [ 'trac' ]
notes:
  - If 'mysql' is used as dbtype, the MySQLdb Python package is required on the
    the remote host. For Debian, this is as easy as apt-get install python-mysqldb.
  - If 'postgresql' is used as dbtype, the psycopg2 Python package, a PostgreSQL
    database adapter is required on the remote host. For Debian, this can be
    installed with apt-get install python-psycopg2.
"""

EXAMPLES = """
# Create new Trac project with name 'myproject'
- trac_project: name='myproject' path='/srv/trac/myproject'

# Create new Trac project with remote PostgreSQL database backend. The database
# and user have to be created separately (e.g. with the Ansible 'postgressql_db'
# module) before running this task.
- trac_project: name='myproject' path='/srv/trac/myproject'
                dbtype='postgresql'
                dbuser='myprojectadm'
                dbpass='p4s5w0rD'
                dbhost='pghost.example.com'
"""

import ConfigParser
try:
    from trac.config import Configuration
    from trac.core import TracError
    from trac.env import Environment
except ImportError:
    msg = 'The trac module is not importable. Check the requirements.'
    print("failed=True msg='%s'" % msg)
    raise SystemExit(msg)


# TRAC_ANSIBLE_DB_TYPES is a list of possible database backends.
TRAC_ANSIBLE_DB_TYPES = [
    'sqlite',
    'mysql',
    'postgresql',
]

class TracProjectManager(object):
    def __init__(self, module):
        """Management of Trac projects via Ansible.

        :param module: Processed Ansible Module.
        :type module: ``object``
        """
        self.module = module
        self.state_change = False
        self.project_path = self.module.params['path']
        self.trac_ini = os.path.join(self.project_path, 'conf', 'trac.ini')

    @staticmethod
    def _project_exists(path):
        """Check if a project exists.

        :param path: Path of the project.
        :type: ``str``
        :returns: True or False if the project is found.
        :rtype: ``bol``
        """
        try:
            Environment(path)
        except TracError:
            return False
        return True

    def _get_update_config(self):
        """Returns a list of dict with the project config parameters to apply.

        :returns: project config to apply
        :rtype: ``list``
        """
        update_config = []
        project_config = self.module.params.get('config')

        if project_config:
            if self._project_exists(self.project_path):
                old_config = ConfigParser.RawConfigParser()

                if not os.path.exists(self.trac_ini):
                    self.module.fail_json(msg="Project configuration not found [ %s ]" % self.trac_ini)

                old_config.readfp(open(self.trac_ini))
                for option in project_config:
                    if option['value'] != old_config.get(option['section'], option['option']):
                        update_config.append(option)
            else:
                update_config = project_config

        return update_config

    def _project_setup(self):
        """Setup a Trac project.

        This method will create and configure a Trac project.
        """

        project_options = []
        if not self.module.params['dbtype'] == 'sqlite':
            db_url = "%s://%s:%s@%s/%s" % (
                self.module.params['dbtype'],
                self.module.params['dbuser'],
                self.module.params['dbpass'],
                self.module.params['dbhost'],
                self.module.params['dbname'],
            )
        else:
            db_url = 'sqlite:db/trac.db'
        project_options.append(('trac', 'database', db_url))

        project_config = self._get_update_config()
        for option in project_config:
            project_options.append((option['section'], option['option'], option['value']))
            self.state_change = True

        if not self._project_exists(self.project_path):
            project_env = Environment(self.project_path, create=True, options=project_options)
            project_env.shutdown()    
            self.state_change = True
        else:
            project_conf = Configuration(self.trac_ini)
            for entry in project_options:
                project_conf.set(*entry)
            project_conf.save()

    def run(self):
        """Run the main method."""
        self._project_setup()

        self.module.exit_json(
            project=self.module.params['name'],
            changed=self.state_change
        )

# ===========================================
# Module execution.
#

def main():
    """Ansible Main module."""

    module = AnsibleModule(
        argument_spec=dict(
            name=dict(
                type='str',
                required=True
            ),
            path=dict(
                type='str',
                required=True
            ),
            dbtype=dict(
                choices=TRAC_ANSIBLE_DB_TYPES,
                default='sqlite',
                required=False
            ),
            dbhost=dict(
                type='str',
                default='localhost',
                required=False
            ),
            dbuser=dict(
                type='str',
                default=None,
                required=False
            ),
            dbpass=dict(
                type='str',
                default=None,
                required=False
            ),
            dbname=dict(
                type='str',
                default=None,
                required=False
            ),
            config=dict(
                type='list',
                default=[],
                required=False
            )
        )
    )

    if module.params['dbtype'] != 'sqlite':
        if not module.params['dbuser']:
            module.params['dbuser'] = module.params['name']
        if not module.params['dbname']:
            module.params['dbname'] = module.params['name']
        if not module.params['dbpass']:
            module.fail_json(msg="missing required arguments: dbpass")

    TracProjectManager(module=module).run()

# import module bits
from ansible.module_utils.basic import *
main()
