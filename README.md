# GDPR Obfuscator Project

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
- **Github** - Repository management, CI/CD (Github-Actions), Credentials Security (Github-Secrets)
- **AWS** - S3, Lambda, CloudWatch, Step Functions

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
pytest tests/
```

## 👩🏼‍💻 How to use this Python module

### Assumptions and prerequisites

The following assumptions are made about the data being processed:
1. Data is stored in CSV, JSON, or parquet format in S3. Supported encoding types for CSV and JSON include UTF-8, UTF-16 and UTF-8-SIG.
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
have already been zipped for use in AWS Lambda, and can be found in the `deployment-package.zip` and `pandas-layer.zip` and `fastparquet-layer.zip` files.

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
1. Create a new Lambda function in the AWS Management Console.
2. Upload the pandas-pyarrow-layer.zip as a Lambda Layer. Attach the layer to the Lambda function.
3. Upload the deployment-package.zip to the Lambda function.
4. Set the handler to point to the module and function (e.g., `obfuscator.lambda_handler`).
5. Configure the necessary IAM roles and permissions for the Lambda function to access S3.
6. Set environment variables if needed (e.g., for configuration settings).
7. Test the Lambda function with sample input to ensure it works as expected.  

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