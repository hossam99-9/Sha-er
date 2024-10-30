# Allam Challenge 2024

This project is designed to facilitate building and running a Dockerized environment for the Allam Challenge 2024. It includes a `start.sh` script that ensures the necessary models are downloaded, directories are set up, and the Docker containers are built and started.

## Features
- **Automated Setup**: `start.sh` handles the creation of necessary directories and downloads the required SentenceTransformer model.
- **Dockerized Environment**: Easily build and run the project with Docker Compose.
- **Multilingual Model**: Utilizes the `paraphrase-multilingual-mpnet-base-v2` from the SentenceTransformers library for sentence embedding.

## Prerequisites
Before running this project, ensure you have the following installed:
- Docker
- Docker Compose
- Python 3.x

## How to Run the Project

1. **Clone the Repository:**

    ```bash
    git clone <your-repository-url>
    cd <your-repository-name>
    ```

2. **Make the `start.sh` Script Executable:**

    You need to make sure the `start.sh` file has the necessary permissions to be executed.

    ```bash
    chmod +x start.sh
    ```

3. **Run the `start.sh` Script:**

    The `start.sh` script will:
    - Create the required `models` folder.
    - Download the `paraphrase-multilingual-mpnet-base-v2` model from the SentenceTransformers library.

    To run the script:

    ```bash
    ./start.sh
    ```

4. **To start the fronend:**

    To run the script:

    ```bash
    Go to the frontend folder
    Run npm ci
    Run npm run start
    ```

4. **Manually Start Docker Compose:**

    If you want to manually control Docker Compose without using `start.sh`, you can run:

    ```bash
    docker compose up --build
    ```


