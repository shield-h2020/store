Feature: vNSF Onboarding
  Validates the entire vNSF onboarding process.


  @smoke
  Scenario Outline: Onboarding vNSF packages
    Given I mock the vNSFO response with <mock_file>
    When I onboard a vNSF <package>
    Then I expect the response code <status>
    Then I expect the JSON response to be as in <file>

    Examples:
      | mock_file                             | package                        | status | file                                  |
      # (codes: HTTP_201_CREATED, HTTP_502_BAD_GATEWAY)

      # Sucessful Store and the vNSFO operation.
      | mock-onboard-success-cirrus_vnsf.json | vnsf/shield_cirros_vnsf.tar.gz | 201    | vnsf/onboard-success-cirrus_vnsf.json |
      # vNSFO failure.
      | mock-onboard-failure-cirrus_vnsf.json | vnsf/shield_cirros_vnsf.tar.gz | 502    | vnsf/onboard-failure-cirrus_vnsf.json |


  @coverage
  Scenario Outline: vNSF packages onboarding failures
    Given I mock the vNSFO response with <mock_file>
    When I onboard a vNSF <package>
    Then I expect the response code <status>
    Then I expect the JSON response to be as in <file>

    Examples:
      | mock_file                             | package                                           | status | file                                         |
      # (codes: HTTP_406_NOT_ACCEPTABLE, HTTP_412_PRECONDITION_FAILED)

      # SHIELD package format isn't compliant (no .tar.gz format).
      | mock-onboard-success-cirrus_vnsf.json | vnsf/shield_cirros_vnsf.wrong_format.tar          | 412    | vnsf/onboard-failure-wrong_format.json       |
      # SHIELD package format isn't valid (no .tar.gz format).
      | mock-onboard-success-cirrus_vnsf.json | vnsf/shield_cirros_vnsf.other_format.zip          | 412    | vnsf/onboard-failure-wrong_format.json       |
      # vNSFO package format isn't compliant (vNSFO package is no .tar.gz).
      | mock-onboard-success-cirrus_vnsf.json | vnsf/shield_cirros_vnsf.wrong_format_vnsfo.tar.gz | 412    | vnsf/onboard-failure-wrong_format_vnsfo.json |
      # vNSFO package missing VNFD file.
      | mock-onboard-success-cirrus_vnsf.json | vnsf/shield_cirros_vnsf.missing_vnfd.tar.gz       | 406    | vnsf/onboard-failure-missing_vnfd.json       |
      # SHIELD package impersonation (not an actual .tar.gz file, just the extension).
      | mock-onboard-success-cirrus_vnsf.json | vnsf/shield_cirros_vnsf.impersonate.tar.gz        | 412    | vnsf/onboard-failure-wrong_format.json       |
      # vNSFO package impersonation (not an actual .tar.gz file, just the extension).
      | mock-onboard-success-cirrus_vnsf.json | vnsf/shield_cirros_vnsf.impersonate_vnsfo.tar.gz  | 412    | vnsf/onboard-failure-impersonate_vnsfo.json  |

