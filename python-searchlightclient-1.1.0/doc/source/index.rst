Python bindings to the OpenStack Searchlight API
================================================

This is a client for OpenStack Searchlight API. There's a Python API
(the :mod:`searchlightclient` module), and a command-line script
(installed as :program:`openstack`).

Contributing
============

Code is hosted at `git.openstack.org`_. Submit bugs to the searchlight project
on `Launchpad`_. Submit code to the openstack/python-searchlightclient project
using `Gerrit`_.

.. _git.openstack.org: https://git.openstack.org/cgit/openstack/python-searchlightclient
.. _Launchpad: https://launchpad.net/python-searchlightclient
.. _Gerrit: http://docs.openstack.org/infra/manual/developers.html#development-workflow

Testing
-------

The preferred way to run the unit tests is using ``tox``.

See `Consistent Testing Interface`_ for more details.

.. _Consistent Testing Interface: http://git.openstack.org/cgit/openstack/governance/tree/reference/project-testing-interface.rst

Man Page
========

.. toctree::
   :maxdepth: 1

   man/openstack
   man/search
