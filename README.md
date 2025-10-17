# GDPR Obfuscator

[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://www.python.org/downloads/release/python-3130/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub issues](https://img.shields.io/github/issues/CharlotteC63/gdpr-obfuscator)]

## Overview
`Obfuscator` is a python module that locates a specified CSV, JSON or Parquet file within an AWS S3 bucket, obfuscates specified fields containing personally identifiable information (PII), and then returns a bytestream representation of the obfuscated file, preserving the original encoding and format type, ready for upload back to S3.

### How does obfuscation work?

When provided with (i) an s3 path to a file for obfuscation; and (ii) a list of PII fields, the module:
- detects the file format and encoding;
- uses this to read the file from S3 into a pandas DataFrame;
- replaces all values in the specified PII fields with the obfuscator string (default: "***");
- converts the DataFrame into a bytestream, preserving original file format and encoding;
- uploads the obfuscated file to s3 (when invoked in AWS Lambda)

## 📁 File Structure

```
gdpr-obfuscator/
├── .github
│   └── workflows
│       └── ci.yml          # CI/CD Automated deployment via Github Actions
│
├── dependencies-layer
│   └── python/             # Third party Python modules for AWS Lambda layer
│
├── src/
│   ├── utils/              # Python utility functions (for dependency injection)
│   ├── obfuscator.py       # Class containing attributes and methods
│   └── lambda_function.py  # AWS Lambda handler function
|
├── tests/
│   ├── data/               # Dummy data files for use in testing
│   └── test*.py            # Unit and integration tests for python functions (pytest)
|
├── .gitignore              # Files not to be pushed to remote repository
├── Makefile                # Automated environment setup & configuration
├── README.md               # Project overview
├── requirements-deploy.txt # Third party Python modules required for deployment
└── requirements.txt        # Third party Python modules required for development and testing
```

## 🔧 Tech Stack
- **Python 3.13** - Primary programming language
  - **Pytest** - Test Driven Development (TDD)
  - **Pandas** - Data transformation
  - **Boto3** - AWS SDK for Python
  - **Black** - Code formatting
  - **Flake8** - Linting
  - **Bandit** - Security analysis
- **Github** - Repository management, CI/CD (Github-Actions)
- **AWS** - S3, Lambda

## 🚀 Developer instructions

### Installing the module

If you are installing the module for development/testing purposes, use these commands in your terminal:

```bash
git clone https://github.com/CharlotteC63/gdpr-obfuscator.git
cd gdpr-obfuscator
make create-environment
source venv/bin/activate
make requirements
make dev-setup
```

### Continuous Integration and Deployment (CI/CD)

This project uses GitHub Actions for continuous integration and deployment, the workflow automatically runs tests and security checks.

The CI/CD pipeline is triggered on:
  - Pushes to the main branch
  - Pull requests targeting the main branch

The run-tests job performs the following steps:
 - Configures the Python environment and installs (development) dependencies
 - Runs python security, format and linting checks
 - Runs tests using pytest and checks test coverage

The run-build job performs the following:
 - Packages the dependencies and core code into zip files for AWS Lambda deployment

### 🧪 Testing
The project uses `pytest` for unit and integration testing. Tests are run via the CI/CD pipeline on every push or pull request to main.

Tests are located in the `tests/` directory, and can be run locally using the command:

```bash
pytest --testdox -vvvrP tests/
```

## 👩🏼‍💻 Deployment instructions

### Prerequisites

To use this module, the following prerequisites must be met:
- The file for obfuscation is stored in an S3 bucket accessible by the AWS account of the user
- The user has IAM user credentials (aws_access_key_id and aws_secret_access_key) with permissions to read from and write to the S3 bucket, and these have been configured in their local environment (if running locally) or assigned to the Lambda function's execution role (if deploying via AWS Lambda)
- The user knows and can provide:
  - the S3 path to the input data file (in one of the following formats: `s3://bucket-name/path/to/file`, `https://bucket-name/path/to/file` or `arn:aws:s3:::bucket-name/path/to/file`)
  - the names of the fields containing PII that need to be obfuscated (as they appear in the file header)
- The file format is either CSV, JSON or Parquet
- The file encoding is either UTF-8, UTF-16 or UTF-8-sig

### Installing the module

If you are installing the module to use in a production/deployment environment, use these commands in your terminal:

```bash
git clone https://github.com/CharlotteC63/gdpr-obfuscator.git
cd gdpr-obfuscator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-deploy.txt
```

### Importing the module
To import the module within your Python codebase (after installation), run:

```python
from obfuscator import Obfuscator
```

### Deployment options

#### AWS Lambda

The module is suitable for deployment via AWS Lambda. Follow these steps:

1. Run `make run-build` in the terminal. This will create the `dependencies-layer.zip` and `deployment-package.zip` files.
2. Go to the AWS Lambda Console and create a new Lambda function. For Runtime, select Python 3.13.
3. Go to the 'Layers' tab on the left navigation panel and select 'Create layer'. Select 'Upload a .zip file', then 'Choose file', then upload `dependencies-layer.zip`. Under 'Compatible runtimes' select 'Python 3.13', then select 'Create'. Navigate back to the Lambda function you created, select 'Layers' from the left navigation panel, then 'Add a layer'. Select 'Custom layers', then select the layer you just created, then select 'Add'.
4. In the 'Code' tab within the AWS Lambda Console, select 'Upload from' then '.zip file', then Upload the `deployment-package.zip` to the Lambda function, as the function code. The `lambda_handler` function in `lambda_function.py` serves as the entry point for the Lambda function.
5. Go to the IAM Console in AWS and navigate to 'Roles'. Select the role for the Lambda function you just created (it will have a name starting with [your-lambda-function-name]-role-...), then select 'Add Permissions', then 'Create Inline Policy'. In the JSON tab, paste the policy below, replacing my-ingestion-bucket with the name of your S3 bucket containing the files to be obfuscated. Select 'Next', then give the policy a name (S3AccessPolicy) and select 'Create Policy'.

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

6. Go back to the AWS Lambda Console and select your Lambda function. Under 'Configuration', select 'General Configuration', then 'Edit'. Increase the timeout to 1 minute (for files smaller than 1MB - larger files may require a longer timeout). Save the changes.
7. Test the Lambda function with sample input to ensure it works as expected. The tool is invoked by sending a JSON string to `lambda_handler` containing:
    - `file_to_obfuscate` (required): The s3 location of the required file for obfuscation (as a string)
    - `pii_fields` (required): A list of the PII fields to obfuscate (as a list of strings)

    For example, the input might be:

    ```json
    {
      "file_to_obfuscate": "s3://my-ingestion-bucket/new-data/my-file.csv",
      "pii_fields": ["name", "email_address", "phone_number"]
    }
    ```

8. (Optional) You may also wish to set up an S3 event trigger to automatically invoke the Lambda function when new files are uploaded to a specific S3 bucket or prefix.

#### Command line

The module can also be invoked from the command line following installation. See the below example:

```bash
python -c "from obfuscator import Obfuscator; obfuscator = Obfuscator(); obfuscated_df = obfuscator.get_obfuscated_df('s3://my-ingestion-bucket/new-data/my-file.csv', ['name', 'email_address']); obfuscated_bytes = obfuscator.get_obfuscated_bytestream(obfuscated_df)"
```

### Output

The output will be a bytestream representation of the file with the specified fields obfuscated with the string, "***".
The bytestream object will be compatible with boto3 Put Object, so the file can then be uploaded to S3.
The output file format will match the input file format (CSV, JSON or Parquet).

### Runtime performance

The runtime performance will depend on the size of the input file and the number of fields to obfuscate.

The module is able to handle files up to 1MB with a runtime of less than 1 minute.

### FAQs

- **Q: I want to change the obfuscator string, how do I do this?**
  - A: The default obfuscator string is "***". To change this, you can modify the `obfuscator_string` attribute in the `Obfuscator` class. For example:

  ```python
  obfuscator = Obfuscator()
  obfuscator.obfuscator_string = "your_chosen_obfuscator_string"
  ```

- **Q: If my input file is CSV, which delimiters are supported?**
  - A: The module supports comma (`,`), semicolon (`;`) and tab (`\t`) delimiters. The delimiter is automatically detected when reading the CSV file.

- **Q: If my input file is JSON, which formats are supported?**
  - A: The module supports both JSON lines (newline-delimited JSON) and standard JSON array formats. Examples of supported formats can be found in the `tests/data/` directory. The module does not currently support nested JSON objects.

- **Q: Do I need to provide the format type and encoding type of the file?**
  - A: No, the file type (CSV / JSON / Parquet) and encoding type (UTF-8 / UTF-16 / UTF-8-sig) are automatically detected by the tool when reading the file.

- **Q: What encoding types are supported?**
  - A: The module supports UTF-8, UTF-16 and UTF-8-sig encoded files. The encoding type is automatically detected when reading the file.

- **Q: What S3 path formats are supported?**
  - A: The module supports S3 paths in the following formats: `s3://bucket-name/path/to/file`, `https://bucket-name/path/to/file` or `arn:aws:s3:::bucket-name/path/to/file`. If an unsupported path format is provided by the user, an error will be raised (ValueError: "Invalid path format, could not extract bucket name").

- **Q: What happens if a specified PII field does not exist in the input file?**
  - A: If multiple PII fields are specified, and at least one of those fields is found within the file, that field will be obfuscated, and fields not found in the file will simply be skipped without raising an error. If *none* of the specified fields are found, an error will be raised (NoPIIFoundInFile: "None of the specified PII fields were found in the input file.").

- **Q: I'm getting a timeout error in Lambda, what should I do?**
  - A: This will occur if you are processing a large file (over 1MB), and your Lambda function is configured with a timeout of 1 minute or less. You can increase the timeout in the Lambda function configuration settings to resolve this error.

- **Q: When I run pytest locally I see ModuleNotFoundError: No module named 'hypothesis'. What should I do?**
  - A: Running pytest locally without specifying the `tests/` folder will mean third-party tests within the dependencies-layer are also run, causing import errors because the development environment setup does not install these optional dev dependencies (like hypothesis), as they are not required. To avoid this, ensure you run pytest with the `tests/` folder specified, e.g. `pytest --testdox -vvvrP tests/`.

- **Q: Which AWS regions is this module compatible with?**
  - A: The module is compatible with all AWS regions that support AWS Lambda and S3 services.

- **Q: Is there any logging implemented in the module?**
  - A: Basic logging is implemented within the module to track key events and errors. You can enhance or customize the logging as per your requirements.

- **Q: Can this module handle nested JSON objects?**
  - A: No, the module does not currently support nested JSON objects. It only supports flat JSON structures in both JSON lines and standard JSON array formats.

- **Q: How does the module handle missing values in PII fields?**
  - A: If a PII data field contains missing values, these will also be obfuscated with the obfuscator string. This ensures that the presence of missing values does not inadvertently reveal personally identifiable information (e.g. if it is known that a missing value in a certain field corresponds to a specific individual).

- **Q: Can I obfuscate multiple files in a single Lambda invocation?**
  - A: The current implementation is designed to obfuscate a single file per invocation. To obfuscate multiple files, you would need to invoke the Lambda function separately for each file.

- **Q: Is there a limit to the number of PII fields I can specify for obfuscation?**
  - A: There is no hard limit on the number of PII fields you can specify, but keep in mind that increasing the number of fields may impact performance.

- **Q: Is this module compliant with GDPR regulations?**
  - A: The module is designed to help obscure personally identifiable information (PII) in accordance with GDPR guidelines. However, it is up to the user to identify and specify the fields that require obfuscation to ensure compliance with GDPR.

- **Q: Where can I report bugs or request features?**
  - A: You can report bugs or request features by opening an issue in the GitHub repository.


## 👤 Author / maintainer
**Author:** Charlotte Campbell  
[GitHub: @CharlotteC63](https://github.com/CharlotteC63)  
[LinkedIn: Charlotte Campbell](https://linkedin.com/in/charlotte-campbell-15323a151/)


## 🌍 Links
- GitHub Repository: https://github.com/CharlotteC63/gdpr-obfuscator