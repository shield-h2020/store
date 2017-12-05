# -*- coding: utf-8 -*-

import os
import re
from radish import when, world
from shutil import copyfile
from storetestingutils.steps_utils import *


@when(re.compile(u'I onboard a NS (.*)'))
def ns_onboard(step, package):
    # Set proper vNSFO response.
    dest_file = os.path.join(world.env['mock']['vnsfo_folder'], world.mock_vnsfo_endpoints['onboard_ns'],
                             'index.post.json')
    dest_path = os.path.dirname(dest_file)
    if not os.path.exists(dest_path):
        os.makedirs(dest_path, exist_ok=True)

    src_file = os.path.join(world.env['mock']['vnsfo_data'], step.context.mock_vnsfo['response_file'])
    assert os.path.isfile(src_file)
    copyfile(src_file, dest_file)

    # Onboard NS with the Orchestrator.
    with open(os.path.join(world.env['data']['input_data'], package), 'rb') as f:
        files = {'package': f}
        http_post_file(step, world.endpoints['nss'], files)
