import click
from typing import List, Union
from .Input import Input
from .run import run as rr_run

@click.group(help="runarepo command-line client")
def cli():
    pass

@click.command(help="Run a repo")
@click.argument('repo')
@click.option('--subpath', default=None, help='Relative path within the repo')
@click.option('--input', '-i', help='Input file or directory', multiple=True)
@click.option('--output', '-o', default=None, help='Output directory')
@click.option('--docker', help='Use docker', is_flag=True)
@click.option('--singularity', help='Use singularity', is_flag=True)
@click.option('--image', default=None, help='Docker image to use for docker or singularity mode')
def run(repo, subpath: Union[str, None], input: List[str], output: Union[str, None], docker: bool, singularity: bool, image: Union[str, None]):
    inputs = [
        Input(name=x.split('=')[0], path=x.split('=')[1])
        for x in input
    ]
    rr_run(repo, subpath=subpath, inputs=inputs, output_dir=output, use_docker=docker, use_singularity=singularity, image=image)

cli.add_command(run)
