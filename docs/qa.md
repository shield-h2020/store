
# Quality Assurance

A [Behaviour Driven Development (BDD)](https://www.agilealliance.org/glossary/bdd/) methodology was introduced for testing the Store. The option for this methodology ensures meeting the goals of (i) validating the Store behaviour from an API consumer's perspective and (ii) serve as documentation for describing the features available and the intended operational scenarios.

# Prerequisites

* [Python 3](https://www.python.org/)
* [radish](https://github.com/radish-bdd/radish) Behavior Driven Development tool for Python
* [Requests](http://docs.python-requests.org/en/master/) for HTTP requests and responses
* [dictdiffer](https://pypi.python.org/pypi/dictdiffer) to compare expected versus actual JSON responses
* [NodeJS](https://nodejs.org) for the modules:
    * [canned](https://www.npmjs.com/package/canned) to mock the vNSF Orchestrator API
    * [cucumber-html-reporter](https://www.npmjs.com/package/cucumber-html-reporter) to beautify test reports
    * [argv](https://www.npmjs.com/package/argv) for command line argument parsing


## Python virtual environment

The [environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/) requirements are defined in the [`docker/requirements-qa.txt`](../docker/requirements-qa.txt) file.

# Run

To run the Quality Assurance (QA) environment from a [teardown](../README.md#teardown) starting point:

```bash
cd docker
./run.sh --qa
```

Once the testing finishes a report is generated and the final output presents the location where the report can be found. This signals the end of the testing operation and is as follows:

```bash
===
=== Tests report is at /usr/share/dev/store/test/reports
===
```

To view a beautified version of the report please open the `/usr/share/dev/store/test/reports/report.html` file.

# Framework

As for the BDD methodology features (or specifications) for what the Store should provide are defined along with scenarios ("tests") of applicability. All this is defined using [Gherkin notation](https://github.com/cucumber/cucumber/wiki/Gherkin) and [radish](https://github.com/radish-bdd/radish) as the BDD support tool.

The QA base folder is located at [`test`](../test).

## Features

[Features](https://github.com/cucumber/cucumber/wiki/Feature-Introduction) are described in `*.features` files and can be found in the [`features`](../test/features) folder.

## Steps

[Steps](https://github.com/cucumber/cucumber/wiki/Given-When-Then) are reusable portions used in scenarios. Its behaviour is  defined in the `steps*.py` Python files under the [`features/radish`](../test/features/radish) folder.

## Validation

Any validation requires a controlled and known environment. For this input data and expected output is paramount to determine whether abnormal behaviour is present and pinpoint any detours.

The input data is stored in the [`resources/input-data`](../test/resources/input-data) folder and takes the form best suited for the operation in question, be it a data file or a compressed file.

The expected output is stored in the [`resources/expected-output`](../test/resources/expected-output) folder and takes the form of a JSON file which mimics the Store response to an HTPP request done through its API. This file may be an exact match of the expected response or only the bits that won't change over time. This is defined as [discarding output](#discarding-output).

### Discarding output

In order to identify any detour from the expected behaviour an exact match between actual and expected output must be carried out. Sometimes this purpose is defeated by the ever-changing nature of some response elements (like identifiers and dates for instance) which will take on a different value every time a scenario runs.

To cope with such requirement the JSON file with the expected response contents uses a special notation to state what is to be ignored and what must be matched. Anything else present in the response and not stated in this notation shall render the validation failed and thus the scenario unsuccessful.

An example of the JSON notation to use when wanting to discard some output from the Store API is presented next.

```json
{
  "ignore": [
    "_etag",
    "_updated",
    "_id",
    "_created",
    "_links"
  ],
  "expected": {
    "_status": "OK"
  }
}
```

## Orchestrator

The entire QA set is commanded by the [`test/run.sh`](../test/run.sh) script. This takes care of validating all the features and provide a beautified HTML report of the execution. This report lives at `/usr/share/dev/store/test/reports/report.html`.


# Interactive Execution

When wanting to run a subset of features or scenarios one can open a shell to the QA container and run only the intended ones. This is accomplished by simply open a shell with the QA container and run the desired set. To open a shell do:

```bash
docker container exec -it docker_qa_1 bash
cd ${FOLDER_TESTS_FEATURES}
```

From this point on one can [select what to run](#selection) and [produce a beautified report](#reports) of the run.


## Selection

It is possible to run only a specific set of features or scenarios from the entire selection available. This is done through:

* running a specific features file

        radish --cucumber-json </path/to/report/output.json> health-checks.feature

* identify the group(s) to run by its [tag(s)](http://radish.readthedocs.io/en/latest/tutorial.html#tags)

        radish --cucumber-json </path/to/report/output.json> --tags 'health-check or smoke' .

### Groups

To cater for different purposes of validation the scenarios are [tagged](http://radish.readthedocs.io/en/latest/tutorial.html#tags) with one or more  markers to state to which group(s) it belongs to. The [selection](#selection) is done through stating which group(s) to run. The available groups are presented next.

|Group|Purpose|
|-|-|
| health-check | Ensures the QA environment is properly set up and ready to perform the intended validations.
| smoke | Performs a rapid validation using a small set of features and scenarios. Less time-consuming option to determine the QA status of a build.
| coverage | Intended to validate the features and scenarios to a finer detail covering the most options and possible side effects. The most time-consuming operation to determine the QA status of a build.


## Reports

To build a beautified HTML report for a [selection](#selection) simply do:

```bash
cd docker
node ../tools/html_report.js -s </path/to/report/output.json> -o </path/to/pretty/report/output.html>
```

Once the report is finished it outputs:

```
Cucumber HTML report /path/to/pretty/report/output.html generated successfully.
```

To view the beautified version of the report please open the `/path/to/pretty/report/output.html` file.
