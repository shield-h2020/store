Feature: vNSF Onboarding
  Validates the entire vNSF onboarding process.


  @smoke
  Scenario Outline: Successful onboarding
    When I onboard a vNSF <package>
    Then I expect the JSON response to be as in <file>

    Examples:
      | package               | file                                |
      | vnsf/xpto_vnfd.tar.gz | vnsf/onboard-success-no_images.json |
