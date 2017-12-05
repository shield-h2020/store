#/bin/sh

#  Copyright (c) 2017 SHIELD, UBIWHERE
# ALL RIGHTS RESERVED.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Neither the name of the SHIELD, UBIWHERE nor the names of its
# contributors may be used to endorse or promote products derived from this
# software without specific prior written permission.
#
# This work has been performed in the framework of the SHIELD project,
# funded by the European Commission under Grant number 700199 through the
# Horizon 2020 program. The authors would like to acknowledge the contributions
# of their colleagues of the SHIELD partner consortium (www.shield-h2020.eu).



# ******************************************************************************
# ******************************************************************************
# *
# *                U S A G E   M E S S A G E
# *
# ******************************************************************************
# ******************************************************************************

Usage()
{
    cat <<USAGE_MSG

USAGE: $0 OPTIONS
Sets up the docker environment for the vNSF & NS Store to run and starts up all the required daemons so the Store is operational. It uses the configurations provided along with the ones defined in the .env.base|.en.base.qa file to deploy the environment.
Environment file only needs to provide the deployment-specific settings as all the others come from the base file.


OPTIONS
   --environment        The file holding all the settings to use for the Store configuration.

   --verbose            (Optional) Whether the containers output is on the screen. The default is to have them run as a daemon. To stop it press ^C.

   --qa                 (Optional) Have the Quality Assurance service running so manual validation can take place.

   --check_build        (Optional) Simply build all the source code and run the defined tests to determine the build status. This ignores any other conflicting options and only does what it states. Mainly used for CI.

   --shutdown           (Optional) Stops all the Store-related running containers.

   -h, --help           Prints this usage message.

EXAMPLES
  $0 --environment .env.production

    Runs the environment with the settings from the '.env.production' file. All containers run as daemons and the shutdown option must be provided later on when wanting to terminate all the Store-related containers.

  $0 --shutdown

    Terminates all the Store running environment and cleans up.

  $0 --environment .env.staging --verbose

    Runs the environment with the settings from the '.env.staging' file. All the containers output is visible so the user can see what is going on.

  $0 --environment .env.staging --verbose --qa

    Same as above but now the QA service is available (through docker container exec command).

  $0 --environment .env.qa --check_build

    Runs the environment with the settings from the '.env.qa' file. All containers run as daemons. A test execution report is produced and stored in the 'test/reports' folder.

USAGE_MSG
}





# ******************************************************************************
# ******************************************************************************
# *
# *                G L O B A L   D A T A
# *
# ******************************************************************************
# ******************************************************************************


_PARAM_INVALID_VALUE="__##_INVALID_VALUE_##__"

p_environment=$_PARAM_INVALID_VALUE
p_qa=$_PARAM_INVALID_VALUE
p_verbose=$_PARAM_INVALID_VALUE
p_check_build=$_PARAM_INVALID_VALUE
p_shutdown=$_PARAM_INVALID_VALUE



# ******************************************************************************
# ******************************************************************************
# *
# *                P A R A M E T E R S   V A L I D A T I O N
# *
# ******************************************************************************
# ******************************************************************************



#******************************************************************************
# Description: Handles a parameter not being set.
#
# Parameters:
#       [IN] - The name of the parameter that is not set.
#
# Returns:     Nothing.
# ******************************************************************************
ErrorParameterNotSet() {
      echo "Parameter not set: $1"
      Usage
      exit 1
}



#******************************************************************************
# Description: Handles a parameter withou invalid value.
#
# Parameters:
#       [IN] - The name of the parameter with invalid values.
#
# Returns:     Nothing.
# ******************************************************************************
ErrorInvalidParameter() {
      echo "Value not allowed for parameter: $1"
      Usage
      exit 1
}



