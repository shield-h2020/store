import logging

import requests


class VnsfOrchestratorApi:
    """
    Interface with the vNSF Orchestrator through it's API.
    """

    def __init__(self, server, port, api_basepath, logger=None):
        self.logger = logger or logging.getLogger(__name__)

        if port is not None:
            server += ':' + port

        self.basepath = 'http://{}/{}'.format(server, api_basepath)
        self.logger.info('vNSF Orchestrator API at: {}'.format(self.basepath))

    def onboard_vnsf(self, tenant_id, vnsf_package_path):
        url = '{}/{}/vnsfs'.format(self.basepath, str(tenant_id))
        self.logger.info("Onboard vNSF package '{}' to '{}'".format(vnsf_package_path, url))

        r = requests.post(url)
        return r.status_code == 200
