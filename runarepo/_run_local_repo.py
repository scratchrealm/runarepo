import os
import docker
from typing import List, cast, Union
import tarfile
import shutil
import kachery_client as kc
from docker.models.images import Image
from docker.models.containers import Container
from docker.types import Mount
from .Input import Input

def _run_local_repo(
    repo_path: str, *,
    inputs: List[Input]=[],
    output_dir: Union[str, None]=None,
    use_docker: bool=False
):
    if repo_path is not None and not os.path.isabs(repo_path):
        repo_path = os.path.abspath(repo_path)
    if output_dir is not None and not os.path.isabs(output_dir):
        output_dir = os.path.abspath(output_dir)
    if os.path.exists(output_dir):
        raise Exception(f'Output directory already exists: {output_dir}')
    if use_docker:
        client = docker.from_env()
        image, _ = client.images.build(path=repo_path + '/env')
        image = cast(Image, image)
        mounts: List[Mount] = []
        env = {}
        for input in inputs:
            source = input.path
            if not os.path.isabs(source):
                source = os.path.abspath(source)
            target = f'/inputs/{input.name}'
            mounts.append(Mount(target=target, source=source, type='bind', read_only=True))
            env[input.name] = target
        mounts.append(Mount(target='/repo', source=repo_path, type='bind', read_only=True))
        env['OUTPUT_DIR'] = '/output'
        env['WORKING_DIR'] = '/working'
        container = client.containers.create(
            image.id,
            '/repo/run',
            mounts=mounts,
            environment=env
        )
        container = cast(Container, container)
        try:
            container.start()
            logs = container.logs(stream=True)
            for a in logs:
                for b in a.split(b'\n'):
                    if b:
                        print(b.decode())
            if output_dir is not None:
                os.mkdir(output_dir)
                with kc.TemporaryDirectory() as tmpdir:
                    strm, st = container.get_archive(path='/output/')
                    output_tar_path = tmpdir + '/output.tar.gz'
                    with open(output_tar_path, 'wb') as f:
                        for d in strm:
                            f.write(d)
                    with tarfile.open(output_tar_path) as tar:
                        tar.extractall(tmpdir)
                    for fname in os.listdir(tmpdir + '/output'):
                        shutil.move(tmpdir + '/output/' + fname, output_dir + '/' + fname)
        finally:
            try:
                container.kill()
            except:
                pass
            container.remove()
    else:
        with kc.TemporaryDirectory() as tmpdir:
            script = '#!/bin/bash\n\n'
            if output_dir is not None:
                script += f'export OUTPUT_DIR={output_dir}\n'
            script += f'export WORKING_DIR={tmpdir}\n'
            for input in inputs:
                script += f'export {input.name}="{input.path}"\n'
            script += f'\n'
            script += f'{repo_path}/run'
            ss = kc.ShellScript(script)
            ss.start()
            ss.wait()


