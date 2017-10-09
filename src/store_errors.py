# -*- coding: utf-8 -*-

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


# HTTP status codes
HTTP_200_OK = 200
HTTP_406_NOT_ACCEPTABLE = 406
HTTP_412_PRECONDITION_FAILED = 412
HTTP_502_BAD_GATEWAY = 502

# Onboarding package-related.
PKG_MISSING_FILE = 'No package provided'
PKG_NOT_TARGZ = 'Package is not a valid .tar.gz file'
PKG_NOT_SHIELD = 'Package does not comply with the SHIELD format'
PKG_MISSING_VNFD = 'vNF Descriptor not found where manifest.yaml places it'
PKG_NOT_VNSFO = 'Package does not comply with the vNSFO format'

# vNSF-related.
VNSF_NOT_ADDED_TO_CATALOG = 'Catalog insertion failed'
