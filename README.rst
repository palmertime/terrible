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


Installation
------------

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
-----

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


Features
--------

Terraform Resources:
^^^^^^^^^^^^^^^^^^^^

* VMware vSphere (`vsphere_virtual_machine`_)
* AWS Instance (`aws_instance`_)

.. _`vsphere_virtual_machine`: https://www.terraform.io/docs/providers/vsphere/r/virtual_machine.html
.. _`aws_instance`: https://www.terraform.io/docs/providers/aws/r/instance.html


Common Parameters
^^^^^^^^^^^^^^^^^

These can be specified by all resources. Uniq configuration details are
documented in specific sections below.

**ansible_user** (Optional)
  The user that Ansible will connect to the host. Defaults to root if not specified.

**ansible_group** (Optional)
  The inventory group associated with the resource. (Add default All group?)

**ansible_host** (Optional)
  The host that Ansible will connect to. VMware defaults to IP of 1st interface,
  ``network_interface:0`` but if can be overwriten to an specific IP. AWS
  defaults to ``public_ip`` and configuralbe to ``private_ip``.
  (TODO:  Add test and error condition for values)


VMware
^^^^^^

When defining Terraform ``vsphere_virtual_machine`` resource use the
``custom_configuration_parameters`` block to set Ansible parameters.

Configuration example::

    custom_configuration_parameters {
      ansible_group = "api-gateway"
      ansible_user = "ansible"
      ansible_host = "192.168.52.101"
    }


AWS
^^^

When defining a Terraform ``aws-instance`` resource use tags to set Ansible
parameters.

**ansible_ssh_private_key_file**
  The key used to connect to AWS instance. The value is the path to the private
  key that matches the defined AWS instance key_name. Defaults to the value of
  ``key_name + .pem``. EXAMPLE: If your AWS instance key_name is ``terraform``
  then Ansible would look in the current working directory for terraform.pem

Configuration example::

    tags {
      Name = "app1-aws"
      ansible_groups = "webapp"
      ansible_user = "ansible"
      ansible_host = "private_ip"
      ansible_ssh_private_key_file = "aws-keys/webapp-terraform.pem"
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
