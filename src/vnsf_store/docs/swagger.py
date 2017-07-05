from flask import Flask
from flask_cors import CORS
from flask_restful_swagger_2 import get_swagger_blueprint

from resources import vnsfs

app = Flask(__name__)
CORS(app)

# A list of swagger document objects
docs = []

# Get user resources
user_resources = vnsfs.get_resources()

# Retrieve and save the swagger document object (do this for each set of resources).
docs.append(user_resources.get_swagger_doc())

# Register the blueprint for user resources
app.register_blueprint(user_resources.blueprint)

# Prepare a.py blueprint to serve the combined list of swagger document objects and register it
app.register_blueprint(get_swagger_blueprint(docs, '/api/swagger', title='Example', api_version='1'))

if __name__ == '__main__':
    # Ensure Flask connections are listened for on all network cards (as loopback is an interface on its own).
    # Docker Rails app fails to be served - curl: (56) Recv failure: Connection reset by peer
    # https://stackoverflow.com/questions/27806631/docker-rails-app-fails-to-be-served-curl-56-recv-failure
    # -connection-reset
    # The answer is applicable to Flask as well.
    app.run(host='0.0.0.0', debug=True)
