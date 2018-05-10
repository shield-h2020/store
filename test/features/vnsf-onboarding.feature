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


Feature: vNSF Onboarding
  Validates the entire vNSF onboarding process.


  @smoke
  Scenario Outline: Onboarding vNSF packages
    Given I mock the vNSFO response with <mock_file>
    When I onboard a vNSF <package>
    Then I expect the response code <status>
    Then I expect the JSON response to be as in <response>

    Examples:
      | mock_file                                  | package                       | status | response                              |
      # (codes: HTTP_201_CREATED, HTTP_502_BAD_GATEWAY, HTTP_422_UNPROCESSABLEENTITY)

      # Sucessful Store and the vNSFO operation.
      | vnsf/mock-onboard-success-cirros_vnsf.json | vnsf/shield_cirros_vnsf.tar.gz | 201    | vnsf/onboard-success-cirros_vnsf.json |
      # vNSFO failure.
      | vnsf/mock-onboard-failure-cirros_vnsf.json | vnsf/shield_cirros_vnsf.tar.gz | 428    | vnsf/onboard-failure-cirros_vnsf.json |
      # Bad vNSF descriptor syntax
      | vnsf/mock-onboard-success-cirros_vnsf.json | vnsf/shield_cirros_vnsf_wrong_descriptor_syntax.tar.gz | 422 | vnsf/onboard-failure-wrong_descriptor_syntax.json |


  @coverage
  Scenario Outline: vNSF packages onboarding failures
    Given I mock the vNSFO response with <mock_file>
    When I onboard a vNSF <package>
    Then I expect the response code <status>
    Then I expect the JSON response to be as in <response>

    Examples:
      | mock_file                                  | package                                           | status | response                                     |
      # (codes: HTTP_406_NOT_ACCEPTABLE, HTTP_412_PRECONDITION_FAILED)

      # SHIELD package format isn't compliant (no .tar.gz format).
      | vnsf/mock-onboard-success-cirros_vnsf.json | vnsf/shield_cirros_vnsf.wrong_format.tar          | 412    | vnsf/onboard-failure-wrong_format.json       |
      # SHIELD package format isn't valid (no .tar.gz format).
      | vnsf/mock-onboard-success-cirros_vnsf.json | vnsf/shield_cirros_vnsf.other_format.zip          | 412    | vnsf/onboard-failure-wrong_format.json       |
      # vNSFO package format isn't compliant (vNSFO package is no .tar.gz).
      | vnsf/mock-onboard-success-cirros_vnsf.json | vnsf/shield_cirros_vnsf.wrong_format_vnsfo.tar.gz | 428    | vnsf/onboard-failure-wrong_format_vnsfo.json |
      # vNSFO package missing VNFD file.
      | vnsf/mock-onboard-success-cirros_vnsf.json | vnsf/shield_cirros_vnsf.missing_vnfd.tar.gz       | 406    | vnsf/onboard-failure-missing_vnfd.json       |
      # SHIELD package impersonation (not an actual .tar.gz file, just the extension).
      | vnsf/mock-onboard-success-cirros_vnsf.json | vnsf/shield_cirros_vnsf.impersonate.tar.gz        | 412    | vnsf/onboard-failure-wrong_format.json       |
      # vNSFO package impersonation (not an actual .tar.gz file, just the extension).
      | vnsf/mock-onboard-success-cirros_vnsf.json | vnsf/shield_cirros_vnsf.impersonate_vnsfo.tar.gz  | 428    | vnsf/onboard-failure-impersonate_vnsfo.json  |

