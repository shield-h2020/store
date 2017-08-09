#!/bin/sh

CURRENT_PATH=${PWD}

TESTS_REPORT_JSON=${FOLDER_TESTS_REPORT}/result.json
TESTS_REPORT_HTML=${FOLDER_TESTS_REPORT}/report.html
REPORT_TOOL=${FOLDER_TESTS_TOOLS}/html_report.js

cd ${FOLDER_TESTS_FEATURES}

# Run tests.
radish --cucumber-json ${TESTS_REPORT_JSON} .

# Beautify tests report.
node ${REPORT_TOOL} -s ${TESTS_REPORT_JSON} -o ${TESTS_REPORT_HTML}

cd ${CURRENT_PATH}
