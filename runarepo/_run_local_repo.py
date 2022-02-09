import os
import docker
from typing import List, cast, Union
import tarfile
import shutil
import time
import kachery_client as kc
from docker.models.images import Image
from docker.models.containers import Container
from docker.types import Mount

from .consolecapture import ConsoleCapture
from .Input import Input

class RunOutput:
    console_lines = None

def _run_local_repo(
    repo_path: str, *,
    inputs: List[Input]=[],
    output_dir: Union[str, None]=None,
    use_docker: bool=False,
    use_singularity: bool=False,
    image: Union[str, None]=None
):
    if repo_path is not None and not os.path.isabs(repo_path):
        repo_path = os.path.abspath(repo_path)
    if output_dir is not None and not os.path.isabs(output_dir):
        output_dir = os.path.abspath(output_dir)
    if os.path.exists(output_dir):
        raise Exception(f'Output directory already exists: {output_dir}')
    output = RunOutput()
    if use_docker:
        if use_singularity:
            raise Exception('Cannot use both docker and singularity simultaneously')
        client = docker.from_env()
        if image is None:
            docker_image, _ = client.images.build(path=repo_path + '/env')
        else:
            docker_image = client.images.pull(image)
        docker_image = cast(Image, docker_image)
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
            docker_image.id,
            '/repo/run',
            mounts=mounts,
            environment=env
        )
        container = cast(Container, container)
        try:
            output.console_lines = []
            container.start()
            logs = container.logs(stream=True)
            for a in logs:
                for b in a.split(b'\n'):
                    if b:
                        output.console_lines.append({'text': b.decode(), 'timestamp': time.time() - 0, 'stderr': False})
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
    elif use_singularity:
        if image is None:
            raise Exception('Must supply an image when using singularity')
        with kc.TemporaryDirectory() as tmpdir:
            bind_opts = ' '.join([
                f'--bind {input.path}:/inputs/{input.name}'
                for input in inputs
            ])
            env_opts = ' '.join([
                f'--env {input.name}=/inputs/{input.name}'
                for input in inputs
            ])
            os.mkdir(f'{tmpdir}/working')
            with ConsoleCapture() as cc:
                ss = kc.ShellScript(f'''
                #!/bin/bash

                # we really should have the -C option here, but it seems to be causing trouble
                singularity exec \\
                    {bind_opts} \\
                    --bind {tmpdir}/working:/working \\
                    --bind {repo_path}:/repo \\
                    {env_opts} \\
                    --env OUTPUT_DIR=/working/output \\
                    --env WORKING_DIR=/working \\
                    {image} \\
                    /repo/run
                ''')
                print(ss._script)
                ss.start()
                ss.wait()
                if output_dir is not None:
                    shutil.copytree(f'{tmpdir}/working/output', output_dir)
                output.console_lines = cc.lines
    else:
        with kc.TemporaryDirectory() as tmpdir:
            with ConsoleCapture() as cc:
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
                output.console_lines = cc.lines
    return output


