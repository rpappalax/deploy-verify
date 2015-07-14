import json


class TestManifest(object):

    def __init__(self, application):

        self.application = application

    #def _test_manifest(self, application):
    def manifest(self, application):

        with open('{0}.json'.format(application)) as data_file:
            return json.load(data_file)

    def urls(self, manifest, env):

        env = env.lower()
        protocols = ['https']
        # TODO: http - need failure check
        # http redirects for loop-client, but not for loop-server
        # protocols = ['http', 'https']
        urls = []
        for key, val in manifest["envs"][env]["urls"].iteritems():
            for protocol in protocols:
                urls.append('{0}://{1}'.format(protocol, val))
        return urls

    def stack_label(self, manifest, env):
        env = env.lower()
        try:
            label = manifest["envs"][env]["stack_label"]
        except KeyError, e:
            print('no stack label found')
            label = None
        return label 

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
            val = 'https://{}'.format(val)
        return val


    def main(self):

        manifest = self._test_manifest(self.application)
        return manifest 

if __name__ == '__main__':

    # example
    application = 'loop-server'
    test = TestManifest(application)
    print test.main()
