"""
Botocore client handler
"""
import os

from collections import OrderedDict
from argparse import ArgumentParser

from botocore.session import Session
from botocore.exceptions import ClientError

from configobj import ConfigObj

DEFAULT_TEMPLATE = "export {key}={value}\n"

CRED_FILE = os.path.join('~', '.aws', 'credentials')
CONFIG_FILE = os.path.join('~', '.aws', 'credentials')

class BotocoreClientHandler(object):
    """
    Client handler class
    """
    def __init__(self, service, session=None, client=None):
        "Initialize"
        self._service = service
        self._session = None
        #self._region = self._session.get_config_variable("region")
        self._region = None
        self._client = None

    def _parse_args(self):
        "Parse command line arguments"

        parser = ArgumentParser(description="Create botocore session and client")

        parser.add_argument('-p', '--profile',
                            action='store',
                            default='default',
                            choices=self._get_available_profiles(),
                            help='Select an available credentials profile')

        parser.add_argument("-t", "--template", default=DEFAULT_TEMPLATE)
        print(parser.parse_args())

        return parser.parse_args()

    def _get_session(self):
        "Get botocore session"

        cred_abs_path = os.path.expanduser(CRED_FILE)
        config_abs_path = os.path.expanduser(CONFIG_FILE)

        if not (os.path.exists(cred_abs_path) and os.path.exists(config_abs_path)):
            raise RuntimeError('AWS credentials or config file not found')

        config = ConfigObj(cred_abs_path)
        print('FOO', config.values())

    def _get_available_profiles(self):
        "Get available profiles from credentials file"

        if not self._session:
            self._get_session()
        print(self._session.available_profiles)
        return self._session.available_profiles

    def create_client(self):
        "Create botocore client"

        print(self._region)
        return self._session.create_client(self._service,
                                           region_name=self._region)

    def lists(self):
        "Lists all repositories"

        aws_res = self._client.describe_repositories(maxResults=2)

        rval = OrderedDict()

        if len(aws_res['respositories']) == 0:
            print('There are no respositories')
            return

        def _get_data(data):
            sval = OrderedDict([('Name', aws_res['repositoryName']),
                                ('ARN', aws_res['repositoryArn']),
                                ('URI', aws_res['repositoryUri']),
                                ('Created', aws_res['createdAt'])])
            rval[aws_res['repositoryName']] = sval

        _get_data(aws_res)

        while aws_res.get('nextToken', False):
            aws_res = self._client.describe_repositories(maxResults=2)
            _get_data(aws_res)


def run():
    "Entry proint"

    obj = BotocoreClientHandler(service='ecr')
    parser = obj._parse_args()
    print(parser.profile)
    session = Session(profile=parser.profile)
    print(dir(session))
    print(session.get_config_variable('region'))
    print(session.get_credentials(), session.profile)

if __name__ == "__main__":
    # execute only if run as a script
    run()