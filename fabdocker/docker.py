from fabric.api import local as run_local, run, env, hide, show
import json

def _check_local(local_param, fabenv):
    return local_param or (fabenv.get("docker_local", False) and local_param is not False)


def _filter_containers(containers, name=None, image=None, version=None):
    return [c for c in containers
            if (not name or name in c['names'])
            and (not image or image in c['image'])
            and (not version or version in c['image'].values())]


class Docker(object):

    def __call__(self, cmd, local=None):
        docker_cmd = "docker {}".format(cmd)
        if _check_local(local, env):
            output = hide("stderr") if env.get("docker_verbose", False) else hide("stdout")
            with output:
                return run_local(docker_cmd, capture=True)
        else:
            output = show("stdout", "stderr", "running") if env.get("docker_verbose", False) else hide("stdout", "stderr")
            with output:
                return run(docker_cmd)

    def ps(self, all=False, local=None):
        cmd = "ps --no-trunc"
        cmd += " -a" if all else ""
        result = self(cmd, local).replace("\r", "").split("\n")
        header = result[0]
        body = result[1:]
        fragments = {
            'container_id': {'start': header.index("CONTAINER ID"), 'end': header.index("IMAGE")},
            'image': {'start': header.index("IMAGE"), 'end': header.index("COMMAND")},
            'command': {'start': header.index("COMMAND"), 'end': header.index("CREATED")},
            'created': {'start': header.index("CREATED"), 'end': header.index("STATUS")},
            'status': {'start': header.index("STATUS"), 'end': header.index("PORTS")},
            'ports': {'start': header.index("PORTS"), 'end': header.index("NAMES")},
            'names': {'start': header.index("NAMES"), 'end': None}
        }
        containers = []
        for line in body:
            container = {}
            for k, v in fragments.iteritems():
                container[k] = line[v['start']:v['end']].strip()
            container['names'] = line[header.index("NAMES"):].strip().split(",")
            image_parts = line[header.index("IMAGE"):header.index("COMMAND")].strip().split(":")
            container['image'] = {image_parts[0]: image_parts[1]}
            containers.append(container)
        return containers

    def exists(self, name=None, image=None, version=None, local=None):
        return len(_filter_containers(self.ps(all=True, local=local), name, image, version)) > 0

    def running(self, name=None, image=None, version=None, local=None):
        return len(_filter_containers(self.ps(all=False, local=local), name, image, version)) > 0

    def create(self, image, name=None, volumes=None, local=None):
        if not volumes:
            volumes = []
        cmd = "create"
        cmd += " --name {}".format(name) if name else ""
        cmd += "".join([" -v {}".format(v) for v in volumes])
        cmd += " {}".format(image)
        return self(cmd, local)

    def rm(self, container_id, force=False, local=None):
        cmd = "rm"
        cmd += "-f" if force else ""
        cmd += " {}".format(container_id)
        return self(cmd, local)

    def inspect(self, container_id, fmt=None, local=None):
        cmd = "inspect"
        cmd += " --format='{}'".format(fmt) if fmt else ""
        cmd += " {}".format(container_id)
        result = self(cmd, local)
        return json.loads(result)

    def run(self):
        pass

    def stop(self):
        pass

    def replace(self):
        pass