#******************************************************************************
# Description: Processes input options and validates them. On error the program
#              execution terminates.
#
# Parameters:
#       [IN] - Script name.
#       [IN] - Information as per usage message.
#
# Returns:     the position of the last option in the input parameters.
# ******************************************************************************
HandleOptions() {

    parseParamsCmd=`getopt -n$0 -o h:: -a --long environment:,qa,verbose,check_build,shutdown -- "$@"`

    if [ $? != 0 ] ; then Usage; echo; echo; exit 1 ; fi

    eval set -- "$parseParamsCmd"

    [ $# -eq 0 ] && Usage

    actionSet=0

    while [ $# -gt 0 ]
    do
        case "$1" in

            --environment)
                p_environment=$2
                shift
                actionSet=1
                ;;

            --qa)
                p_qa=true
                actionSet=1
                ;;

            --shutdown)
                p_shutdown=true
                actionSet=1
                ;;

            --verbose)
                p_verbose=true
                actionSet=1
                ;;

            --check_build)
                p_check_build=true
                actionSet=1
                ;;

            # Help
            -h)
                Usage
                exit 1
                ;;

            # Housekeeping
             --) # End marker from getopt.
                shift
                break
                ;;

            -*)
                echo "Unknown option $1"
                Usage
                exit 1
                ;;

            *)
                # Any additional parameter is an error.
                echo "Too many parameters provided."
                Usage
                exit 1
                ;;

        esac
        shift
    done

    #
    # Check mandatory parameters.
    #

    if [ $actionSet -eq 0 ] ; then
        echo -e "Missing option(s)\n"
        Usage
        echo -e "\n\n"
        exit 1
    fi

    if ! [[ $p_shutdown = true ]] && ! [[ -f $p_environment ]] ; then
        filepath=$(realpath ${p_environment})
        echo -e "Cannot read environment file: ${filepath}"
        echo -e "Please provide a valid file."
        echo -e "\n\n"
        exit 1
    fi

    return $OPTIND
}



# ******************************************************************************
# ******************************************************************************
# *
# *                F U N C T I O N S
# *
# ******************************************************************************
# ******************************************************************************



#******************************************************************************
# Description: Cleans up after execution.
#
# Parameters:  None.
#
# Returns:     None.
# ******************************************************************************
Cleanup()
{
    rm -f ${ENV_FILE_FULL}
    rm -f ${ENV_TMP_FILE}
    rm -f ${DOCKER_COMPOSE_FILE}
    rm -f ${DOCKER_FILE_STORE}
    rm -f ${DOCKER_FILE_DATASTORE}
    rm -f ${DOCKER_COMPOSE_FILE_QA}
    rm -f ${DOCKER_FILE_QA}
}



#******************************************************************************
# Description: Stops and removes all the Store containers.
#
# Parameters: None.
# Returns:    Nothing.
# ******************************************************************************
Shutdown() {

    # Stop and remove containers.
    containers=($($DOCKER ps -aq --filter label=project\=${CNTR_PROJECT}))
    $DOCKER stop "${containers[@]}"
    $DOCKER rm "${containers[@]}"
}



# ******************************************************************************
# ******************************************************************************
# *
# *                M A I N   P R O C E S S I N G   B L O C K
# *
# ******************************************************************************
# ******************************************************************************


#
# Manage input options.
#
HandleOptions "$@"


###
###
### R A T I O N A L E:
###
### To switch between environments play with the .env* files to set the proper configurations.
### It is assumed that the environment files are built top-down with the most-likely settings to change defined at the
### top of the file. Thus any tailoring to the environment is done on those variables leaving the foundation ones alone.
### As such the foundation environment gets appended to the user-defined one so proper interpolation can take place and
### everything auto-magically works. If this constraint changes this script must be updated accordingly.
###
###



# Based on: Let's Deploy! (Part 1)
# http://lukeswart.net/2016/03/lets-deploy-part-1/

# The environment variables start off with the one from the production environment and get replaced from there.
ENV_FILE_FULL=$(mktemp /tmp/XXXXXXX)

# Load deployment-specific settings.
if ! [ $p_shutdown = true ]; then
    # Shutdown option has no environment set.
    cat ${p_environment} > ${ENV_FILE_FULL}
fi

# Append settings for standard operation.
cat .env.base >> ${ENV_FILE_FULL}

if [[ $p_qa = true ]] || [[ $p_check_build = true ]]; then
    # Override with settings from QA.
    cat .env.base.qa >> ${ENV_FILE_FULL}
fi

. ${ENV_FILE_FULL}



