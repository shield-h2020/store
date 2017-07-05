# vNSF & NS Store

SHIELD aims to set up a single, centralised digital store for virtual Network Security Functions (vNSFs) and Network Services (NSs). This approach allows Service Providers to offer new security features for protecting the network or extend already existing functionalities without the need of modifying core elements of the framework. The store acts as a repository for vNSFs and NSs that have been previously published.

The Store onboards vNSFs/NSs in a secure and trusted way. The onboarding process will ensure the provenance is from a trusted source and that the contents integrity can be assured. Once this is achieved the security information is stored for safekeeping and provided upon request so other components can check that the vNSF/NS has not been tampered with since it was onboarded.

The onboarding process also verifies the vNSF and NS associated descriptors to ensure the instantiation process by an Orchestrator is performed without hassle. This encompasses the check of all the descriptors for inconsistencies and validation of the network topology defined within them to prevent issues such as unwanted loops in the forwarding graphs or reference to undefined networks or missing ports.


# Installation


## Prerequisites

* [Python 3](https://www.python.org/)
* [Eve REST API framework](http://python-eve.org/) which provides (amongst other goodies) [Flask](http://flask.pocoo.org/) for RESTful support, [Cerberus](http://python-cerberus.org/) for JSON validation and [MongoDB](https://www.mongodb.com/) for the actual vNSF data store.
* [PyYAML](http://pyyaml.org/) to handle vNSF and NS descriptors


## Python virtual environment

The [environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/) requirements are defined in the `requirements.txt` file.


## Docker

To have a [pain-free installation](https://www.docker.com/) the `Dockerfile` is provided. It ensures all dependencies are met and sets up the proper [Python virtual environment](#python-virtual-environment).

* Build it with:

    ```
    $ cd docker
    $ docker build --force-rm -t shield-store .
    ```
* Run it with:

    `$ docker run -it -p 5000:5000 -v /path/to/local:/path/to/container shield-store CMD`
