import click
from .Input import Input
from .run import run as rr_run

@click.group(help="runarepo command-line client")
def cli():
    pass

@click.command(help="Run a repo")
@click.argument('repo_or_image')
@click.option('--subpath', help='Relative path within the repo')
@click.option('--input', '-i', help='Input file or directory mounts', multiple=True)
@click.option('--output', '-o', help='Output directory')
def run(repo_or_image, subpath, input, output):
    inputs = [
        Input(source=x.split(':')[0], target=x.split(':')[1])
        for x in input
    ]
    rr_run(repo_or_image, subpath=subpath, inputs=inputs, output_dir=output)

cli.add_command(run)