# Export variables so they can be used here. Stop script at first error.
set -ae

SHARED_FOLDER_DEV=${PWD}/../

# Do nested variables interpolation as the shell doesn't seem do it.
ENV_FILE=$(mktemp)
ENV_TMP_FILE=$(mktemp)
echo "#!/bin/sh" > ${ENV_TMP_FILE}
echo ". ${ENV_FILE_FULL}" >> ${ENV_TMP_FILE}
echo "cat <<_VARS_BLOCK_" >> ${ENV_TMP_FILE}
cat ${ENV_FILE_FULL} >> ${ENV_TMP_FILE}
echo "_VARS_BLOCK_" >> ${ENV_TMP_FILE}
echo >> ${ENV_TMP_FILE}
. ${ENV_TMP_FILE} > ${ENV_FILE}



# Tools.
DOCKER=$(command -v docker || { echo "Error: No docker found." >&2; Cleanup; exit 1; })
DOCKER_COMPOSE=$(command -v docker-compose || { echo "Error: No docker-compose found." >&2; Cleanup; exit 1; })


if [ $p_shutdown = true ]; then
    Shutdown
    exit 0
fi


# Remove the template extension from files.
DOCKER_COMPOSE_FILE="${DOCKER_COMPOSE_FILE_TEMPLATE%.*}"
DOCKER_FILE_STORE="${DOCKER_FILE_TEMPLATE_STORE%.*}"
DOCKER_FILE_DATASTORE="${DOCKER_FILE_TEMPLATE_DATASTORE%.*}"

# Replace variables
envsubst < ${DOCKER_COMPOSE_FILE_TEMPLATE} > ${DOCKER_COMPOSE_FILE}
envsubst < ${DOCKER_FILE_TEMPLATE_STORE} > ${DOCKER_FILE_STORE}
envsubst < ${DOCKER_FILE_TEMPLATE_DATASTORE} > ${DOCKER_FILE_DATASTORE}


COMPOSE_FILES="-f ${DOCKER_COMPOSE_FILE}"

if [[ $p_qa = true ]] || [[ $p_check_build = true ]]; then
    # Setup QA environment.
    DOCKER_COMPOSE_FILE_QA="${DOCKER_COMPOSE_FILE_QA_TEMPLATE%.*}"
    DOCKER_FILE_QA="${DOCKER_FILE_TEMPLATE_QA%.*}"
    envsubst < ${DOCKER_COMPOSE_FILE_QA_TEMPLATE} > ${DOCKER_COMPOSE_FILE_QA}
    envsubst < ${DOCKER_FILE_TEMPLATE_QA} > ${DOCKER_FILE_QA}
    COMPOSE_FILES="-${COMPOSE_FILES} -f ${DOCKER_COMPOSE_FILE_QA}"
fi

# Set containers prefix.
COMPOSE_PROJECT_NAME=${PROJECT}

# Create services.
${DOCKER_COMPOSE} ${COMPOSE_FILES} build --force-rm

if [[ $p_check_build = true ]] || ! [[ $p_verbose = true ]]; then
    # Run containers as daemons.
    COMPOSE_FLAGS=-d
fi

# Loadup containers.
${DOCKER_COMPOSE} ${COMPOSE_FILES} up ${COMPOSE_FLAGS}

if [ $p_check_build = true ]; then
    # Have the QA container setup the data store and run the tests.
    echo "Waiting for the containers to be ready..." && sleep 10
    ${DOCKER} container exec docker_${DATASTORE_HOST}_1 bash -c "${CNTR_FOLDER_DEV}/docker/setup-datastore.sh --environment ${p_environment} --qa"
    ${DOCKER} container exec docker_${CNTR_QA}_1 ${FOLDER_TESTS_BASEPATH}/run.sh

    HOST_FOLDER_DEV=$(cd "${SHARED_FOLDER_DEV}"; pwd)
    REPORT_PATH="${FOLDER_TESTS_REPORT/$CNTR_FOLDER_DEV/$HOST_FOLDER_DEV}"
    echo ===
    echo === Tests report is at $REPORT_PATH
    echo ===
fi

Cleanup

echo -e "\n\n"
