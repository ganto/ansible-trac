Default variables: configuration
================================

Some of the ``debops.trac`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _trac_project_map:

trac_project_map
----------------

List of configuration dictionaries for defining Trac projects. Each project
is a separate Trac instance with independant users, repositories, issues, ...
Each project is defined as a YAML dict with the following keys:

``name``
  Name of the project, required.

``user``
  Optional. User account owning the project's directory structure.

``group``
  Optional. Primary group of the user owning the project's directory.

``tracd``
  Optional. Boolean indicating if the integrated standalone HTTP server
  should be used. 

``tracd_address``
  Optional. Listen address for the ``tracd`` service.

``tracd_port``
  Optional. Port used with the ``tracd``. Must be a number >1024.

``config``
  Optional. List of YAML dicts defining ``trac.ini`` configuration
  parameters. Each configuration entry must define the following keys:

  ``section``
  Configuration section.

  ``option``
  Configuration option name.

  ``value``
  Configuration value.
