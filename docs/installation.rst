Installation
============

This role requires at least Ansible ``v1.8.0``. To install it, clone it
to your `DebOps`_ project roles directory::

    git clone http://github.com/ganto/ansible-trac.git

The role also brings its own Ansible module, called ``trac_project`` which
must be included in the Ansible module path by adding the included *modules/*
directory to the ``ANSIBLE_LIBRARY`` environment variable. E.g.:

    ANSIBLE_LIBRARY=/var/lib/debops/myproject/ansible/roles/asible-trac/modules

:: _DebOps: http://debops.org/


Role dependencies
~~~~~~~~~~~~~~~~

* ``debops.ferm``
