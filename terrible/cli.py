# -*- coding: utf-8 -*-

"""Console script for terrible."""
from __future__ import absolute_import

import json
import click
from .terrible import (state_pull, state_resources, state_hosts, query_list,
                       query_host)


@click.command()
@click.option('--host', help='Show varibles for single host')
@click.option('listvars', '--list', is_flag=True, help='List all variables')
@click.option('--nometa', is_flag=True, help='Remove _meta from output')
@click.option('--pretty', is_flag=True, help='Make json look pretty')
@click.argument('root', envvar='TERRAFORM_ROOT', default='terraform',
                type=click.Path(exists=True))
def main(host, listvars, nometa, pretty, root):
    """Console script for terrible."""
    hosts = state_hosts(state_resources(state_pull(root)))
    if listvars:
        output = query_list(hosts)
        if nometa:
            del output['_meta']
        click.echo(json.dumps(output, indent=4 if pretty else None))
    elif host:
        output = query_host(hosts, host)
        click.echo(json.dumps(output, indent=4 if pretty else None))


if __name__ == "__main__":
    main()
