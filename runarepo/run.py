import os
from threading import local
from typing import Union, List
import kachery_client as kc
from ._run_local_repo import _run_local_repo
from .Input import Input

def run(
    repo: str, *,
    subpath: Union[str, None]=None,
    inputs: List[Input]=[],
    output_dir: Union[str, None]=None,
    use_docker: bool=False,
    use_singularity: bool=False,
    image: Union[str, None]=None
):
    def helper(local_path: str):
        if subpath is not None:
            local_path = local_path + '/' + subpath
        _run_local_repo(local_path, inputs=inputs, output_dir=output_dir, use_docker=use_docker, use_singularity=use_singularity, image=image)
    if repo.startswith('http://') or repo.startswith('https://') or repo.startswith('git://'):
        with kc.TemporaryDirectory() as tmpdir:
            local_path = f'{tmpdir}/repo'
            ss = kc.ShellScript(f'''
            #!/bin/bash
            git clone {repo} {local_path}
            ''')
            ss.start()
            ss.wait()
            helper(local_path)
    elif os.path.isdir(repo):
        helper(repo)
    else:
        raise Exception(f'Not a directory: {repo}')
    
    