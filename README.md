# vNSF & NS Store

SHIELD aims to set up a single, centralised digital store for virtual Network Security Functions (vNSFs) and Network Services (NSs). This approach allows Service Providers to offer new security features for protecting the network or extend already existing functionalities without the need of modifying core elements of the framework. The store acts as a repository for vNSFs and NSs that have been previously published.

The Store onboards vNSFs/NSs in a secure and trusted way. The onboarding process will ensure the provenance is from a trusted source and that the contents integrity can be assured. Once this is achieved the security information is stored for safekeeping and provided upon request so other components can check that the vNSF/NS has not been tampered with since it was onboarded.

The onboarding process also verifies the vNSF and NS associated descriptors to ensure the instantiation process by an Orchestrator is performed without hassle. This encompasses the check of all the descriptors for inconsistencies and validation of the network topology defined within them to prevent issues such as unwanted loops in the forwarding graphs or reference to undefined networks or missing ports.


# Installation


## Prerequisites

* [Python 3](https://www.python.org/)
* [Eve REST API framework](http://eve.readthedocs.io/en/stable/) which provides (amongst other goodies) [Flask](http://flask.pocoo.org/) for RESTful support, [Cerberus](http://python-cerberus.org/) for JSON validation and [MongoDB](https://www.mongodb.com/) for the actual vNSF data store.
* [PyYAML](http://pyyaml.org/) to handle vNSF and NS descriptors


## Python virtual environment

The [environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/) requirements are defined in the [requirements.txt](docker/store-requirements.txt) file.


## Docker

TL;DR

* Run it with:
```
$ cd docker
$ docker build --force-rm -t shield-store .
```

    * First-time setup:

    ```
    $ docker exec -it docker_data-store_1 bash
    ```
    Now inside the container:
    ```
    root@<container_id>:/usr/share/dev/store/docker# ./setup-datastore.sh --please
    ```



To have a [pain-free installation](https://www.docker.com/) a docker environment is provided. This uses a [docker-compose](https://docs.docker.com/compose/overview/) file to provide the orchestration for the containers to setup.

Going a step further on easing up the installation process [environment variables](https://docs.docker.com/compose/environment-variables/#setting-environment-variables-with-docker-compose-run) are defined in the [.env](docker/.env) file. Any specific tailoring for the Store environment instantiation should be done here.

The downside of all this auto-magically environment instantiation is that the actual docker files get a bit harder to read and a [setup orchestrator script](docker/run.sh) needs to be put in place to fill in the proper data in the docker files according to the variables defined in the [.env](docker/.env) file. The outcome of all of this tweaking is that the docker files are created as templates ([docker-compose.yml.tmpl](docker/docker-compose.yml.tmpl), [Dockerfile.datastore.tmpl](docker/Dockerfile.datastore.tmpl), [Dockerfile.dev.tmpl](docker/Dockerfile.dev.tmpl)) and the orchestrator script ([run.sh](docker/run.sh)) produces the proper docker files, builds them up and runs the containers so the Store is up and running.

### First time run

The first time the Store environment is set up one must create the data store to hold the vNSF & NS data for the Store. This is done by the [setup-datastore.sh](docker/setup-datastore.sh) script and the steps required are mentioned above.

# API Documentation

The documentation follows the [OpenAPI Specification](https://swagger.io/specification/) (fka Swagger RESTful API Documentation Specification) Version 2.0 and is defined in the [swagger.yaml](swagger.yaml) file. To have it in a user-friendly way simple paste its contents into the [Swagger Editor](https://editor.swagger.io/).


# Packaging

## vNSF Packaging

Please head to [vNSF Packaging](docs/vnsf/packaging.md).
