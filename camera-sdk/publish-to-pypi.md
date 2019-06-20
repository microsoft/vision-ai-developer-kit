# How to publish iotccsdk to PyPI
To publish the package you will need to provide your credentials for PyPI and to be a manager on the [iotccsdk project in PyPI](https://pypi.org/project/iotccsdk/)

After making all of the changes desired to the iotccsdk and testing the changes use these steps to create the package for upload:
1. Update the setup.py file version to a new version using [Semantic Versioning](https://semver.org/) rules
1. Delete the ./dist folder from this project
1. Run the python command to build the wheel file and package

    ```python setup.py sdist bdist_wheel```
1. Ensure that you have twine installed 

    ```pip install twine```
1. Run twine to check the package

    ```twine check dist/*```
1. Upload the package using twine

    ```twine updload dist/*```

Navigate to the [project page](https://pypi.org/project/iotccsdk/) and make sure that the changes you expect are present.

## Publish to  Test PyPI
If you wish to test changes to the published version before creating a new version you should use https://test.pypi.org to do that. You must create a separate account on the test instance of PyPI. Once you have an account and are ready to publish you can run:

```twine upload --repository-url https://test.pypi.org/legacy/ dist/* ```

Then got to the project page on https://test.pypi.org/project/iotccsdk/ to see the results.
