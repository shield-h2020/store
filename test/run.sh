#!/bin/sh

CURRENT_PATH=${PWD}

START_PATH=${FOLDER_TESTS_BASEPATH}/features
TESTS_REPORT_JSON=${FOLDER_TESTS_BASEPATH}/features/result.json
TESTS_REPORT_HTML=${FOLDER_TESTS_BASEPATH}/reports/report.html
REPORT_TOOL=${FOLDER_TESTS_BASEPATH}/tools/html_report.js

cd ${START_PATH}

radish --cucumber-json ${TESTS_REPORT_JSON} .

node ${REPORT_TOOL} -s ${TESTS_REPORT_JSON} -o ${TESTS_REPORT_HTML}

cd ${CURRENT_PATH}
