const argv = require('argv');
var reporter = require('cucumber-html-reporter');


/*
 **
 **    Input arguments validation.
 **
 */

const args = argv.option([{
        name: 'theme',
        short: 't',
        type: 'string',
        description: '(Optional) The HTML report theme to use. Available: bootstrap, hierarchy, foundation and simple. Defaults to bootstrap.',
        example: "'<script> --theme=<Available>'"
    }, {
        name: 'source',
        short: 's',
        type: 'path',
        description: '(Mandatory) The path to the tests report file. Format: cucumber-JSON test report.',
        example: "'<script> --source=/path/to/tests/report/file.json'"
    }, {
        name: 'output',
        short: 'o',
        type: 'path',
        description: '(Mandatory) The path, including file name, where to store the HTML tests report.',
        example: "'<script> --output=/path/to/tests/report/output/file.html'"
    }])
    .info('Produces a nice HTML tests report from a cucumber-JSON test report.')
    .version('v0.1.0')
    .run();

if (args.options['source'] === undefined ||
    args.options['output'] === undefined) {

    console.log("\n!!! Error!!! Missing parameters.\n");
    argv.help();
    process.exit();
}


const theme = args.options['theme'] || 'bootstrap';
const source = args.options['source'];
const output = args.options['output'];


/*
 **
 **    Main block.
 **
 */


var options = {
    theme: theme,
    jsonFile: source,
    output: output,
    reportSuiteAsScenarios: true,
    launchReport: true,
    metadata: {
        "App Version": "0.1.0",
        "Test Environment": "QA"
    }
};

reporter.generate(options);
