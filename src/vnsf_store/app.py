from flask import Flask
from flask_restful_swagger_2 import Api

from common import constants as const
from endpoints import resources
import endpoints_base

app = Flask(__name__)
api = Api(app,
          title='vNSF Store API',
          api_version='0.1',
          base_path='/localhost:5000/',
          produces=const.API_RESPONSE_TYPE,
          api_spec_url='/docs',
          description='''
This API onboards vNSFs and NSs in a secure and trusted way. The onboarding process will ensure the provenance is
from a trusted source and that the contents integrity can be assured. Once this is achieved the security information
is stored for safekeeping and provided upon request so other components can check that the vNSF/NS has not been
tampered with since it was onboarded.
<p>
Another relevant feature provided by the Store is the verification done on the vNSF and NS associated descriptors to
ensure the instantiation process by an Orchestrator is performed without hassle.
</p>
''',
          tags=[{'name': endpoints_base.ENDPOINT_VNSFS,
                 'description': 'vNSF operations'}])

for endpoint in resources:
    api.add_resource(endpoint['handler'], endpoint['resource'])

if __name__ == '__main__':
    # Ensure Flask connections are listened for on all network cards (as loopback is an interface on its own).
    # Docker Rails app fails to be served - curl: (56) Recv failure: Connection reset by peer
    # https://stackoverflow.com/questions/27806631/docker-rails-app-fails-to-be-served-curl-56-recv-failure
    # -connection-reset
    # The answer is applicable to Flask as well.
    app.run(host='0.0.0.0', port=5050, debug=True)
