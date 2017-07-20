@smoke
@health-check
Feature: Health Checks
  Ensures the Store is up and running.


  Scenario: Endpoints ready
    When I list the endpoints
    Then I expect the JSON response to be as in api-endpoints.json


