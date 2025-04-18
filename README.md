## pygen: A Python test case and code generator

### Getting Started

These instructions are for using the `pygen.py` script to use AI to generate test cases and automation code from JIRA
tickets. Test cases are written in a human-readable format whereas the code is written in TypeScript.

### Tech Stack

The Azure OpenAI project is built with the following set of technologies:

* **Pip**: Lifecycle and dependency management
* **Python**: Programming language
* **Azure OpenAI Service**: Access to the AI chat completion models

### System Requirements

Python is required in order to install dependencies and run the script. You can download
it [here](https://www.python.org/downloads/). To test the installation, run the following commands:

**Mac/Linux:**

```bash
python3 --version; pip3 --version
```

**Windows:**

```
py --version & pip3 --version
```

If `py` does not work but `pip3` does, rerun the command with:

```
python --version & pip3 --version
```

### Installation

All required dependencies can be installed by running the following command from the `scripts` directory:

**Mac/Linux:**

```bash
./setup.sh
```

**Windows:**

```
setup.bat
```

Dependencies are installed as user packages but if an error regarding an "externally-managed-environment" occurs during
setup, pass `--break-system-packages` as a parameter to the script. Example:

**Mac/Linux:**

```bash
./setup.sh --break-system-packages
```

**Windows:**

```
setup.bat --break-system-packages
```

### Setup

The pygen project is expecting environment variables to be set in order to make API calls to the chat completion models.
You can set these variables using a variety of methods, but the simplest method is to put them in a `.env` file in the
project root directory.

* **AZURE_OPENAI_API_KEY**: The Azure OpenAI API key.
* **AZURE_OPENAI_ENDPOINT**: The Azure OpenAI endpoint (e.g. https://qatesting.openai.azure.com).
* **AZURE_SEARCH_KEY**: The Azure search key.
* **AZURE_SEARCH_SERVICE_ENDPOINT**: The Azure search service endpoint (
  e.g. https://ai-search-dev-copilot234082715031.search.windows.net).
* **JIRA_API_ENDPOINT**: The JIRA API endpoint. (e.g. https://benefitsolutionsinc.atlassian.net/rest/api/2/issue).
* **JIRA_API_TOKEN**: The JIRA API token.
* **JIRA_API_USERNAME**: The JIRA API username.

Reach out to a developer for obtaining key and token values as they are not stored in any repository.

### Using pygen

`pygen.py` is a command line utility for generating test cases from JIRA tickets. The only required parameter is the
ticket number specified with `-t` or `--ticket`. Example:

**Mac/Linux:**

```bash
./pygen.py -t QUO-5620
```

**Windows:**

```
py pygen.py -t QUO-5620
```

To see all the available options, use `-h` or `--help`. Example:

**Mac/Linux:**

```bash
./pygen.py -h
```

**Windows:**

```
py pygen.py -h
```

Output from the `help` option:

```
usage: pygen.py [-h] [--no-code | --no-test-cases] [-H methods] [-f field] [-l {debug,info,warning,error}] [-m model]
                [-o folder] [-s] -t ticket [-v]

utility for generating test cases from jira tickets

options:
  -h, --help                                    show this help message and exit
  --no-code                                     do not generate code
  --no-test-cases                               do not generate test cases
  -H, --helper-methods methods                  the number of helper methods to query for
  -f, --field field                             the jira ticket qa field
  -l, --log-level {debug,info,warning,error}    set the log level
  -m, --model model                             the model to use for generating code
  -o, --output-folder folder                    the output folder
  -s, --split                                   split test cases and code into separate files
  -t ticket, --ticket ticket                    the jira ticket id
  -v, --version                                 show program's version number and exit
```

**Defaults:**

* `field`: description
* `log-level`: info
* `helper-methods`: 5
* `model`: GPT_4
* `output-folder`: ai_generated

### AI Generated Output

The test cases and code are saved to the output folder. By default, this is `ai-generated` but can be set by using the
`-o` or `--output` option. Files are organized by the ticket number and can be in a single file or split into two files
if the `-s` or `--split` option is used. Example:

```
quo-5620-test-cases.txt
quo-5620-code.test.ts
```

### Deployed Models

The following models are deployed and are available to be used for generating test cases and code.

* **GPT-35-Turbo**: The most capable and cost-effective model in the gpt-3.5 family and has been optimized for chat.
* **GPT-4**: Can solve complex problems with great accuracy. It is the default code generation model.
* **GPT-4o**: Engineered for speed and efficiency and can handle complex queries.
* **text-embedding-ada-002**: Specializes in text and code search.

### How it Works

The process to generate test cases and code uses a total of four API calls. The Microsoft Azure OpenAI platform
uses a chat history that is expanded upon and/or reset throughout the process when communicating with the chat
completion model. The chat history is divided into two parts: `system` and `user`. The `system` chat history is
predefined and provides context whereas the `user` chat history is dynamic and acts as the query.

**System Messages:**

* **QA Message**: Tells the AI that it specializes in writing test cases from tickets.
* **TypeScript API Dev Message**: Tells the AI that it is a senior engineer that writes test cases for validating REST
  web services using TypeScript and the Jest test framework.

**API Calls:**

* **Get JIRA Ticket Information**
* **Generate Test Cases**
* **Search for Helper Methods**
* **Generate Test Code**

**Get JIRA Ticket Information:**
This is a GET call to our JIRA APIs using the ticket id and field. The response is the ticket information.

**Generate Test Cases:**
This call adds the **QA Message** and the JIRA ticket information to the `system` chat history and asks the chat
completion model to write test cases. The response is a list of test cases. If the `--no-test-cases` option was used,
then this call is bypassed and the test cases are set to the ticket information.

**Search for Helper Methods:**
This call takes the test cases that were generated and uses that as search criteria to make a vectorized search of the
indexed code using a hybrid search. The response is a list of helper methods with their name, description and code. This
call is skipped if the `--no-code` option was used.

**Generate Test Code:**
This call resets the `system` chat history and adds the **TypeScript API Dev Message** to it. The test cases and helper
methods are added to the `user` chat history and a call is made to the chat completion model to write code for the test
cases. The response is the code. This call is skipped if the `--no-code` option was used.
