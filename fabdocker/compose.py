from fabric.api import local as run_local, run, env
from docker import _check_local



class Compose(object):

    def __call__(self, cmd, local=None):
        docker_cmd = "docker-compose {}".format(cmd)
        if _check_local(local, env):
            return run_local(docker_cmd, capture=True)
        else:
            return run(docker_cmd)

    def up(self, daemon=True, recreate=True, compose_file=None, local=None):
        cmd = "up {daemon} {recreate} {file}".format(
            daemon="-d" if daemon else "",
            recreate="--no-recreate" if not recreate else "",
            file="-f {}".format(compose_file) if compose_file else ""
        )
        self(cmd, local)
