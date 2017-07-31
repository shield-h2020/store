import requests


class VnsfOrchestratorApi:
    """
    Interface with the vNSF Orchestrator through it's API.
    """

    def __init__(self, server, port, api_basepath):
        if port is not None:
            server += ':' + port

        self.basepath = 'http://{}/{}'.format(server, api_basepath)

    def onboard_vnsf(self, tenant_id, vnsf_package_path):
        url = '{}/{}/vnsfs'.format(self.basepath, str(tenant_id))
        r = requests.post(url)
        return r.status_code == 200
