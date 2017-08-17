# -*- coding: utf-8 -*-

"""Main module."""

import json
from collections import defaultdict
from subprocess import (Popen, PIPE)


def state_pull(root=None):
    """Gather tfstate output from terraform."""
    root = root
    getstate = Popen(['terraform', 'state', 'pull'], cwd=root, stdout=PIPE)
    output, _ = getstate.communicate()
    yield json.loads(output)


def state_resources(sources):
    for source in sources:
        if type(source) in [str, str]:
            with open(source, 'r') as json_file:
                state = json.load(json_file)
        else:
            state = source
            for module in state['modules']:
                name = module['path'][-1]
                for key, resource in list(module['resources'].items()):
                    yield name, key, resource


PARSERS = {}


def state_hosts(resources):
    '''yield host tuples of (name, attributes, groups)'''
    for module_name, key, resource in resources:
        resource_type, name = key.split('.', 1)
        try:
            parser = PARSERS[resource_type]
        except KeyError:
            continue

        yield parser(resource, module_name)


def parses(prefix):
    def inner(func):
        PARSERS[prefix] = func
        return func

    return inner


def parse_dict(source, prefix, sep='.'):
    return dict(_parse_prefix(source, prefix, sep))


def _parse_prefix(source, prefix, sep='.'):
    for compkey, value in list(source.items()):
        try:
            curprefix, rest = compkey.split(sep, 1)
        except ValueError:
            continue

        if curprefix != prefix or rest == '#':
            continue

        yield rest, value


@parses('vsphere_virtual_machine')
def vsphere_host(resource, module_name, **kwargs):
    raw_attrs = resource['primary']['attributes']
    network_attrs = parse_dict(raw_attrs, 'network_interface')
    network = parse_dict(network_attrs, '0')
    ip_address = network.get('ipv4_address', network['ip_address'])
    name = raw_attrs['name']
    groups = []

    attrs = {
        'id': raw_attrs['id'],
        'ip_address': ip_address,
        'private_ipv4': ip_address,
        'public_ipv4': ip_address,
        'metadata': parse_dict(raw_attrs, 'custom_configuration_parameters'),
        'provider': 'vsphere',
    }

    try:
        attrs.update({
            'ansible_ssh_host': ip_address,
        })
    except (KeyError, ValueError):
        attrs.update({'ansible_ssh_host': '', })

    # attrs specific to Ansible
    if 'ssh_user' in attrs['metadata']:
        attrs['ansible_ssh_user'] = attrs['metadata']['ssh_user']

    if 'ansible_group' in attrs['metadata']:
        groups.append(attrs['metadata'].get('ansible_group'))

    return name, attrs, groups


def query_host(hosts, target):
    for name, attrs, _ in hosts:
        if name == target:
            return attrs

    return {}


def query_list(hosts):
    groups = defaultdict(dict)
    meta = {}

    for name, attrs, hostgroups in hosts:
        for group in set(hostgroups):
            groups[group].setdefault('hosts', [])
            groups[group]['hosts'].append(name)

        meta[name] = attrs

    groups['_meta'] = {'hostvars': meta}
    return groups
