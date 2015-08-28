## [![DebOps project](http://debops.org/images/debops-small.png)](http://debops.org) trac

This [Ansible](http://ansible.com/) role allows you to install and manage
[Trac](http://trac.edgewall.org/), an enhanced wiki and issue tracking
system for software development projects.

### Installation

This role requires at least Ansible `v1.8.0`. To install it, clone it
to your [DebOps](http://debops.org) project roles directory:

    git clone http://github.com/ganto/ansible-trac.git

### Role dependencies

* ``debops.ferm``

### Are you using this as a standalone role without DebOps?

You may need to include missing roles from the [DebOps common
playbook](https://github.com/debops/debops-playbooks/blob/master/playbooks/common.yml)
into your playbook.

[Try DebOps now](https://github.com/debops/debops) for a complete solution to run your Debian-based infrastructure.

### Authors and license

`trac` role was written by:
- Reto Gantenbein | [e-mail](mailto:reto.gantenbein@linuxmonk.ch) | [GitHub](https://github.com/ganto)

License: [GPLv3](https://tldrlegal.com/license/gnu-general-public-license-v3-%28gpl-3%29)
