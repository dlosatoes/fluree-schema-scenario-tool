## domain.json

The *domain.json* file, when found in a stage or step directory and running one of the fsst test commands with version 0.3 or higher, a set of Python tests will be run that are defined in the [apimap](https://github.com/pibara/aioflureedb/blob/master/apimap.MD).

Here we describe the format used in the domain.json file. Let's do so using an example:

```json
[
  {
      "doc": "Test if the role slartibartfast can do everything defined in the domain API",
      "auth": "$auth00",
      "user": "test_backend",
      "auth_roles": ["slartibartfast"],
      "api_role": "slartibartfast",
      "minimal_coverage": 16.5
  },
  {
      "doc": "Test if the role marvin can't do anything in the sso2fluree role except for get_roles",
      "auth": "$auth01",
      "user": "whatdoyoucare",
      "auth_roles": ["marvin"],
      "api_role": "slartibartfast",
      "test": "slartibartfast",
      "should_succeed": false,
      "should_succeed_exceptions":  ["get_roles"],
      "warn_only": true,
      "warn_only_exceptions": ["get_roles"],
      "skip": [
              "delete_user_by_auth",
              "delete_user_by_id",
              "replace_key",
              "get_auth_handles",
              "get_user_contacts"],
      "minimal_coverage": 50.0
  }
]
```

### _auth and _user related fields

The file defines a collection of test sets. Each test set will be run on a freshly installed new database using all the stages up and untill the current stage. 
The test set will be run using two identities: The *root* identity and the one defined in the test set description. In FlureeDB the _auth and _user collection are closely related and relevant for test-set definition. We always bind an _auth to a _user for a test. The *fsst* tool will populate the database with 32 _auth records: "auth00" up to "auth31". The *auth* field in the tests above defines which _auth (and matching signing key) will be used foer the given test-set.
The *user* field is used to create a new _user record and bind it to the _auth designated by *auth*. Finaly, both the _user and the _auth can be bound to zero or more *roles*. The fields **auth_roles** and **user_roles** bind the _user and/or _auth to its relevant roles for testing.

### link to the apimap

The fields **api_role** and **test** are closely related. If **test is undefined, it defaults to the value of **api_role**. Usually the two will be the same and **test** won't need to be defined.

* api_role: Defines the API map to use and determines what methods are available from within a test set. Also determines what a coverage percentage relates to.
* test: Defines the name of the python test file. It is suggested to use the same name as the role for this file, unless there are reasons to have more than one file.
* minimal_coverage: Defines the percentage of the number of methods defined in the apimap for api_role that needs to exist and not fail in order for sufficient coverage to be considered to be achieved. 

## Negative tests

By default, tests are expected to succeed. This default can be changed by setting **should_succeed** to **False** (that defaults to True). Exceptions to the value of should_succeed can be set using the **should_succeed_exceptions** field. This field defines an array of test names in our test set that should use the inverted value of should_succeed. So if should_succeed is undefined or True and a named test is added to should_succeed_exceptions, then that test is expected to fail. If however should_succeed is set to False and a named test is added to should_succeed_exceptions, then that test is expected to succeed.

## Hard fail or warn only?

By default all tests that fail will throw an exception and make fsst hard fail. Just as with should_succeed there are two fields that can be used to change this behaviour: warn_only, that defaults to False and warn_only_exceptions. These two fields work in the exact same way as should_succeed and should_succeed_exceptions with the exception of the default value.

## Skipping specific tests.

Skipped tests, defined by the field **skip** will be skipped for a test set. You should be verry carefull adding tests to this set as the tests aren't just skipped, they also are no longer counted towards the coverage requirement. 
