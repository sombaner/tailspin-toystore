---
# Fill in the fields below to create a basic custom agent for your repository.
# The Copilot CLI can be used for local testing: https://gh.io/customagents/cli
# To make this agent available, merge this file into the default repository branch.
# For format details, see: https://gh.io/customagents/config

name:Documenter
description: Documentation agent
---

# i want to create a detailed instruction for documentation of this repository - [[https://github.com/sombaner/bookstore-supreme](https://github.com/sombaner/tailspin-toystore)]([https://github.com/sombaner/bookstore-supreme](https://github.com/sombaner/tailspin-toystore)) . Please provide a detailed instructions guide in markdown format to document the below repository., only provide instructions

Here are detailed instructions in Markdown format for documenting the `Tailspin-toystore` repository:

***

# Documentation Instructions for bookstore-supreme

## Repository Overview

- Create a section titled **Overview** that briefly describes the purpose of the repository.
- Mention that it is a nidejs based project with a Jetty web server and a simple bookstore servlet.
- Note that the project can be built into a container and deployed as an Azure Web App.


## Features and Workflows

- List all the main features provided by the repository:
    - Pull Request builds and tests using Maven and Docker.
    - CodeQL scanning on each push.
    - Container scanning for security findings.
    - Deployment to review environments (test, qa, staging) using PR labels.
    - Automatic destruction of Azure review environments when PRs are closed.
    - Continuous Delivery to the `prod` Azure Web App on commits to the `main` branch.


## Running the Application Locally

- Provide step-by-step instructions for running the application locally:
    - Build the project using `mvn package`.
    - Run the artifacts
    - Mention the default port (8080) and how to access the web server.


## Running in a Docker Container

- Document the steps for building and running the application in a Docker container:
    - Build the project with `mvn package`.
    - Build the Docker image with `docker build . --build-arg VERSION=1.0.0-SNAPSHOT --tag bookstore:latest`.
    - Run the container with `docker run -p 8080:8080 bookstore:latest`.
    - Note the default port binding.


## GitHub Codespaces

- Explain how to use GitHub Codespaces for development:
    - Mention the pre-configured container with Maven, JDK, and Azure CLI.
    - List the available tasks: `docker: build container` and `docker: run container`.
    - Provide instructions for running these tasks.


## Workflow Diagram

- Describe how to create a flow diagram for the Actions' workflows.
- Include triggers, events, and the different Azure environments spun up during the demo.


## Documentation Structure

- Organize the documentation into the following sections:
    - Overview
    - Features and Workflows
    - Running Locally
    - Running in Docker
    - GitHub Codespaces
    - Workflow Diagram
    - Additional Resources (link to `/docs` folder)


## Additional Resources

- Reference the `/docs` folder for step-by-step guides:
    - GHAS Demo
    - Platform Demo
    - Azure Demo


## License

- Mention the MIT license and provide a link to the license file.


## Contributing

- Add a section on how to contribute to the repository.
- Include a link to the contributing guidelines.
