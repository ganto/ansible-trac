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
   db_type:
     description:
        - Type of database backend.
     choices: [ 'sqlite', 'mysql', 'postgresql' ]
     default: sqlite
   db_host:
     description:
        - Host name of database. Only used with db_type 'mysql' or 'postgresql'.
     default: localhost
   db_user:
     description:
        - Database user name. Only used with db_type 'mysql' or 'postgresql'.
          If unspecified the project name will be used as user name.
     default: Value of the project name
   config:
     description:
        - List of trac.ini configuration parameters.
          Syntax: { 'section': INI-section, 'option': option, 'value': value }
     default: []
requirements: [ 'trac', 'MySQL-python', 'python-psycopg2' ]
notes:
  - The 'MySQL-python' package is only used if 'mysql' is used as db_type.
  - The 'python-psycopg2' package is only used if 'postgresql' is used as db_type.
"""

EXAMPLES = """
# Create new Trac project with name 'myproject'
- trac_project: name='myproject' path='/srv/trac/myproject'
"""

import ConfigParser
try:
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
        self.project_name = self.module.params['name']
        self.project_path = self.module.params['path']

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

    def _project_data(self):
        """Returns a dict of project information.

        :returns: project data
        :rtype: ``dict``
        """
        return {
            'name': self.project_name,
            'path': self.project_path
        }

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
                trac_ini = os.path.join(self.module.params['path'], 'conf', 'trac.ini')

                if not os.path.exists(trac_ini):
                    self.failure(
                        error='trac.ini: No such file',
                        rc=1,
                        msg='Project configuration not found [ %s ]' % trac_ini
                    )
                old_config.readfp(open(trac_ini))

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
        if not self.module.params['db_type'] == 'sqlite':
            db_url = "%s://%s:%s@%s/%s" % (
                self.module.params['db_type'],
                self.module.params['db_user'],
                'p4s5w0rD',
                self.module.params['db_host'],
                self.project_name
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
            project_env = Environment(self.project_path, create=False, options=project_options)
            project_env.shutdown()    

    def failure(self, **kwargs):
        """Return a Failure when running an Ansible command.

        :param error: ``str``  Error that occurred.
        :param rc: ``int``     Return code while executing an Ansible command.
        :param msg: ``str``    Message to report.
        """

        self.module.fail_json(**kwargs)

    def run(self):
        """Run the main method."""

        self._project_setup()
        outcome = self._project_data()

        self.module.exit_json(
            changed=self.state_change,
            trac_project=outcome
        )


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
            db_type=dict(
                choices=TRAC_ANSIBLE_DB_TYPES,
                default='sqlite',
                required=False
            ),
            db_host=dict(
                type='str',
                default='localhost',
                required=False
            ),
            db_user=dict(
                type='str',
                required=False
            ),
            config=dict(
                type='list',
                default=None,
                required=False
            )
        )
    )

    trac_manager = TracProjectManager(module=module)
    trac_manager.run()

# import module bits
from ansible.module_utils.basic import *
main()
