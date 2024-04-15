# Python Script for SOL/BOME token DEX

This project is aim to implement simple DEX functionality of Solana network.
main functionality of swap is originated from raydium.io-sdk library.
Functionalities are follows:

1. Swap BOME token from SOL token and vice versa on Raydium SDK.
2. Add and Remove Liquidity to BOME/SOL Liquidity.
3. Output each method result as a csv format.

## Configuration of development environment

### Pre requirements

This app is runnning on python version 3.11.x or higher.
please make sure your python version before launch this app.

```bash
python --version
```

### Steps to launch app

1. clone project from github.

```bash
git clone
```

2. create virtual environment

```bash
python -m venv bot
```

If this command not works then you need to install venv module globally and activate your environment.

```bash
pip install virtualenv

source bot/Scripts/activate  # For Linux/macOS
./bot/Scripts/activate       # For Windows
```

3. install requirements.

```bash
pip install -r requirements.txt
```

4. launch app.

```bash
python main.py
```

## Functions of Each method

As you can see the screenshot, there are 5 main functions.
you can check prototype and parameters simply by typing `help <command_name>`

- Help

  This function helps you to get information each functions.

- Wallet information

  This function helps you to get information of desired wallet.

  - `wallet`: public key of wallet to get info

- Swap SOL to BOME

  This function helps you to swap SOL token to BOME token.

  - `wallet`: private key of wallet to swap.
  - `amount`: amount of SOL to swap.
  - `percent`: slippage of token swap.

- Swap BOME to SOL

  This function helps you to swap BOME token to SOL token.

  - `wallet`: private key of wallet to swap.
  - `amount`: amount of SOL to swap.
  - `percent`: slippage of token swap.

- Add Liquidity

  This function helps you to add liquidity to SOL/BOME liquidity pool.

  - `wallet`: private key of wallet.
  - `amount`: amount of SOL to add to liquidity.

- Remove Liquidity

  This function helps you to remove liquidity to SOL/BOME liquidity pool.

  - `wallet`: private key of wallet.
  - `amount`: amount of LP token to remove from liquidity.
