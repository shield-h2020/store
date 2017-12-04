/*
 *  Copyright (c) 2017 SHIELD, UBIWHERE
 * ALL RIGHTS RESERVED.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * Neither the name of the SHIELD, UBIWHERE nor the names of its
 * contributors may be used to endorse or promote products derived from this
 * software without specific prior written permission.
 *
 * This work has been performed in the framework of the SHIELD project,
 * funded by the European Commission under Grant number 700199 through the
 * Horizon 2020 program. The authors would like to acknowledge the contributions
 * of their colleagues of the SHIELD partner consortium (www.shield-h2020.eu).
 */

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
