import os
from radish import world

env = {
    'host': 'http://{0}:{1}'.format(os.environ['CNTR_DEV'],
                                    os.environ['API_PORT']),
    'input_data': os.environ['FOLDER_INPUT_DATA'],
    'expected_output': os.environ['FOLDER_EXPECTED_OUTPUT']
}

world.env = env

endpoints = {
    'vnsfs': '{0}/{1}'.format(world.env['host'], 'vnsfs')
}

world.endpoints = endpoints
