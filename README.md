# TICKER 

Farming TIC tokens from TIC TON oracle with no risk & effort.

## Setup

1. Install docker desktop
   
    [This](https://docs.docker.com/desktop/) website provides instructions for installing docker desktop on your machine. 
    
2. Install Python

3. Clone this repo

    ```bash
    git clone https://github.com/alan890104/ticker.git
    ```

4. Start the docker container

    ```bash
    docker compose up -d
    ```

5. Create virtual environment

    ```bash
    python3 -m venv venv
    ```

6. Activate virtual environment

    - Windows

        ```bash
        venv\Scripts\activate
        ```

    - Mac / Linux

        ```bash
        source venv/bin/activate
        ```

7. Install requirements

    ```bash
    pip install -r requirements.txt
    ```

8. Copy `.env.example` to a `.env` file and fill in the required fields

    ```bash
    cp .env.example .env
    ```

9.  Run the script

    ```bash
    python main.py
    ```
