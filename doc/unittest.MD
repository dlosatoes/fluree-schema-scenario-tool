## Build stage unit testing

A project directory contains the build.json directory defining one or multiple build targets.
A [build target](buildtarget.MD) consists of one or multiple steps or stages. 
Each step contains a number of transactions, and might optionally contain unit test definition for that stage.
It is important to note that while unit tests *within* a stage might end up conflicting if not constructed correctly, because they act on the same database, the system design of the *fsst* tool is such that tests in a single stage end up being run in one database, and test in an other stage directory will get run in a different database. This allows for meningfully isolation of stage unit tests.

Before we look into the directory structure for the unit tests for a single stage, we need to discuss the test flow for *fsst*.

Let's imagine a build target with seven stages:

* stage1: no tests
* stage2: no tests
* stage3: tests
* stage4: no tests
* stage5: tests
* stage6: tests
* stage7: no tests

What will happen here is that *fsst* will:

* create a database, run all transactions from stage1..stage3 and run the stage3 tests.
* create another database, run all transactions from stage1..stage5 and run the stage5 tests
* create a 3th database, run all transactions from stage1..stage6 and run the stage6 tests

The transactions in stage7 will never get used in any test or database, as stage7 has no tests and no stage after it has either because it is the final stage.

### Stage test definitions

Next to the file *main.json*, a *step or stage directory* may contain the file *test.json*. This file looks something like this:

```json
[
  "test1"
]
```

The file contains a simple JSON array of strings. Each string in the array designates a *test scenario* for the build step. Each test scenario directory could contain the following files:

* user.json
* prepare.json
* yes.json
* no.json
* tyes.json
* tno.json
* cleanup.json

The *user.json* and *prepare.json* files are mandatory. The other ones are optional. We'll discuss the content of these files in the *testing* section below.


#### prepare.json

In prepare.json we are responsible for defining the flureeDB auth records needed to run our tests with

```json
[
  [
    {
      "_id": "_auth",
      "id": "TeyTH5RdmweiWzrkEzwc5vYnPwqZDSh8Ng6",
      "roles": [["_role/id","root"]]
    }
  ],
  [
    {
      "_id": "_auth",
      "id": "Tf5p2VyQgYJQ6p8suVkX633BD4kQgsp29FC",
      "roles": [["_role/id","root"]]
    }
  ]
]
```

In actually usefull tests, more meaningfull roles than *root* should get used.

#### user.json

For each of these _auth records, an entry in the *user.json* file defines the keys and when these keys will get used.

```json
{
   "keys" : [
      {
         "account-id" : "TeyTH5RdmweiWzrkEzwc5vYnPwqZDSh8Ng6",
         "private" : "bb19048fbfc8f6a7f02b336048fa8e5aba1fb87f55893d40ff1ba375b90a8398"
      },
      {
         "account-id" : "Tf5p2VyQgYJQ6p8suVkX633BD4kQgsp29FC",
         "private" : "b11648b8f45a2cae682cbc549c35b065dff32794562b0765874e911e31163469"
      }
   ],
   "no" : 0,
   "yes" : 0,
   "tno": 1,
   "tyes": [0,1,1,1,1]
}
```

This file defines two keys. The key at index 0 will get used for the *yes*, and the *no* queries as defined in the test. Also the *first* transaction in the *tyes* tests will use this key. The other transactions in *tyes and *tno* will use the key at index 1.

It is important to note that with this definition, the number of transactions in tyes.json will need to match the the number of entries in the tyes array.

#### yes.json and no.json

These files, if they exist, should contain an array of flureeql *queries*. A query in yes.json constitutes a failure if either:

* The query returns an empty array
* The query contains a non-empty array, but the entries in the response are objects containing only the _id predicate.

Otherwise, the query is considdered successfull.

For no.json it is the other way arround. 

####  tyes.json and tno.json

These files are like yes.json and no.json, but instead of queries, they contain transactions. The failure vs success of these transactions is a bit more involved. This is because a transaction is always combined with a query for transaction success, a query that might return an empty answer either when the transaction isn't done yet, or if the _auth querying for completion has insufficient rights to query the _tx collection. To overcome this problem, *fsst* will query the transaction with both the all powerfull default key as with the key defined in user.json.

For tyes.json:

* A transaction is successfull if the transaction doesn't fail and the key from user.json is able to query the result
* A transaction is unsuccesfull if the transaction fails
* A transaction is unsuccessfull if if the transaction doesnt fail and the key from user.json isnt able to query the result

For tno.json:

* A transaction is successfull if the transaction fails
* A transaction is unsuccesfull if the transaction succeeds.
* If the _auth isnt able to query the result, this is logged as a warning, but by itself isnt considered failure.

#### cleanup.json

This file contains any desired cleanup transactions that might be needed for test isolation between tests within the same stage.
