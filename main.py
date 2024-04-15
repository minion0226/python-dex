import os
import cmd
import csv
import time
import pytz
import requests
import argparse
import threading
from datetime import datetime

api_url = 'https://solbot-j0a6.onrender.com/api/'

class BomeDEXShell(cmd.Cmd):
  intro = """
    ***************************************************
    *                                                 *
    *            WELCOME TO SIMPLE BOME DEX           *
    *                                                 *
    *       ╭━━╮╭━━━┳━╮╭━┳━━━╮╱╱╱╱╭━━━┳━━━┳╮          *
    *       ┃╭╮┃┃╭━╮┃┃╰╯┃┃╭━━╯╱╱╱╱┃╭━╮┃╭━╮┃┃          *
    *       ┃╰╯╰┫┃╱┃┃╭╮╭╮┃╰━━╮╱╱╱╱┃╰━━┫┃╱┃┃┃          *
    *       ┃╭━╮┃┃╱┃┃┃┃┃┃┃╭━━╯╭━━╮╰━━╮┃┃╱┃┃┃╱╭╮       *
    *       ┃╰━╯┃╰━╯┃┃┃┃┃┃╰━━╮╰━━╯┃╰━╯┃╰━╯┃╰━╯┃       *
    *       ╰━━━┻━━━┻╯╰╯╰┻━━━╯╱╱╱╱╰━━━┻━━━┻━━━╯       *
    *                                                 *
    *  wallet_info <wallet>                           *
    *  swap_bome <wallet> <amount> <percent>          *
    *  swap_sol <wallet> <amount> <percent>           *
    *  add_liquidity <wallet> <amount>                *
    *  remove_liquidity <wallet> <amount>             *
    *                                                 *
    *  if you need some help, please type             *
    *  help <command_name>                            *
    *                                                 *
    ***************************************************
  """
  prompt = "> "
  
  def __init__(self):
    super().__init__()
    self.loading_thread = None
    self.loading_active = False

  def start_loading_animation(self):
    self.loading_active = True
    self.loading_thread = threading.Thread(target=self.loading_animation)
    self.loading_thread.start()

  def stop_loading_animation(self):
    self.loading_active = False
    if self.loading_thread:
      self.loading_thread.join()

  def loading_animation(self):
    while self.loading_active:
      for char in "|/-\\":
        print(f"\rProcessing command... {char}", end="")
        time.sleep(0.1)
    print('\n')
  
  def validate_wallet_address(self, address):
    if len(address) != 88:  # Assuming wallet addresses are 88 characters long
      raise argparse.ArgumentTypeError("Wallet address must be 88 characters long")
    return address

  def do_wallet_info(self, arg):
    """
    Get informations for wallet secret key. 
    wallet_info <wallet>
    """
    self.start_loading_animation()
    
    try:
      parser = argparse.ArgumentParser(description="Get information for wallet")
      parser.add_argument("wallet", help="Wallet address")
      
      args = parser.parse_args(arg.split())
      response = requests.post(api_url + 'account-info', json={ 'publicKey': args.wallet })
      
      if response.status_code == 200:
        data = response.json()
        if data.get('success') == True:
          extracted_data = [{"mint": item["accountInfo"]["mint"], "amount": item["accountInfo"]["amount"]} for item in data.get('walletTokenAccount')]
          
          for item in extracted_data:
            mint = item.get('mint')
            amount_int = int(item.get('amount'), 16)

            if mint == 'So11111111111111111111111111111111111111112':
              item['mint'] = 'SOL'
              item["amount"] = amount_int / (10 ** 9)
            elif mint == 'ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82':
              item['mint'] = 'BOME'
              item['amount'] = amount_int / (10 ** 6)
            elif mint == '83WevmL2JzaEvDmuJUFMxcFNnHqP4xonfvAzKmsPWjwu':
              item['mint'] = 'BOME-SOL'
              item['amount'] = amount_int / (10 ** 6)
            else:
              item['mint'] = 'Unknown'
              item["amount"] = amount_int / (10 ** 6)
              
          lamport = data.get('accountInfo').get('value').get('lamports') / 1e9
          extracted_data.append({
            'mint': 'SOL',
            'amount': lamport
          })
          print('\naccount information:')
          
          for item in extracted_data:
              print("Token:", item['mint'], "\tAmount:", item['amount'])
        else:
          print('\nCould not get data from server.\n')
      else:
        print('\ncould not get information.\n')
    except Exception as e:
      print('\nException: ', e, '\n')
      
    self.stop_loading_animation()

  def do_swap_bome(self, arg):
    """
    Swap BOME tokens. 
    swap_bome <wallet> <amount> <percent>
    """
    self.start_loading_animation()
    
    # Parse arguments and perform swap_bome operation
    try:
      parser = argparse.ArgumentParser(description="Swap BOME to SOL")
      parser.add_argument("wallet", type=self.validate_wallet_address, help="Wallet address")
      parser.add_argument("amount", type=float, help="Amount of BOME tokens to swap")
      parser.add_argument("percent", type=int, help="Percent")
      
      args = parser.parse_args(arg.split())
      
      response = requests.post(api_url + 'swap-amm', json={ 'secretKey': args.wallet, 'amount': args.amount, 'percent': args.percent, 'solToBome': True})
      if response.status_code == 200:
        swap_info = response.json()
        if swap_info and swap_info.get('success'):
          transaction_ids = swap_info.get('txIds', [])
          estimation = swap_info.get('estimation', {})
          num = int(estimation.get('numerator', '0'), 16)
          den = int(estimation.get('denominator', '0'), 16)
          estiVal = num / den

          resp = requests.post(api_url + 'transaction-info', json={'ids': transaction_ids})
          if resp.status_code == 200:
            trans_info = resp.json()
            detail = trans_info.get('detail', [])
            if detail[0]:
              status = 'success'
              message = '\nSuccess to swap: \n{}'.format(detail[0])
            else:
              status = 'fail'
              message = '\nFailed to swap\n{}'.format(transaction_ids)
            print(message)
          else:
            print("Error fetching transaction info:", resp.status_code)
            status = 'fail'

          data = [
            datetime.now(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'swap_bome',
            ', '.join(transaction_ids),
            estiVal,
            args.amount,
            status
          ]
          self.update_log('logs', data)
        else:
          print("Error in swap operation:", swap_info.get('error', 'Unknown error'))
      else:
        print("Error in swap operation:", response.status_code)

    except argparse.ArgumentError as e:
      print("Error parsing arguments:", e)
      
    self.stop_loading_animation()

  def do_swap_sol(self, arg):
    """
    Swap SOL tokens.
    swap_sol <wallet> <amount> <percent>
    """
    # Parse arguments and perform swap_sol operation
    self.start_loading_animation()
    
    # Parse arguments and perform swap_bome operation
    try:
      parser = argparse.ArgumentParser(description="Swap BOME to SOL")
      parser.add_argument("wallet", type=self.validate_wallet_address, help="Wallet address")
      parser.add_argument("amount", type=float, help="Amount of BOME tokens to swap")
      parser.add_argument("percent", type=int, help="Percent")
      
      args = parser.parse_args(arg.split())
      
      response = requests.post(api_url + 'swap-amm', json={ 'secretKey': args.wallet, 'amount': args.amount, 'percent': args.percent, 'solToBome': False})
      if response.status_code == 200:
        swap_info = response.json()
        if swap_info and swap_info.get('success'):
          transaction_ids = swap_info.get('txIds', [])
          estimation = swap_info.get('estimation', {})
          num = int(estimation.get('numerator', '0'), 16)
          den = int(estimation.get('denominator', '0'), 16)
          estiVal = num / den

          resp = requests.post(api_url + 'transaction-info', json={'ids': transaction_ids})
          if resp.status_code == 200:
            trans_info = resp.json()
            detail = trans_info.get('detail', [])
            if detail[0]:
              status = 'success'
              message = '\nSuccess to swap: \n{}'.format(detail[0])
            else:
              status = 'fail'
              message = '\nFailed to swap\n{}'.format(transaction_ids)
            print(message)
          else:
            print("Error fetching transaction info:", resp.status_code)
            status = 'fail'

          data = [
            datetime.now(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'swap_sol',
            ', '.join(transaction_ids),
            estiVal,
            args.amount,
            status
          ]
          print('logs',data)
          self.update_log('logs', data)
        else:
          print("Error in swap operation:", swap_info.get('error', 'Unknown error'))
      else:
        print("Error in swap operation:", response.status_code)

    except argparse.ArgumentError as e:
      print("Error parsing arguments:", e)
      
    self.stop_loading_animation()

  def do_add_liquidity(self, arg):
    """
    Add liquidity.
    add_liquidity <wallet> <amount>
    """
    self.start_loading_animation()
    
    # Parse arguments and perform add_liquidity operation
    try:
      parser = argparse.ArgumentParser(description="Add liquidity to pool")
      parser.add_argument("wallet", type=self.validate_wallet_address, help="Wallet address")
      parser.add_argument("amount", type=float, help="Amount of SOL token to add liquidity.")
      
      args = parser.parse_args(arg.split())
      response = requests.post(api_url + 'add-liquidity', json={ 'secretKey': args.wallet, 'amount': args.amount })
      if response.status_code == 200:
        parsed = response.json()
        
        amount = parsed.get('liquidityD', '0')
        txid = parsed.get('txids', [])

        self.update_log('logs', [
          datetime.now(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
          'add_liquidity',
          ', '.join(txid),
          args.amount,
          amount,
          'success' if parsed.get('success') else 'fail'
        ])
      else:
        print('Error Response:', response.status_code)
    except Exception as e:
      print('Error: ', e)
      
    self.stop_loading_animation()
    
  def do_remove_liquidity(self, arg):
    """
    Remove liquidity.
    remove_liquidity <wallet> <amount>
    """
    self.start_loading_animation()
    
    try:
      # Parse arguments and perform remove_liquidity operation
      parser = argparse.ArgumentParser(description="Add liquidity to pool")
      parser.add_argument("wallet", type=self.validate_wallet_address, help="Wallet address")
      parser.add_argument("amount", type=float, help="Amount of SOL token to add liquidity.")
      
      args = parser.parse_args(arg.split())
      response = requests.post(api_url + 'remove-liquidity', json={ 'secretKey': args.wallet, 'amount': args.amount })
      if response.status_code == 200:
        parsed = response.json()
        
        txid = parsed.get('txids', [])

        self.update_log('logs', [
          datetime.now(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
          'remove_liquidity',
          ', '.join(txid),
          args.amount,
          args.amount,
          'success' if parsed.get('success') else 'fail'
        ])
      else:
        print('Error', response.status_code)
    except Exception as e:
      print('Error: ', e)
    
    self.stop_loading_animation()

  def update_log(self, filename, row):
    header = ['date', 'type', 'transaction_id', 'estimate_value', 'real_value', 'status']

    try:
      if not os.path.isfile(filename + '.csv'):
        # If the file doesn't exist, write the header
        with open(filename + '.csv', mode='w', newline='') as file:
          writer = csv.writer(file)
          writer.writerow(header)
          
      with open(filename + '.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)

      print('log saved to csv flie.')
    except Exception as e:
      print('fail to save to csv file')
  
  def do_exit(self, arg):
    """
    Exit the program.
    """
    return True

if __name__ == '__main__':  
  BomeDEXShell().cmdloop()