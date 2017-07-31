Feature: vNSF Onboarding
  Validates the entire vNSF onboarding process.


  @smoke
  Scenario Outline: Onboarding fat packages
    Given I mock the vNSFO response with <mock_file>
    When I onboard a vNSF <package>
    Then I expect the response code <status>
    Then I expect the JSON response to be as in <file>

    Examples:
      | mock_file                           | package               | status | file                                |
      | mock-onboard-success-no_images.json | vnsf/xpto_vnfd.tar.gz | 201    | vnsf/onboard-success-no_images.json |
      | mock-onboard-failure-no_images.json | vnsf/xpto_vnfd.tar.gz | 502    | vnsf/onboard-failure-no_images.json |
