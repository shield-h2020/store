import os
from radish import world

world.env = {
    'hosts': {
        'backend_api': {
            'host': '{}://{}:{}'.format(os.environ['BACKENDAPI_PROTOCOL'], os.environ['CNTR_STORE'],
                                        os.environ['BACKENDAPI_PORT'])
            },
        'vnsfo': {
            'host': '{}://{}:{}/{}'.format(os.environ['VNSFO_PROTOCOL'], os.environ['VNSFO_HOST'],
                                           os.environ['VNSFO_PORT'], os.environ['VNSFO_API'])
            }
        },
    'data': {
        'input_data': os.environ['FOLDER_TESTS_INPUT_DATA'],
        'expected_output': os.environ['FOLDER_TESTS_EXPECTED_OUTPUT'],
        },
    'mock': {
        'vnsfo_data': os.environ['FOLDER_TESTS_MOCK_VNSFO_DATA'],
        'vnsfo_folder': os.path.join(os.environ['CNTR_FOLDER_VNSFO'], os.environ['VNSFO_API'])
        }
    }

world.endpoints = {
    'vnsfs': '{}/{}'.format(world.env['hosts']['backend_api']['host'], 'vnsfs'),
    'nss': '{}/{}'.format(world.env['hosts']['backend_api']['host'], 'nss')
    }

world.mock_vnsfo_endpoints = {
    'onboard_vnsf': 'package/r2/onboard',
    'onboard_ns': 'package/r2/onboard',
    }
