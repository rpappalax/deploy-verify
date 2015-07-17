import json
import requests


URL_GITHUB = 'https://raw.githubusercontent.com'
# TODO: once test manifests are hardened, point to:
# REPO = 'mozilla-services/services-test/master'
REPO = 'rpappalax/services-test/master'
KEY = 0
VAL = 1


class TestManifest(object):

    def __init__(self, application):
        self.application = application

    def manifest(self, application):
        url = '{0}/{1}/{2}/manifest.json'.format(
            URL_GITHUB, REPO, application
        ) 
        r = requests.get(url)
        return r.json()
        # FOR LOCAL DEV ONLY 
        #file_path = '/Users/rpappalardo/git/services-test/{}/manifest.json'.format(application)
        #with open(file_path) as data_file:
        #    return json.load(data_file)

    def urls(self, manifest, env):
        env = env.lower()
        protocols = ['https']
        # TODO: http - need failure check
        # http redirects for loop-client, but not for loop-server
        # protocols = ['http', 'https']
        urls = []
        url_root = manifest["envs"][env]["urls"]["root"]
        for key, val in manifest["envs"][env]["urls"].iteritems():
            for protocol in protocols:
                if 'root' in key:
                    # force root url to sort first
                    key = key.replace('root', '_root')
                urls.append([key, val])
                
        urls.sort(key=lambda x: x[0]) 
        urls_new = []
        for url in urls:
            if not '/' in url[KEY]:
                root = url[VAL]
            if '/' in url[KEY]:
                urls_new.append('{0}://{1}/{2}'.format(
                    protocol, root, url[VAL]))
            else:
                urls_new.append('{0}://{1}'.format(protocol, url[VAL]))
        return urls_new

    def region(self, manifest, env):
        env = env.lower()
        try:
            region = manifest["envs"][env]["aws_region"]
        except KeyError, e:
            print('no region found')
            region = None
        return region 

    def stack_label(self, manifest, env):
        env = env.lower()
        try:
            label = manifest["envs"][env]["stack_label"]
        except KeyError, e:
            print('no stack_label found')
            label = None
        return label 

    def environments(self, manifest, env_selected):
        """Returns environments and their corresponding stack label 
        as json string
        
        Example:
            For msisdn-gateway, if env_match=="STAGE", we return:
            {
              u'stage': u'msisdnstage',
              u'stage-loadtest': u'msisdnload',
            }
        """

        envs_matching = {}  
        env_selected = env_selected.lower()
        environments = manifest["envs"].keys()
        for environment in environments:
            if env_selected in environment:
                envs_matching.update(
                    {environment: manifest["envs"][environment]["stack_label"]}
                )    
        return envs_matching

    def substitute_param(self, manifest, env, val):
        """If we have a param in brackets, we substitute it for an url
        with a key indicated:  <key_name_here>

        Example:
            <root> becomes:  https://xxx.services.mozilla.com
        """

        import re
        env = env.lower()
        param = re.search(r'<(.*)>', val)
        if param:
            key_substitute = param.group(1)
            val = manifest["envs"][env]["urls"][key_substitute]
            val = 'https://{0}'.format(val)
        return val


    def main(self):

        manifest = self._test_manifest(self.application)
        return manifest 

if __name__ == '__main__':

    # example
    application = 'loop-server'
    test = TestManifest(application)
    print test.main()
