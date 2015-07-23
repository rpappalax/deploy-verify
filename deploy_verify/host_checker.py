import json
from fabric.api import run, env
from deploy_verify.ec2_handler import EC2Handler

REQUEST_TIMEOUT = 3.0
LINE = '----------------------------'


class FabricException(Exception):
    pass


class HostChecker(object):

    def __init__(
        self, jump_host_uri, application, tag_num,
        env_selected, host_string, instance_properties,
        test_manifest
    ):


        self.instance_properties = instance_properties
        self.test_manifest = test_manifest

        # Fabric settings
        env.gateway = jump_host_uri
        env.hosts = [
            host_string
        ]
        env.forward_agent = True
        env.host_string = host_string

        self.application = application
        self.tag_num = tag_num
        self.env_selected = env_selected

    def _header_label(self, env=''):

        if env:
            env = '({0})'.format(env.upper())
        label = 'HOST CHECKS {0}'.format(env)
        return '{0}\n{1}\n{2}\n\n'.format(LINE, label, LINE)

    def _http_request(self, url):
        # requests: r.status_code, r.headers, r.content

        import requests
        out = ''

        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response_time = requests.get(url).elapsed.total_seconds() 
            if response.history:
                out += "Request was redirected!\n"
                for resp in response.history:
                    print resp.status_code, resp.url
                out += 'status code: {0} --> destination: {1}\n'.format(
                    response.status_code, response.url)
            else:
                try:
                    j = json.loads(response.content)
                    out += json.dumps(j, indent=4)
                except ValueError:
                    out = response.content
            out += '\nResponse time: {0}\n'.format(response_time)
        except requests.exceptions.Timeout:
            out += ">>> ERROR! Request timed out! <<<\n"
        return out + '\n\n'

    def get_version_txt(self):

        """
        Note:
            this will be deprecated once vers.json is out
            curl -s https://accounts.firefox.com/ver.json ; echo;
            {"version":"0.39.0","commit":"229d43d28d58b3c6014b393187fd378831e8ac84","l10n":"90a7cd2884","tosPp":"3e3426f74e"}
        """
        out = ''
        if self.application == 'loop-server':
            cmd = 'cat /data/{0}/VERSION.txt'.format(self.application)
        else:
            cmd = 'cat /data/{0}/content/VERSION.txt'.format(self.application)
        out += '$ {0}:\n'.format(cmd)
        out += run(cmd) + '\n\n'
        return out

    def package_version(self):

        """
        Note:
            this will be deprecated once vers.json is out
            curl -s https://accounts.firefox.com/ver.json ; echo;
            {"version":"0.39.0","commit":"229d43d28d58b3c6014b393187fd378831e8ac84","l10n":"90a7cd2884","tosPp":"3e3426f74e"}
        """
        out = ''
        cmd = ''
        if self.application == 'loop-server':
            cmd = 'sed -n "/version/p" /data/{0}/package.json'.format(
                self.application
            )
            out += '$ {0}:\n'.format(cmd)

            try:
                out += run(cmd) + '\n\n'
            except FabricException:
                print('ERROR: unable to run command - {0}'.format(cmd))
                exit(1)
        return out

    # @TODO: check this against git tag
    def verify_githash(self, githash):

        return 'c3db82a'

    def substitute_param(self, manifest, env, val):

        import re
        # TODO: we need to pass env var
        env = env.lower()
        # if we have a param in brackets, we substitute it for an url
        # with a key indicated:  <key_name_here>
        # example:
        # <root> becomes:  https://xxx.services.mozilla.com
        param = re.search(r'<(.*)>', val)
        if param:
            key_substitute = param.group(1)
            val = manifest["envs"][env]["urls"][key_substitute]
            val = 'https://{0}'.format(val)
        return val

    def verify_commands(self, manifest, env):

        out = ''
        for key, vals in manifest["commands"].iteritems():
            for val in vals:
                val = self.substitute_param(manifest, env, val)
                cmd = '{0} {1}'.format(key, val)
                out += '$ {0}:\n'.format(cmd)
                out += run(cmd)
                # remove blank lines
                out = "".join(
                    [s for s in out.strip().splitlines(True)
                        if s.strip("\r\n")]
                )
        return '{0}\n\n\n'.format(out)

    def verify_processes(self, manifest):
        """
        We use ps instead of pgrep - it's easier to grep for processes by name.

        grepping must be in the form [p]rocessname, so the process grep action
        isnt' counted.

        more verbose awk statement to get more info:
        cmd_awk = "awk '{print $1\" \"$2\" \"$8\" \"$9}'"
        """
        out_cmds = ''
        running = []
        not_running = []

        processes = manifest["processes"]
        for p in processes:
            cmd_ps = 'ps -ef'
            cmd_grep = 'grep [{0}]{1}'.format(p[:1], p[1:])
            cmd_awk = "awk '{print $1}'"
            cmd_wc = 'wc -l'
            cmd = "{0} | {1} | {2} | {3}".format(
                cmd_ps, cmd_grep, cmd_awk, cmd_wc)
            result = int(run(cmd))
            if result >= 1:
                running.append(str(p))
            else:
                not_running.append(str(p))

        running = ', '.join(running)
        not_running = ', '.join(not_running)

        if len(running) > 0:
            out_cmds += '{0} --> Running!\n'.format(running)
        if len(not_running) > 0:
            # TODO: if not running, we'll need to return a FAIL flag
            out_cmds += '{0} --> NOT RUNNING!!!\n'.format(not_running)
        return out_cmds + '\n\n'

    def get_linux_version(self):

        out = ''
        cmd = 'cat /etc/*release'
        out += '$ {0}:\n'.format(cmd)
        out += run(cmd) + '\n\n'
        return out

    def diskspace(self):

        # Use to check disk space before / after loadtest
        return run('df') + '\n\n'

    def main(self, manifest):

        out = ''
        env_selected = self.env_selected.lower()

        environment = self.env_selected
        out += self._header_label(environment)

        out += '{0}\n\n'.format(self.instance_properties)

        # out += 'PACKAGE VERSION\n\n'
        # out += str(self.package_version())

        if 'processes' in manifest and env_selected != 'PRODUCTION':
            out += 'PROCESS CHECK\n\n'
            out += str(self.verify_processes(manifest))

        if 'commands' in manifest:
            out += str(self.verify_commands(manifest, environment))

        # Use for loadtest pre/post check only
        #out += 'DISK SPACE\n\n'
        #out += self.diskspace()
        return out

if __name__ == '__main__':

    # env vars
    import os
    bastion_username = os.environ["BASTION_USERNAME"]
    bastion_host = os.environ["BASTION_HOST"]
    bastion_port = os.environ["BASTION_PORT"]
    bastion_host_uri = '{0}@{1}:{2}'.format(
        bastion_username, bastion_host, bastion_port
    )

    # example
    application = 'loop-server'
    tag_num = '0.17.7'
    ec2 = EC2Handler()
    host_string = '<elb_host_string_here.compute.amazonaws.com>'

    checker = HostChecker(bastion_host_uri, application, tag_num, host_string)

    print '================'
    checker.main()
