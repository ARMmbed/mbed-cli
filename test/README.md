# Testing

Tests for *neo* are based on the [pytest framework](http://pytest.org/latest/).
To run the available tests, invoke py.test on the test directory:

``` bash
py.test test
```

The easiest way to debug failing tests is to run them individually. The names for specific
tests can be found with the `-v` option.

``` bash
py.test test/ls_test.py::test_ls[git1]
```

## Test structure

Each function that begins with `test_` indicates a test to run. `util.py` provides useful
testing utilities for testing *neo*.

- The `neo` [fixture](http://pytest.org/latest/fixture.html#fixture) provides the path to
  the current `neo` python script.

- The `testrepos` [fixture](http://pytest.org/latest/fixture.html#fixture) provides a set
  of repositories to test against of varying git/hg combinations. Each repository has a local
  "server" specified by absolute path and the server address can be accesses through the 
  `testrepos` variable. Currently the repostories are laid out in the following:

```
test1
`- test2
   `- test3
      `- test4
```

- The `assertls` takes a neo path, directory to test, and a structure of repositories to compare
  against the result of `neo ls`.

`ls_test.py` provides the simpliest test to demonstrate the framework.
