import os
from radish import world

world.env = {
    'host': 'http://{}:{}'.format(os.environ['CNTR_STORE'],
                                  os.environ['API_PORT']),
    'input_data': os.environ['FOLDER_TESTS_INPUT_DATA'],
    'expected_output': os.environ['FOLDER_TESTS_EXPECTED_OUTPUT'],
    'mock-vnsfo-data': os.environ['FOLDER_TESTS_MOCK_VNSFO_DATA'],
    'mock-vnsfo-folder': os.path.join(os.environ['CNTR_FOLDER_VNSFO'], os.environ['VNSFO_API'])
    }

world.endpoints = {
    'vnsfs': '{}/{}'.format(world.env['host'], 'vnsfs')
    }

world.mock_vnsfo_endpoints = {
    'onboard': 'upload'
    }
