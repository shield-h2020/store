#/bin/sh


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
Sets up the docker environment for the vNSF & NS Store to run and starts up all the required daemons so the Store is operational. It uses the configurations defined in the .env file to deploy the environment.


OPTIONS
   --production         (Optional) Instantiate the running environment for the Store. This starts up all the containers in the background (like a daemon) and returns to the command line. To stop everything use the 'shutdown' option.

   --staging            (Optional) Does not run the containers in background so the output from the containers is visible. To stop it press ^C.

   --qa                 (Optional) Whether the tests are to be run.

   --shutdown           (Optional) Stops all the Store-related running containers.

   -h, --help           Prints this usage message.

EXAMPLES
  $0 --production

    Runs the production environment. All containers run in the background and the shutdown option must be provided later on when wanting to terminate all the Store-related containers.

  $0 --shutdown

    Terminates all the Store running environment and cleans up.

  $0 --staging

    Runs the staging environment where the containers output is visible so the user can see what is going on.

  $0 --qa

    Runs the QA environment and produces a report with the test execution status. The report is at the 'test/reports' folder.

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

p_production=$_PARAM_INVALID_VALUE
p_staging=$_PARAM_INVALID_VALUE
p_shutdown=$_PARAM_INVALID_VALUE
p_qa=$_PARAM_INVALID_VALUE



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

    parseParamsCmd=`getopt -n$0 -o h:: -a --long production,staging,shutdown,qa -- "$@"`

    if [ $? != 0 ] ; then Usage; echo; echo; exit 1 ; fi

    eval set -- "$parseParamsCmd"

    [ $# -eq 0 ] && Usage

    actionSet=0

    while [ $# -gt 0 ]
    do

        case "$1" in

            --production)
                p_production=true
                shift
                actionSet=1
                ;;

            --shutdown)
                p_shutdown=true
                shift
                actionSet=1
                ;;

            --staging)
                p_staging=true
                shift
                actionSet=1
                ;;

            --qa)
                p_qa=true
                shift
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
    rm -f ${DOCKER_FILE_DEV}
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
###
###



# Based on: Let's Deploy! (Part 1)
# http://lukeswart.net/2016/03/lets-deploy-part-1/

# The environment variables start off with the one from the production environment and get replaced from there.
ENV_FILE_FULL=$(mktemp /tmp/XXXXXXX)
cat .env > ${ENV_FILE_FULL}

if [ $p_staging = true ]; then
    # Load changes for Staging.
    cat .env.staging >> ${ENV_FILE_FULL}
fi

if [ $p_qa = true ]; then
    # Load changes for QA.
    cat .env.qa >> ${ENV_FILE_FULL}
fi

. ${ENV_FILE_FULL}



# Export variables so they can be used here. Stop script at first error.
set -ae

SHARED_FOLDER_DEV=${PWD}/../

# Do nested variables interpolation as the shell doesn't seem do it.
ENV_FILE=$(mktemp /tmp/XXXXXXX)
ENV_TMP_FILE=$(mktemp /tmp/XXXXXXX)
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
DOCKER_FILE_DEV="${DOCKER_FILE_TEMPLATE_DEV%.*}"
DOCKER_FILE_DATASTORE="${DOCKER_FILE_TEMPLATE_DATASTORE%.*}"

# Replace variables
envsubst < ${DOCKER_COMPOSE_FILE_TEMPLATE} > ${DOCKER_COMPOSE_FILE}
envsubst < ${DOCKER_FILE_TEMPLATE_DEV} > ${DOCKER_FILE_DEV}
envsubst < ${DOCKER_FILE_TEMPLATE_DATASTORE} > ${DOCKER_FILE_DATASTORE}


COMPOSE_FILES="-f ${DOCKER_COMPOSE_FILE}"

if [ $p_qa = true ]; then
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

# if ! [ $p_staging = true ]; then
#     COMPOSE_FLAGS=-d
# fi

# Loadup containers.
${DOCKER_COMPOSE} ${COMPOSE_FILES} up ${COMPOSE_FLAGS}

if [ $p_qa = true ]; then
    # Have the QA container setup the data store and run the tests.
    echo "Waiting for the containers to be ready" && sleep 10
    ${DOCKER} container exec docker_${DATASTORE_HOST}_1 bash -c "${CNTR_FOLDER_DEV}/docker/setup-datastore.sh --qa"
    ${DOCKER} container exec docker_${CNTR_QA}_1 ${FOLDER_TESTS_BASEPATH}/run.sh
    echo ===
    echo === Tests report is at ${FOLDER_TESTS_REPORT}
    echo ===
fi

Cleanup

echo -e "\n\n"
