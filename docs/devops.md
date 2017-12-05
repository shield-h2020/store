# DevOps

To have a pain-free installation a [docker environment](../https://www.docker.com/) is provided. This uses a [docker-compose](../https://docs.docker.com/compose/overview/) file to provide the orchestration for the containers to setup.

Going a step further on easing up the deployment process [environment variables](../https://docs.docker.com/compose/environment-variables/#setting-environment-variables-with-docker-compose-run) are used. These are split in deployment-specific and foundation settings. Any tailoring to the Store instantiation is done to the deployment-specific settings.

The downside of all this auto-magically environment instantiation is that the actual docker files get a bit harder to read and a [setup orchestrator script](../docker/run.sh) needs to be put in place to fill in the proper data in the docker files according to the variables defined for the environment. The outcome of all of this tweaking is that the docker files are created as templates ([`docker-compose.yml.tmpl`](../docker/docker-compose.yml.tmpl), [`docker-compose.qa.yml.tmpl`](../docker/docker-compose.qa.yml.tmpl), [`Dockerfile.store.tmpl`](../docker/Dockerfile.store.tmpl),  [`Dockerfile.datastore.tmpl`](../docker/Dockerfile.datastore.tmpl), [`Dockerfile.qa.tmpl`](../docker/Dockerfile.qa.tmpl)) and the orchestrator script ([`run.sh`](../docker/run.sh)) produces the proper docker files, builds them up and runs the containers so the Store is up and running as intended.


## Environments

In order to allow for testing without disrupting the Store operation, ensure new features won't introduce regressions, a new deployment is properly set up or even prevent any downtime during misbehaviour analysis environments are introduced. The purpose behind such environments is to separate concerns and provide for the flexibility mentioned.

Any tailoring to the Store deployment is done through the variables below. These variables are defines in a file and provided to the [setup orchestrator script](../docker/run.sh) as a parameter (further details available on the help message for the script).

Variable | Purpose | Format
-|-|-
`API_PORT` | TCP port where the Store REST API is running. | Number. User or Dynamic Port number as defined by [RFC 6335](https://tools.ietf.org/html/rfc6335)
`VNSFO_PROTOCOL` | Protocol used to communicate with the vNSF Orchestrator | String. `http` or `https`
`VNSFO_HOST` | vNSF Orchestrator IP address | String. IP or DNS name where the vNSFO is running
`VNSFO_PORT` | vNSF Orchestrator IP port | Number. Port number where the vNSFO REST API is listening for requests
`VNSFO_API` | vNSF Orchestrator API basepath | String. Basepath to the vNSFO onboarding REST API

For your convenience some environments are already defined. These are:

Environment | File | Purpose
-|-|-
Production | [`.env.production`](../docker/.env.production) | Put into operation for the intended use
Staging | [`.env.staging`](../docker/.env.staging) | Replicates (as closely as possible) the production environment so a "test-drive" can be done and potential issues uncovered. Also be used for development purposes to have a better understanding of what is happening
QA | [`.env.qa`](../docker/.env.qa) | Quality Assurance settings used to verify no regressions were introduced by new features being deployed. This provides a mock for the vNSF Orchestrator API.


## Automation

The tools below are used to provide all the environments auto-magically instantiation.

### Scripts

* [`run.sh`](../docker/run.sh) is the Store environment instantiation orchestrator. It builds the docker files according to the environment to instantiate based on the defined [templates](../#docker-templates)

* [`setup-store.sh`](../docker/setup-store.sh) ensures the Store requirements are installed on the container so the code can run and performa as expected

*  [`setup-datastore.sh`](../docker/setup-datastore.sh) ensures the Store data store is up and running according to the settings defined in the environment files

* [`setup-qa.sh`](../docker/setup-qa.sh) takes care of setting up the requirements for the quality assurance environment so the validation runs against the Store code

* [`mongodb-init.js`](../docker/mongodb-init.js) initializes the data store for the environment being used


### (Docker) Templates

* [`docker-compose.yml.tmpl`](../docker/docker-compose.yml.tmpl) defines the services to run for the Store container
* [`docker-compose.qa.yml.tmpl`](../docker/docker-compose.qa.yml.tmpl) defines the services to run for the QA container
* [`Dockerfile.store.tmpl`](../docker/Dockerfile.store.tmpl) packages installation to setup the Store container
* [`Dockerfile.datastore.tmpl`](../docker/Dockerfile.datastore.tmpl) packages installation to setup the data store container
* [`Dockerfile.qa.tmpl`](../docker/Dockerfile.qa.tmpl) packages installation to setup the QA container


### Requirements

* [`requirements-store.txt`](../docker/requirements-store.txt) defines the libraries required for the Store code
* [`requirements-qa.txt`](../docker/requirements-qa.txt) defines the libraries required for the [BDD testing environment](./qa.md)
