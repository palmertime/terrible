========
terrible
========


.. image:: https://img.shields.io/pypi/v/terrible.svg
        :target: https://pypi.python.org/pypi/terrible

.. image:: https://img.shields.io/travis/palmertime/terrible.svg
        :target: https://travis-ci.org/palmertime/terrible

.. image:: https://readthedocs.org/projects/terrible/badge/?version=latest
        :target: https://terrible.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/palmertime/terrible/shield.svg
     :target: https://pyup.io/repos/github/palmertime/terrible/
     :alt: Updates


Terrible (TERRaform to ansIBLE) creates dynamic Ansible inventory from Terraform
state.


* Free software: Apache Software License 2.0
* Documentation: https://terrible.readthedocs.io.


Features
--------

Terraform Resources:
^^^^^^^^^^^^^^^^^^^^

* VMware vSphere (`vsphere_virtual_machine`_)

.. _`vsphere_virtual_machine`: https://www.terraform.io/docs/providers/vsphere/r/virtual_machine.html


Installation
^^^^^^^^^^^^

To install terrible, run this command in your terminal.::

  $ pip install terrible

Once installed a symbolic link or shell script can be added to the Ansible
inventory directory.

Symbolic link.::

  $ ln -s /path/to/terrible inventory/terrible

Simple shell script wrapper.::
  #!/usr/bin/env bash
  terrible "$@"


Usage
^^^^^

::

  Usage: terrible [OPTIONS] <root_dir>

    Terrible extracts Ansible inventory data from Terraform state. The
    <root_dir> is relative to the directory where Ansible is executed but
    defaults to ./terraform in the current directory.

  Options:
    --host TEXT  Show varibles for single host
    --list       List all variables
    --nometa     Remove _meta from output
    --pretty     Make json look pretty
    --help       Show this message and exit.

VMware
^^^^^^

When defining a Terraform ``vsphere_virtual_machine`` resource use the ``custom_configuration_parameters`` block to set Ansible parameters.

**ansible_ssh_user**
  The user that Ansible will connect with.

**ansible_group**
  The inventory group that is associated with the resource.

Configuration example::

    custom_configuration_parameters {
      ansible_group = "api-gateway"
      ansible_ssh_user = "ansible"
    }


Directory Layout
^^^^^^^^^^^^^^^^

By default, Terrible looks for the ``terraform`` inside the Ansible playbook root directory.::

    .
    ├── ansible.cfg
    ├── inventory
    │   ├── group_vars
    │   └── terrible
    ├── playbooks
    │   └── site.yml
    ├── requirements.yml
    ├── roles
    │   └── example_role
    └── terraform
        ├── terraform.tf
        ├── terraform.tfstate
        ├── terraform.tfvars
        └── variables.tf

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

This package was greatly influenced by the `sean-abbott/terraform.py`_ project.

.. _`sean-abbott/terraform.py`: https://github.com/sean-abbott/terraform.py
