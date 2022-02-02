import os
from threading import local
from typing import Union, List
import kachery_client as kc
from ._run_local_repo import _run_local_repo
from .Input import Input

def run(
    repo_or_image: str, *,
    subpath: Union[str, None]=None,
    inputs: List[Input]=[],
    output_dir: Union[str, None]=None
):
    def helper(local_path: str):
        if subpath is not None:
            local_path = local_path + '/' + subpath
        dockerfile = f'{local_path}/Dockerfile'
        if not os.path.isfile(dockerfile):
            raise Exception(f'File not found: {dockerfile}')
        _run_local_repo(local_path, inputs=inputs, output_dir=output_dir)
    if repo_or_image.startswith('docker://'):
        raise Exception('Not yet supported')
    elif repo_or_image.endswith('.sif'):
        raise Exception('Not yet supported')
    elif repo_or_image.startswith('http://') or repo_or_image.startswith('https://') or repo_or_image.startswith('git://'):
        with kc.TemporaryDirectory() as tmpdir:
            local_path = f'{tmpdir}/repo'
            ss = kc.ShellScript(f'''
            #!/bin/bash
            git clone {repo_or_image} {local_path}
            ''')
            ss.start()
            ss.wait()
            helper(local_path)
    elif os.path.isdir(repo_or_image):
        helper(repo_or_image)
    else:
        raise Exception(f'Not a directory: {repo_or_image}')
    
    