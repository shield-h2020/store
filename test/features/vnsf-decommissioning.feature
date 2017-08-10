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
