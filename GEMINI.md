# Gemini Project Context: Large Model Evaluation Framework

## Directory Overview

This repository serves as a comprehensive, structured knowledge base and framework for the evaluation of Large Language Models (LLMs) and other AI models. Its primary goal is to create a "panoramic" view of model capabilities and specifications to support product design, particularly within the automotive industry.

The project is organized as a collection of structured data files (JSON), documentation (Markdown), and supporting scripts (Python). It is not a single runnable application but a system for managing the data and processes related to AI model evaluation.

The core philosophy is to link product requirements to measurable production metrics, ensuring a traceable and quantifiable evaluation process from design to deployment.

## Key Concepts & Structure

The repository is built around several key concepts, each housed in its own directory:

*   **`models/`**: Contains detailed specifications for various AI models. The schema for these files is defined in `templates/model_schema.json`. This is the central registry of all models under consideration.

*   **`indicators/`**: A pool of performance and quality indicators (metrics) used for evaluation. Each indicator is defined in a JSON file, detailing its calculation method, source, and purpose. The template is `templates/indicator_template.json`.

*   **`benchmarks/`**: Holds the results and definitions of benchmarks run against various models. This provides the baseline data for comparison.

*   **`scenarios/`**: Describes specific use-case scenarios (e.g., "Voice Knowledge Q&A," "Driver Monitoring"). Each scenario maps to a set of required model capabilities and performance indicators, linking abstract model performance to real-world application requirements.

*   **`product_lines/`**: This is a key concept for traceability. These files link a specific product's features to the required model capabilities, scenarios, and acceptance metrics defined elsewhere in the repository. This allows for automated regression tracking and clear acceptance criteria. The schema is in `templates/product_line_schema.json`.

*   **`templates/`**: This directory is crucial as it contains the JSON schemas and templates for all major data structures used in the repository (models, indicators, agents, product lines, etc.). It enforces data consistency.

*   **`scripts/` & `tools/`**: A collection of Python scripts and other tools for automating tasks such as:
    *   Validating data files against their schemas (`scripts/validate_models.py`).
    *   Estimating VRAM and other performance characteristics (`scripts/estimate_vram.py`).
    *   Logging QA history (`tools/log_qa.py`).

*   **`registration/`**: Contains documentation and checklists related to AI compliance, regulations, and responsible AI principles (e.g., EU AI Act, NIST AI RMF).

## Usage & Workflow

The intended workflow for using this repository is as follows:

1.  **Define Entities**: New models, evaluation indicators, or application scenarios are added by creating new JSON files in the `models/`, `indicators/`, or `scenarios/` directories, respectively. These files must conform to the schemas defined in `templates/`.

2.  **Create a Product Line**: To track a new product or feature, create a new file in `product_lines/`. In this file, link the product's requirements to the specific `models`, `scenarios`, and `indicators` that are relevant.

3.  **Run Benchmarks & Evaluations**: Use the definitions and tools in this repository to run evaluations. Store the results in the `benchmarks/` directory.

4.  **Validate & Automate**: Use the provided Python scripts to validate the integrity and consistency of the data. For example, ensuring that a `product_line` file correctly references existing models and indicators. These scripts are intended to be integrated into a CI/CD pipeline.

5.  **Query & Report**: The structured nature of the repository allows for the data to be easily queried to generate reports, compare models, and track the readiness of a product line for deployment.
