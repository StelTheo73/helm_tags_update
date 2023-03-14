# Update helm tags in requirements.yaml

<strong> For testing purposes, a specific Merge Request is specified in the code (lines 311-313 of ./src/requirements_yaml_updater.py), overriding the feature of specifying your own branch.</strong>

<strong> If you wish to test this script with a branch that <ins>follows</ins> the [limitations](#limitations), you have to:</strong>

* Uncomment line 311 of ./src/requirements_yaml_updater.py file.
* Remove lines 312 and 313 of the same file.


<strong> If you wish to test this script for an other branch that <ins>does not follow</ins> the [limitations](#limitations), change the value of override_branch_name variable (line 312 of ./src/requirements_yaml_updater.py) with the title of your MR. Keep in mind that the MR's title has to be the same in every helm project affected.</strong>


<hr>

## Description

This script updates helm tags in [/tas/kubernetes/helm/nokia-tas/requirements.yaml](https://gitlabe1.ext.net.nokia.com/tas/kubernetes/-/blob/ntas-19-0/helm/nokia-tas/requirements.yaml).

<hr>

## Limitations <a name="limitations"></a>

The title of the Merge Request of every helm project under [ntas/helm](https://scm.cci.nokia.net/ntas/helm) <strong><ins>has to start</ins></strong> with the name of the branch of [tas/kubernetes](https://gitlabe1.ext.net.nokia.com/tas/kubernetes) project.

For example, if branch name is <em>"ntas-xy-z-foo"</em> then the MR title of each helm project has to be like: 
* <em>"ntas-xy-z-foo "\<any text here\>"</em>

<hr>

## Installation

    pip install -r dependencies.txt

<hr>

## Usage
**Parameters**

* ***Optional***
    * `-b, --branch <string>`: The name of the branch of [tas/kubernetes](https://gitlabe1.ext.net.nokia.com/tas/kubernetes) project (script prompts for input if not provided).
    * `-d, --deep <boolean>`:
        - [True / 1]  --> All tags of each helm project will be fetched. Useful if you wish to update yaml file with the tags of an old branch.
        - [False / 0] --> (default) Only the last 50 tags of each helm project will be fetched.
    
**Execution**

If your branch of [tas/kubernetes](https://gitlabe1.ext.net.nokia.com/tas/kubernetes) project is: <em>ntas-xy-z-foo</em>
    
    python3 -m main -b ntas-xy-z-foo

