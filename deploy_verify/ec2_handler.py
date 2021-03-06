"""Module for to ec2 EC2 deployments
"""
import argparse
import boto.ec2
from operator import attrgetter

REGIONS = [
    'us-east-1', 'us-west-1', 'us-west-2', 'eu-west-1', 'sa-east-1',
    'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1'
]
LINE = '----------------------------'


class EC2Handler(object):

    #def __init__(self):
    #    pass

    def instances_newest(self, region, filters):
        """Get chronologically sorted list of instances

        Retrieves and sorts list of all matching instances chronologically.
        For most operations, we may want just the last one created,
        but for others (like msisdn-gateway), we may want the last few.

        TODO:
            Add specific release number to filter (in the event we have
            multiple versions staged and we want to pick an earlier one.

        Returns:
            sorted list of instances as json object
        """

        sort_by = 'launch_time'

        ec2_conn = boto.ec2.connect_to_region(region)
        reservations = ec2_conn.get_all_instances(filters=filters)
        instances = [i for r in reservations for i in r.instances]

        # sort list, return last element
        return sorted(instances, key=attrgetter(sort_by), reverse=True)

    def instance_properties(self, region, instance):
       
        props = 'EC2 INSTANCE PROPERTIES\n'
        props += 'region: {0}: \nid: {1}\n'.format(region, instance.id)
        try:
            if instance.tags["Type"]:
                props += 'tags["Type"]: {0}\n'.format(instance.tags["Type"])
        except KeyError:
            pass
        try:
            if instance.tags["AppGitRef"]:
                props += 'tags["AppGitRef"]: {0}\n'.format(instance.tags["AppGitRef"])
        except KeyError:
            pass
        try:
            if instance.tags["Stack"]:
                props += 'tags["Stack"]: {0}\n'.format(instance.tags["Stack"])
        except KeyError:
            pass
        props += 'public_dns_name: {0}\n'.format(instance.public_dns_name)
        props += 'launch_time: {0}\n'.format(instance.launch_time)
      
        """
        props = 'EC2 INSTANCE PROPERTIES\n  \
            \nregion: {0}: \nid: {1} \n \
            \ntags["Type"]: {2}  \
            \ntags["AppGitRef"]: {3}\n \
            \ntags["Stack"]: {4}  \
            \npublic_dns_name: {5} \
            \nlaunch_time: {6}\n'.format(
            region,
            instance.id,
            instance.tags['Type'],
            instance.tags['AppGitRef'],
            instance.tags['Stack'],
            instance.public_dns_name,
            instance.launch_time
        )
        """
        return props


def main():

    regions = REGIONS
    ec2 = EC2Handler()
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--region')
    parser.add_argument('-a', '--application',
                        help='Application (i.e. loop-client)')
    args = parser.parse_args()

    application = args.application

    if args.region:
        regions = []
        regions.append(args.region)

    filters = {
        'tag:App': application.replace('-', '_')
    }
    print 'hello'

    for region in regions:
        instances = ec2.instances_newest(region, filters)
        for instance in instances:
            print('--------------------')
            print(ec2.instance_properties(region, instance))


if __name__ == '__main__':

    main()
