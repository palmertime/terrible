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


def parse_attr_list(source, prefix, sep='.'):
    attrs = defaultdict(dict)
    for compkey, value in _parse_prefix(source, prefix, sep):
        idx, key = compkey.split(sep, 1)
        attrs[idx][key] = value

    return list(attrs.values())


def parse_dict(source, prefix, sep='.'):
    return dict(_parse_prefix(source, prefix, sep))


def parse_list(source, prefix, sep='.'):
    return [value for _, value in _parse_prefix(source, prefix, sep)]


def parse_bool(string_form):
    token = string_form.lower()[0]

    if token == 't':
        return True
    elif token == 'f':
        return False
    else:
        raise ValueError('could not convert %r to a bool' % string_form)


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
    metadata = parse_dict(raw_attrs, 'custom_configuration_parameters')
    groups = []

    attrs = {
        'provider': 'vsphere',
    }

    try:
        attrs.update({
            'ansible_host': ip_address,
        })
    except (KeyError, ValueError):
        attrs.update({'ansible_host': '', })

    if 'ansible_user' in metadata:
        attrs['ansible_user'] = metadata['ansible_user']
    else:
        attrs['ansible_user'] = 'root'

    if 'ansible_host' in metadata:
        attrs['ansible_host'] = metadata['ansible_host']

    if 'ansible_group' in metadata:
        groups.append(metadata.get('ansible_group'))


    return name, attrs, groups


@parses('aws_instance')
def aws_host(resource, module_name, **kwargs):
    raw_attrs = resource['primary']['attributes']
    if 'tags.Name' in raw_attrs:
        name = raw_attrs['tags.Name']
    else:
        name = resource['id']

    groups = []

    attrs = {
        'provider': 'aws',
        'ansible_host': raw_attrs['public_ip'],
    }
    attrs['ansible_ssh_private_key_file'] = raw_attrs['key_name'] + ".pem"

    # attrs specific to Ansible
    if 'tags.ansible_user' in raw_attrs:
        attrs['ansible_user'] = raw_attrs['tags.ansible_user']
    else:
        attrs['ansible_user'] = 'root'

    if 'tags.ansible_host' in raw_attrs:
        if raw_attrs['tags.ansible_host'] == 'private_ip':
            attrs['ansible_host'] = raw_attrs['private_ip']

    if 'tags.ansible_ssh_private_key_file' in raw_attrs:
        attrs['ansible_ssh_private_key_file'] = raw_attrs[
            'tags.ansible_ssh_private_key_file']

    if 'tags.ansible_groups' in raw_attrs:
        groups.append(raw_attrs['tags.ansible_groups'])

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
