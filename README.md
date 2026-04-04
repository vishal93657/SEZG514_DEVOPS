# ACEest Fitness & Gym

## Course: Introduction to DEVOPS

## Assignment Overview
Implementing Automated CI/CD Pipelines for ACEest Fitness & Gym

### Objective
This assignment is designed to provide students with comprehensive, hands-on experience in modern DevOps methodologies. By executing this project, students will attain professional proficiency in:
- **Version Control** (Git/GitHub)
- **Containerization** (Docker)
- **CI/CD Orchestration** (GitHub Actions and Jenkins)

### Problem Statement
You have been appointed as a Junior DevOps Engineer for ACEest Fitness & Gym, a rapidly scaling startup. Your mission is to architect and implement a robust, automated deployment workflow that guarantees code integrity, environmental consistency, and rapid delivery.

Your solution must transition the application through a rigorous lifecycle—from local development to an automated Jenkins BUILD environment.

---

## Core Assignment Phases

### 1. Application Development & Modularization
Develop a foundational Flask web application tailored for fitness and gym management. The baseline Python script initializes the core logic and service endpoints.

### 2. Version Control System (VCS) Strategy
Initialize a local Git repository and synchronize it with a remote GitHub counterpart. Follow industry standards for versioning, including:
- Descriptive commit messages
- Branch management to track features, bug fixes, and infrastructure updates

### 3. Unit Testing & Validation Framework
Integrate the Pytest framework to develop a comprehensive suite of unit tests. These tests validate the internal logic of the Flask application, ensuring all components perform according to specification before they reach the build stage.

### 4. Containerization with Docker
Encapsulate the Flask application, along with its environment and dependencies, into a portable Docker Image. This ensures "write once, run anywhere" consistency, eliminating the "it works on my machine" syndrome during the transition from testing to production.

### 5. The Jenkins BUILD & Quality Gate
Integrate a Jenkins server to handle the primary BUILD phase. Configure a Jenkins project that:
- Pulls the latest code from GitHub
- Performs a clean build of the environment
- Serves as a secondary validation layer to ensure code compiles and integrates correctly in a controlled build environment

### 6. Automated CI/CD Pipeline via GitHub Actions
Design a fully automated pipeline using GitHub Actions (`.github/workflows/main.yml`). The pipeline is triggered by every push or pull_request, executing the following critical stages:
- **Build & Lint**: Compile the application and check for syntax errors
- **Docker Image Assembly**: Successfully build the Docker container
- **Automated Testing**: Execute the Pytest suite inside the containerized environment to confirm stability

---

## Local Setup and Execution Instructions

Follow these steps to set up and run the application in your local environment:

### Prerequisites
- Python 3.10 or higher
- `pip` (Python package installer)
- Docker (for containerization testing)
- Git (for version control)

### Installation
1. Clone the repository to your local computer:
   ```bash
   git clone <your-repository-url>
   cd <your-repository-folder>
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application
Start the Flask application:
```bash
python app.py
```

The application will be accessible at `http://localhost:5000`.

---

## Steps to Run Tests Manually

### Unit Testing with Pytest
Run the complete test suite:
```bash
pytest tests/test_app.py -v
```

Run tests with coverage report:
```bash
pytest tests/test_app.py --cov=. --cov-report=html
```

Run a specific test:
```bash
pytest tests/test_app.py::test_<function_name> -v
```

---

## Docker Setup and Execution

### Building the Docker Image
Build the Docker image locally:
```bash
docker build -t fitapp:latest .
```

### Running the Container
Run the application inside a Docker container:
```bash
docker run -p 5000:5000 fitapp:latest
```

The application will be accessible at `http://localhost:5000`.

### Running Tests Inside Docker
Execute tests within the containerized environment:
```bash
docker run fitapp:latest pytest tests/test_app.py -v
```

---

## Jenkins and GitHub Actions Integration

### Jenkins BUILD Pipeline
The Jenkins server is configured to automatically trigger on GitHub Webhook when changes are pushed to the main branch. The build process executes the following steps:

#### Jenkins Build Script

```batch
REM Jenkins Build Script for ACEest Fitness & Gym App

REM Step 1: Build Docker image
docker build -t fitness-app .

REM Step 2: Run lint check inside Docker container
docker run --rm fitness-app python -m pylint app.py tests/test_app.py --disable=all --enable=E

REM Step 3: Run unit tests inside Docker container
docker run --rm fitness-app python -m pytest -v

REM Optional: run the app inside container for manual verification
REM docker run --rm -p 5000:5000 fitness-app
```

#### Build Stages

1. **Docker Image Build** (Step 1)
   - Builds a Docker image from the Dockerfile
   - Tags the image as `fitness-app` for consistent naming
   - Ensures all dependencies are packaged correctly

2. **Code Quality Gate - Linting** (Step 2)
   - Runs Pylint on `app.py` and `test_app.py`
   - Checks for syntax errors and code quality issues
   - Only enables error checks (`--disable=all --enable=E`)
   - Fails the build if any errors are found

3. **Quality Gate - Unit Testing** (Step 3)
   - Executes the complete Pytest suite in verbose mode
   - Validates all endpoints and business logic
   - Fails the build if any tests do not pass
   - Ensures code integrity before deployment

4. **Manual Verification (Optional)**
   - Allows developers to test the containerized application
   - Runs the Flask app on port 5000 for integration testing
   - Useful for pre-deployment validation

**Expected Outcome**: A successfully built Docker image (`fitness-app`) with verified code quality and passing test suite, ready for deployment.

### GitHub Actions Workflow
The GitHub Actions pipeline (`.github/workflows/main.yml`) automates the following stages:

**Build & Lint Stage**:
- Checks Python syntax errors
- Validates code quality with linting tools
- Ensures all dependencies are correctly specified

**Docker Image Assembly**:
- Builds the Docker image from the Dockerfile
- Tags the image with the commit SHA for version tracking
- Verifies image integrity

**Automated Testing**:
- Executes the Pytest suite inside the containerized environment
- Validates all endpoints and business logic
- Generates coverage reports
- Fails the pipeline if any test does not pass

**Pipeline Triggers**: Every `push` or `pull_request` event

---