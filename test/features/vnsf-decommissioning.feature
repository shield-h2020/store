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


Feature: vNSF Decommissioning
"""
  NOTE: for the time being the decommissioning test is package-based, i.e., the package is first onboarded and right
  afterwards decommissioned. This is obviously not the desired behaviour but saves for now the overwork of populating
  the data store beforehand. Also ensuring the record is no longer in the data store is a must.
"""
  Validates the entire vNSF decommissioning process.


#  @smoke
#  Scenario Outline: Successful decommissioning
#    When I decommission a <vNSF>
#    Then I expect the response code <status>
#
#    Examples:
#      | vNSF                  | status |
#      | vnsf/xpto_vnfd.tar.gz | 204    |
