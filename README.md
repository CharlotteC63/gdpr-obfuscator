# GDPR Obfuscator

[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://www.python.org/downloads/release/python-3130/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub issues](https://img.shields.io/github/issues/CharlotteC63/gdpr-obfuscator)]

## Overview
A python module that can be imported as a library to process data being ingested to AWS (or Apache) and obscure fields containing GDPR-sensitive data (personally identifiable information, PII).

## 📁 File Structure

```
gdpr-obfuscator/
├── .github
│   └── workflows
│       └── ci.yml     # CI/CD Automated deployment via Github Actions
├── src/
|   ├── utils/         # Python utility functions (for dependency injection)
│   └── obfuscator.py  # Class containing attributes and methods
|
├── tests/
|   ├── data/          # Dummy data files for use in testing
│   └── test*.py       # Unit and integration tests for python functions (pytest)
|
├── .gitignore         # Files not to be pushed to remote repository
├── Makefile           # Automated environment setup & configuration
├── README.md          # Project overview
└── requirements.txt   # Third party Python modules
```

## 🔧 Tech stack
- **Python 3.13** - Primary programming language
  - **Pytest** - Test Driven Development (TDD)
  - **Pandas** - Data transformation
- **Github** - Repository management, CI/CD (Github-Actions)
- **AWS** - S3, Lambda

## 🚀 Setup & Deployment

This project uses GitHub Actions for continuous integration and deployment, the workflow automatically runs tests and security checks.

The CI/CD pipeline is triggered on:
  - Pushes to the main branch
  - Pull requests targeting the main branch

The run-tests job performs the following steps:
 - Configures the Python environment and installs dependencies
 - Runs python security, format and linting checks
 - Runs pytests and checks test coverage

## 🧪 Testing
The project uses `pytest` for unit and integration testing. Tests run via CI/CD pipeline on every push to main or pull request.

Tests are located in the `tests/` directory, and can be run locally using the command:

```bash
pytest --testdox -vvvrP tests/
```

## 👩🏼‍💻 How to use this Python module

### Assumptions and prerequisites

This tool is used to obfuscate fields containing GDPR-sensitive data (personally identifiable information, PII) in data files being ingested to AWS (or Apache).

The following assumptions are made about the data being processed:

1. Data is stored in CSV, JSON, or parquet format in S3. Supported encoding types for CSV and JSON include UTF-8, UTF-16 and UTF-8-sig.
2. Fields containing GDPR-sensitive data are known and will be supplied in advance.
3. Data records will be supplied with a primary key.

### Importing the module
To import the Python module within your codebase, run:

```python
from obfuscator import Obfuscator
```

### Deployment options

#### AWS Lambda

The library is suitable for deployment on a platform within the AWS ecosystem, such as AWS Lambda. The dependencies
have already been zipped for use in AWS Lambda, and can be found in the `dependencies-layer.zip` file, and the core
code can be found in the `deployment-package.zip` file.

The tool is invoked by sending a JSON string to lambda_handler containing:
- `file_to_obfuscate` (required): The s3 location of the required file for obfuscation (as a string)
- `pii_fields` (required): A list of the PII fields to obfuscate (as a list of strings)

For example, the input might be:

```json
{
  "file_to_obfuscate": "s3://my-ingestion-bucket/new-data/my-file.csv",
  "pii_fields": ["name", "email_address", "phone_number"]
}
```

To deploy the module to AWS Lambda, follow these steps:
1. Run make run-build in the terminal. This will create the `dependencies-layer.zip` and `deployment-package.zip` files.
2. Go to the AWS Lambda Console and create a new Lambda function. For Runtime, select Python 3.13.
3. Go to the 'Layers' tab on the left navigation panel and select 'Create layer'. Select 'Upload a .zip file', then 'Choose file', then upload `dependencies-layer.zip`. Under 'Compatible runtimes' select 'Python 3.13', then select 'Create'. Navigate back to the Lambda function you created, select 'Layers' from the left navigation panel, then 'Add a layer'. Select 'Custom layers', then select the layer you just created, then select 'Add'.
4. In the 'Code' tab within the AWS Lambda Console, select 'Upload from' then '.zip file', then Upload the `deployment-package.zip` to the Lambda function, as the function code.
5. Go to the IAM Console in AWS and navigate to 'Roles'. Select the role for the Lambda function you just created (it will have a name starting with [your-lambda-function-name]-role-...), then select 'Add Permissions', then 'Create Inline Policy'. In the JSON tab, paste the following policy, replacing my-ingestion-bucket with the name of your S3 bucket containing the files to be obfuscated:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::my-ingestion-bucket/*"
        }
    ]
}
```
  Select 'Next', then give the policy a name (S3AccessPolicy) and select 'Create Policy'.

6. Go back to the AWS Lambda Console and select your Lambda function. Under 'Configuration', select 'General Configuration', then 'Edit'. Increase the timeout to 1 minute (for files smaller than 1MB - larger files may require a longer timeout). Save the changes.
7. Test the Lambda function with sample input to ensure it works as expected.
8. (Optional) You may also wish to set up an S3 event trigger to automatically invoke the Lambda function when new files are uploaded to a specific S3 bucket or prefix.

#### Command line

The library function can also be invoked from the command line. For example:

```bash
python -c "from obfuscator import Obfuscator; obfuscator = Obfuscator(); obfuscated_df = obfuscator.get_obfuscated_df('s3://my-ingestion-bucket/new-data/my-file.csv', ['name', 'email_address']); obfuscated_bytes = obfuscator.get_obfuscated_bytestream(obfuscated_df)"
```

### Output

The output will be a bytestream representation of the file with the specified fields obfuscated.
The bytestream object will be compatible with boto3 Put Object, so the file can then be uploaded to S3.
The output file format will match the input file format (CSV, JSON or parquet).

### Runtime performance

The runtime performance will depend on the size of the input file and the number of fields to obfuscate.

The module is able to handle files up to 1MB with a runtime of less than 1 minute.



## 👤 Author / maintainer
- Charlotte Campbell (GitHub: @CharlotteC63)

## 🌍 Links
- GitHub Repository: https://github.com/CharlotteC63/gdpr-obfuscator