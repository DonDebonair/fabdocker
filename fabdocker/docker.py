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
            return run_local(docker_cmd, capture=True)
        else:
            return run(docker_cmd)

    def ps(self, all=False, local=None):
        cmd = "ps --no-trunc {all}".format(
            all="-a" if all else ""
        )
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
        cmd = "create {name} {volumes} {image}".format(
            name="--name {}".format(name) if name else "",
            volumes=" ".join(["-v {}".format(v) for v in volumes]),
            image=image
        )
        return self(cmd, local)

    def rm(self, container_id, force=False, local=None):
        cmd = "rm {force} {container}".format(
            force="-f" if force else "",
            container=container_id
        )
        return self(cmd, local)

    def inspect(self, container_id, fmt=None, local=None):
        cmd = "inspect {format} {container}".format(
            format="--format='{}'".format(fmt) if fmt else "",
            container=container_id
        )
        result = self(cmd, local)
        return json.loads(result)

    def tag(self, source_image, target_image, source_tag=None, target_tag=None, force=None, local=None):
        cmd = "tag {force} {source_image}{source_tag} {target_image}{target_tag}".format(
            force="-f" if force else "",
            source_image=source_image,
            source_tag=":{}".format(source_tag) if source_tag else "",
            target_image=target_image,
            target_tag=":{}".format(target_tag) if target_tag else ""
        )
        return self(cmd, local)

    def build(self, image, directory, tag=None, local=None):
        cmd = "build -t {image}{tag} {directory}".format(
            image=image,
            tag=":{}".format(tag) if tag else "",
            directory=directory
        )
        return self(cmd, local)

    def pull(self, image, tag=None, local=None):
        cmd = "pull {image}{tag}".format(
            image=image,
            tag=":{}".format(tag) if tag else ""
        )
        return self(cmd, local)

    def login(self, url, username, password, email, local=None):
        cmd = "login -u {user} -p {password} -e {email} {url}".format(
            user=username,
            password=password,
            email=email,
            url=url
        )
        return self(cmd, local)

    def push(self, image, tag=None, local=None):
        cmd = "push {image}{tag}".format(
            image=image,
            tag=":{}".format(tag) if tag else ""
        )
        return self(cmd, local)

    def run(self, image, tag=None, name=None, ports=None, volumes=None, volumes_from=None, env_vars=None, daemon=True, local=None):
        if not volumes:
            volumes = {}
        if not volumes_from:
            volumes_from = []
        if not env_vars:
            env_vars = {}
        if not ports:
            ports = {}
        cmd = "run {name} {daemon} {ports} {volumes} {volumes_from} {environment} {image}{version}".format(
            name="--name {}".format(name) if name else "",
            daemon="-d" if daemon else "",
            ports=" ".join(["-p {}{}".format("{}:".format(v) if v else "", k) for k, v in ports.iteritems()]),
            volumes=" ".join(["-v {}{}".format("{}:".format(v) if v else "", k) for k, v in volumes.iteritems()]),
            volumes_from=" ".join(["--volumes-from {}".format(v) for v in volumes_from]),
            environment=" ".join(["-e {}={}".format(k, v) for k, v in env_vars.iteritems()]),
            image=image,
            version=":{}".format(tag) if tag else ""
        )
        return self(cmd, local)

    def stop(self, container_id, wait_time=None, local=None):
        cmd = "stop {wait_time} {container}".format(
            wait_time="-t {}".format(wait_time) if wait_time else "",
            container=container_id
        )
        return self(cmd, local)

    def replace(self, name, tag='latest', new_image=None, force=False, ports=None, volumes=None, volumes_from=None, env_vars=None, daemon=True, local=None):
        containers = _filter_containers(self.ps(all=False, local=local), name=name)
        if len(containers) > 0:
            container_id = containers[0]['container_id']
            image_name = new_image or containers[0]['image'].keys()[0]
            if force:
                self.rm(container_id, force=True, local=local)
            else:
                if self.inspect(container_id, fmt="{{ .State.Running }}", local=local):
                    self.stop(container_id, local=local)
                self.rm(container_id, local=local)
        else:
            image_name = new_image
        return self.run(image_name, tag=tag, name=name, ports=ports, volumes=volumes, volumes_from=volumes_from, env_vars=env_vars, daemon=daemon, local=local)
