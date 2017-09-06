# DevOps

To have a pain-free installation a [docker environment](../https://www.docker.com/) is provided. This uses a [docker-compose](../https://docs.docker.com/compose/overview/) file to provide the orchestration for the containers to setup.

Going a step further on easing up the installation process [environment variables](../https://docs.docker.com/compose/environment-variables/#setting-environment-variables-with-docker-compose-run) are defined in the [`.env`](../../docker/.env) file. Any specific tailoring for the Store environment instantiation should be done here.

The downside of all this auto-magically environment instantiation is that the actual docker files get a bit harder to read and a [setup orchestrator script](../docker/run.sh) needs to be put in place to fill in the proper data in the docker files according to the variables defined in the [`.env`](../docker/.env) file. The outcome of all of this tweaking is that the docker files are created as templates ([`docker-compose.yml.tmpl`](../docker/docker-compose.yml.tmpl), [`docker-compose.qa.yml.tmpl`](../docker/docker-compose.qa.yml.tmpl), [`Dockerfile.dev.tmpl`](../docker/Dockerfile.dev.tmpl),  [`Dockerfile.datastore.tmpl`](../docker/Dockerfile.datastore.tmpl), [`Dockerfile.qa.tmpl`](../docker/Dockerfile.qa.tmpl)) and the orchestrator script ([`run.sh`](../docker/run.sh)) produces the proper docker files, builds them up and runs the containers so the Store is up and running.

## Environments

In order to allow for testing without disrupting the Store operation, ensure new features won't introduce regressions, a new deployment is properly set up or even prevent any downtime during misbehaviour analysis environments are introduced. The purpose behind such environments is to separate concerns and provide for the flexibility mentioned.

Each environment settings are defined in a configuration file. The rationale behind these files is to have a base file ([`.env`](../docker/.env)) with the settings required for normal operation (known as production) and have additional environment-specific files which redefine values for the normal operation variables or defining additional ones used only for the intended purposes. All this is described in the table below.


Environment | Purpose | `run.sh` Flag | Settings
-|-|-
Production | Put into operation for the intended use | `--production` | [`.env`](../docker/.env)
Staging | Replicates (as closely as possible) the production environment so a "test-drive" can be done and potential issues uncovered. Also be used for development purposes to have a better understanding of what is happening | `--staging` | [`.env.staging`](../docker/.env.staging)
QA | Quality Assurance settings used to verify no regressions were introduced by new features being deployed | `--qa` | [`.env.qa`](../docker/.env.qa)

## Automation

The tools below are used to provide all the environments auto-magically instantiation.

### Scripts

* [`run.sh`](../docker/run.sh) is the Store environment instantiation orchestrator. It builds the docker files according to the environment to instantiate based on the defined [templates](../#docker-templates)

* [`setup-dev.sh`](../docker/setup-dev.sh) ensures the Store requirements are installed on the container so the code can run and performa as expected

*  [`setup-datastore.sh`](../docker/setup-datastore.sh) ensures the Store data store is up and running according to the settings defined in the environment files

* [`setup-qa.sh`](../docker/setup-qa.sh) takes care of setting up the requirements for the quality assurance environment so the validation runs against the Store code

* [`mongodb-init.js`](../docker/mongodb-init.js) initializes the data store for the environment being used


### (Docker) Templates

* [`docker-compose.yml.tmpl`](../docker/docker-compose.yml.tmpl) defines the services to run for the Store container
* [`docker-compose.qa.yml.tmpl`](../docker/docker-compose.qa.yml.tmpl) defines the services to run for the QA container
* [`Dockerfile.dev.tmpl`](../docker/Dockerfile.dev.tmpl) packages installation to setup the Store container
* [`Dockerfile.datastore.tmpl`](../docker/Dockerfile.datastore.tmpl) packages installation to setup the data store container
* [`Dockerfile.qa.tmpl`](../docker/Dockerfile.qa.tmpl) packages installation to setup the QA container


### Requirements

* [`requirements-store.txt`](../docker/requirements-store.txt) defines the libraries required for the Store code
* [`requirements-qa.txt`](../docker/requirements-qa.txt) defines the libraries required for the BDD testing environment
