Getting started
===============

.. contents::
   :local:

Default setup
-------------

If you don't specify any configuration values, the role will setup a `nginx`_ instance
running a default installation of the latest Roundcube stable release which is then
accessible via ``https://roundcube.<your-domain>``. It will also setup a `MySQL`_
instance to store profile data of your Roundcube users.

Example inventory
-----------------

You can install Trac on a host by adding it to the ``[debops_trac]`` group
in your Ansible inventory::

    [debops_trac]
    hostname

Example playbook
----------------

Here's an example playbook which uses ``ansible-trac`` role to install Trac::

    ---

    - name: Setup Trac
      hosts: debops_trac

      roles:
        - role: ansible-trac
          tags: trac


.. _nginx: https://github.com/debops/ansible-nginx
.. _MySQL: https://github.com/debops/ansible-mysql

