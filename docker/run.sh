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
   -h                   Prints this usage message.

  --dev_folder          (Required) /path/to/the/store/development/folder

EXAMPLES
  $0 --dev_folder /path/to/the/store/development/folder

    Used by the setup script as the source path for some files it uses during the docker build and containers instantiation. It also makes available the development folder inside the Store containers so a developer can make any changes or improvements to the Store (through docker exec).

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

#p_dev_folder=$_PARAM_INVALID_VALUE



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

    parseParamsCmd=`getopt -n$0 -o h:: -a --long dev_folder: -- "$@"`

    if [ $? != 0 ] ; then Usage; echo; echo; exit 1 ; fi

    eval set -- "$parseParamsCmd"

    [ $# -eq 0 ] && Usage

    while [ $# -gt 0 ]
    do

        case "$1" in

            --dev_folder)
                p_dev_folder=$2
                shift
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

    # if [ "$p_dev_folder" = "$_PARAM_INVALID_VALUE" ]; then
    #   ErrorParameterNotSet "dev_folder"
    # fi

    return $OPTIND
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


# Based on: Let's Deploy! (Part 1)
# http://lukeswart.net/2016/03/lets-deploy-part-1/



# Export variables so they can be used here. Stop script at first error.
set -ae

SHARED_FOLDER_DEV=${PWD}/../

. .env

# Do nested variables interpolation as the shell doesn't seem do it.
ENV_FILE=.env.subst
ENV_TMP_FILE=`mktemp /tmp/XXXXXXX`
echo "cat <<VARS_BLOCK" > ${ENV_TMP_FILE}
cat .env >> ${ENV_TMP_FILE}
echo -e "\nVARS_BLOCK" >> ${ENV_TMP_FILE}
. ${ENV_TMP_FILE} > ${ENV_FILE}


# Tools.
DOCKER=$(command -v docker || { echo "Error: No docker found." >&2; exit 1; })
DOCKER_COMPOSE=$(command -v docker-compose || { echo "Error: No docker-compose found." >&2; exit 1; })

# Remove the template extension from files.
DOCKER_COMPOSE_FILE="${DOCKER_COMPOSE_FILE_TEMPLATE%.*}"
DOCKER_FILE_DEV="${DOCKER_FILE_TEMPLATE_DEV%.*}"
DOCKER_FILE_DATASTORE="${DOCKER_FILE_TEMPLATE_DATASTORE%.*}"
DOCKER_FILE_QA="${DOCKER_FILE_TEMPLATE_QA%.*}"

# Replace variables
envsubst < $DOCKER_COMPOSE_FILE_TEMPLATE > $DOCKER_COMPOSE_FILE
envsubst < $DOCKER_FILE_TEMPLATE_DEV > $DOCKER_FILE_DEV
envsubst < $DOCKER_FILE_TEMPLATE_DATASTORE > $DOCKER_FILE_DATASTORE
envsubst < $DOCKER_FILE_TEMPLATE_QA > $DOCKER_FILE_QA


# Set containers prefix.
COMPOSE_PROJECT_NAME=$PROJECT

# Create services.
$DOCKER_COMPOSE build --force-rm

# Loadup containers.
$DOCKER_COMPOSE up

echo
echo
