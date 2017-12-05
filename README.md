# vNSF & NS Store

SHIELD aims to set up a single, centralised digital store for virtual Network Security Functions (vNSFs) and Network Services (NSs). This approach allows Service Providers to offer new security features for protecting the network or extend already existing functionalities without the need of modifying core elements of the framework. The store acts as a repository for vNSFs and NSs that have been previously published.

The Store onboards vNSFs/NSs in a secure and trusted way. The onboarding process will ensure the provenance is from a trusted source and that the contents integrity can be assured. Once this is achieved the security information is stored for safekeeping and provided upon request so other components can check that the vNSF/NS has not been tampered with since it was onboarded.

The onboarding process also verifies the vNSF and NS associated descriptors to ensure the instantiation process by an Orchestrator is performed without hassle. This encompasses the check of all the descriptors for inconsistencies and validation of the network topology defined within them to prevent issues such as unwanted loops in the forwarding graphs or reference to undefined networks or missing ports.

# Installation

## Prerequisites

* [Python 3](https://www.python.org/)
* [Eve REST API framework](http://eve.readthedocs.io/en/stable/) which provides (amongst other goodies) [Flask](http://flask.pocoo.org/) for RESTful support, [Cerberus](http://python-cerberus.org/) for JSON validation and [MongoDB](https://www.mongodb.com/) for the actual vNSF & NS data store.
* [PyYAML](http://pyyaml.org/) to handle vNSF and NS descriptors

## Python virtual environment

The [environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/) requirements are defined in the [requirements-store.txt](docker/requirements-store.txt) file.

## Docker

### Prerequisites

Install the following packages and versions following the manuals:

* [Docker](https://docs.docker.com/engine/installation/) (17.06.0+)
* [docker-compose](https://docs.docker.com/compose/install/) (3.0+)

Alternatively, install them through the steps below:

```bash
sudo apt-get install --no-install-recommends apt-transport-https curl software-properties-common python-pip
curl -fsSL 'https://sks-keyservers.net/pks/lookup?op=get&search=0xee6d536cf7dc86e2d7d56f59a178ac6c6238f52e' | sudo apt-key add -
sudo add-apt-repository "deb https://packages.docker.com/1.13/apt/repo/ubuntu-$(lsb_release -cs) main"
sudo apt-get update
sudo apt-get -y install docker-engine
sudo pip install docker-compose
```

Finally, add current user to the docker group (allows issuing Docker commands w/o sudo):
```
sudo usermod -G docker $(whoami)
```

### Setup

Automation details can be found in the [DevOps](#devops) section.

TL;DR

* Run it with:

```bash
cd docker
./run.sh --environment .env.production --verbose
```

Once everything is up and running the last lines on the screen should be something like:
```bash
Creating docker_data-store_1
Creating docker_dev_1 ... done

store_1         |  * Running on http://0.0.0.0:6060/ (Press CTRL+C to quit)
store_1         |  * Restarting with stat
store_1         |  * Debugger is active!
store_1         |  * Debugger pin code: <XXX-XXX-XXX>
```

* First-time setup (from another terminal window):

```bash
docker exec docker_store-persistence_1 bash -c "/usr/share/dev/store/docker/setup-datastore.sh --environment /usr/share/dev/store/docker/.env.production"


```

After the first-time setup is finished, you should see that Mongo has been successfully installed.

At this point, two containers should be running; namely the store and the mongo database:

```bash
$ docker ps
CONTAINER ID        IMAGE                             NAMES
420133c8e114        docker_store                      docker_store_1
bea2622e00d3        docker_store-persistence          docker_store-persistence_1
```

Troubleshooting is possible after accessing the container through its name (last column from above): `docker exec -it $docker_container_name bash`

### Teardown

To stop the docker environment and teardown everything simply (_in the docker folder_):

```bash
./run.sh --shutdown
```

### First-time setup

The first time the Store environment is set up one must create the data store to hold the vNSF & NS data for the Store. This is done by the [setup-datastore.sh](docker/setup-datastore.sh) script and the steps required are mentioned above.

# Deployment

The default settings deploy the Store API in the localhost and running on port 6060. To ensure the environment is up and running place a `GET` request to http://localhost:6060. The response should be a `200 OK` with the available endpoints presented in either XML:

```xml
<resource>
    <link rel="child" href="vnsfs/attestation" title="vnsfs/attestation"/>
    <link rel="child" href="vnsfs" title="vnsfs"/>
</resource>
```

or JSON format if the `Accept: application/json` HTTP header is set:

```json
{
    "_links": {
        "child": [{
                "href": "vnsfs",
                "title": "vnsfs"
            },
            {
                "href": "vnsfs/attestation",
                "title": "vnsfs/attestation"
            }
        ],
    }
}
```

# API Documentation

The API to interact with the recommendations follows the RESTful principles and serves for CRUD operations on the recommendations.

The [API documentation](http://petstore.swagger.io/?url=https://raw.githubusercontent.com/shield-h2020/store/master/swagger.json) follows the [OpenAPI Specification](https://swagger.io/specification/) (fka Swagger RESTful API Documentation Specification) Version 2.0 and is defined in the [swagger.json](swagger.json) file.

# Packaging

## vNSF Packaging

Please head to [vNSF Packaging](docs/vnsf/packaging.md) to understand how to package a vNSF for submission to the Store.

## Network Service Packaging

[Network Service packaging](docs/ns/packaging.md) details how to package a Network Service for submission to the Store.

# Testing

Please read the [Quality Assurance](docs/qa.md) section to grasp how the Store features are validated.

# DevOps

For deployment setup, environments definition and build automation details please  refer to [DevOps](docs/devops.md).

# Further reading

Please refer to the [Store documentation](docs/index.md) for additional insight on how the Store operates and what lies behind the scenes.
