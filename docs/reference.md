**ai-doc-gen Technical Reference Document**
=============================================

Table of Contents
-----------------

1. [API Documentation](#api-documentation)
2. [Configuration Options](#configuration-options)
3. [Command-Line Interface Reference](#command-line-interface-reference)
4. [File Formats and Data Structures](#file-formats-and-data-structures)
5. [Architectural Overview](#architectural-overview)

**API Documentation**
---------------------

### Introduction

The ai-doc-gen API provides a set of endpoints for generating project documentation using AI.

### Endpoints

#### 1. Generate Documentation

* **URL:** `/generate`
* **Method:** `POST`
* **Request Body:**
	+ `input_text`: The input text to be used for generating documentation.
	+ `model`: The model to use for generation (e.g., "ollama", "llama").
* **Response:**
	+ A JSON object containing the generated documentation.

Example Request:
```bash
curl -X POST \
  https://localhost:8080/generate \
  -H 'Content-Type: application/json' \
  -d '{"input_text": "This is a sample input text.", "model": "ollama"}'
```

#### 2. Get Documentation Status

* **URL:** `/status`
* **Method:** `GET`
* **Query Parameters:**
	+ `status`: The status of the documentation generation process (e.g., "in_progress", "completed").

Example Request:
```bash
curl -X GET \
  https://localhost:8080/status?status=in_progress
```

**Configuration Options**
-------------------------

### Environment Variables

The following environment variables can be used to configure the project:

* `AI_DOC_GEN_MODEL`: The model to use for generating documentation (e.g., "ollama", "llama").
* `AI_DOC_GEN_INPUT_TEXT`: The input text to be used for generating documentation.
* `AI_DOC_GEN_OUTPUT_DIR`: The directory where the generated documentation will be stored.

**Command-Line Interface Reference**
-------------------------------------

### Installation

To install the project, run the following command:
```bash
pip install -r requirements.txt
```

### Usage

To generate documentation using the command-line interface, run the following command:
```bash
invoke
```
This will start the AI-doc-gen service and generate documentation based on the input text.

**File Formats and Data Structures**
--------------------------------------

The project uses the following file formats:

* `.txt`: The input text to be used for generating documentation.
* `.html`: The generated HTML documentation.

The project also uses the following data structures:

* `model`: The model to use for generating documentation (e.g., "ollama", "llama").
* `input_text`: The input text to be used for generating documentation.

**Architectural Overview**
---------------------------

### High-Level Diagram

Here is a high-level diagram of the project architecture:
```
          +---------------+
          |  Input Text  |
          +---------------+
                  |
                  |  o
                  v
+---------------+       +---------------+
|  AI Doc Gen  |       |  Output Directory|
+---------------+       +---------------+
        |                         |
        |  o                       |
        v                         v
+---------------+       +---------------+
|  Model    |       |  HTML Document  |
+---------------+       +---------------+
```
This diagram shows the input text being passed to the AI Doc Gen service, which generates an HTML document based on the model and input text.

Note: This is a simplified high-level diagram and may not show all the components of the project architecture.