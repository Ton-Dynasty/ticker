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

4. Copy `.env.example` to a `.env` file and fill in the required fields

    Hint: get "TESTNET" ton center api key from [telegram bot](https://t.me/tonapibot)

    ```bash
    cp .env.example .env
    ```

5. Start the docker container

    ```bash
    docker compose up -d
    ```

6. Create virtual environment

    ```bash
    python3 -m venv venv
    ```

7. Activate virtual environment

    - Windows

        ```bash
        venv\Scripts\activate
        ```

    - Mac / Linux

        ```bash
        source venv/bin/activate
        ```

8. Install requirements

    ```bash
    pip install -r requirements.txt
    ```

9. Periodically get free TON from [this bot](https://t.me/testgiver_ton_bot)

10. Go to [this app](https://t.me/TicTonOracleBot) and get some free USDT 

11.  Run the script

    ```bash
    python main.py
    ```
