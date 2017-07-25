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
Creates the data store for the vNSF & NS Store. This script is intended to run the first time one wants to setup the Store environment and from within the container defined for the data store (which is declared in the variable CNTR_DATASTORE in the .env file and should be something like 'docker exec -it docker_data-store_1 bash' to have a shell open for the proper container).


OPTIONS
  --production          (Optional) Creates the data store.

  --staging             (Optional) Creates the data store for staging purposes.

  --qa                  (Optional) Creates the data store for quality assurance purposes.

  -h, --help           Prints this usage message.

EXAMPLES
  $0 --production

    Creates the data store to hold the vNSF & NS data for the Store.

  $0 --staging

    Creates the stating environment data store to hold the vNSF & NS data for the Store.

  $0 --qa

    Creates the QA environment data store to hold the vNSF & NS data for the Store.

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

p_production=${_PARAM_INVALID_VALUE}
p_staging=${_PARAM_INVALID_VALUE}
p_qa=${_PARAM_INVALID_VALUE}



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

    parseParamsCmd=`getopt -n$0 -o h:: -a --long production,staging,qa -- "$@"`

    if [ $? != 0 ] ; then Usage; echo; echo; exit 1 ; fi

    eval set -- "$parseParamsCmd"

    [ $# -eq 0 ] && Usage

    while [ $# -gt 0 ]
    do

        case "$1" in

            --production)
                p_production=true
                actionSet=1
                shift
                ;;

            --staging)
                p_staging=true
                actionSet=1
                shift
                ;;

            --qa)
                p_qa=true
                actionSet=1
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
                UsageBASE_ENV_FILE
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
# *                M A I N   P R O C E S S I N G   B L O C K
# *
# ******************************************************************************
# ******************************************************************************


#
# Manage input options.
#
HandleOptions "$@"


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


# Do nested variables interpolation as the shell doesn't seem do it.
ENV_FILE=.env.subst
ENV_TMP_FILE=$(mktemp /tmp/XXXXXXX)
echo "#!/bin/sh" > ${ENV_TMP_FILE}
echo ". ${ENV_FILE_FULL}" >> ${ENV_TMP_FILE}
echo "cat <<_VARS_BLOCK_" >> ${ENV_TMP_FILE}
cat ${ENV_FILE_FULL} >> ${ENV_TMP_FILE}
echo "_VARS_BLOCK_" >> ${ENV_TMP_FILE}
echo >> ${ENV_TMP_FILE}
. ${ENV_TMP_FILE} > ${ENV_FILE}


# Setup mongoDB data store.
mongo --port ${DATASTORE_PORT} --eval "var PORT='$DATASTORE_PORT', STORE_COLLECTION='$DATASTORE_DBNAME', STORE_USER='$DATASTORE_USERNAME', STORE_PASS='$DATASTORE_PASSWORD'" ${CNTR_FOLDER_DEV}/docker/mongodb-init.js
