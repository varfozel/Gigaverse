import time
import requests
import random
import struct
import signer
import sys

from web3 import Web3

from loguru import logger

logger.remove()
logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")

headers = {
    'accept': '*/*',
    'accept-language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
    'authorization': 'Bearer',
    'content-type': 'application/json',
    'origin': 'https://gigaverse.io',
    'priority': 'u=1, i',
    'referer': 'https://gigaverse.io/play',
    'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
}


def get_token(private_key, wallet_address):
    logger.info("Signing message and requesting JWT...")
    signature, address, timestamp = signer.main(private_key)

    url = 'https://gigaverse.io/api/user/auth'
    data = {
        'address': wallet_address,
        'message': f'Login to Gigaverse at {timestamp}',
        'signature': signature,
        'timestamp': timestamp
    }

    headers1 = {
        "accept": "*/*",
        "content-type": "application/json",
        "origin": "https://gigaverse.io",
        "referer": "https://gigaverse.io/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
    }

    response = requests.post(url, json=data, headers=headers1)
    if response.status_code == 200:
        jwt = response.json()['jwt']
        logger.success("JWT obtained successfully")
        return jwt
    else:
        logger.error(f'Error getting JWT: {response.status_code}, {response.text}')
        return None

def start_game():
    logger.info("Starting new run...")
    json_data = {
        'action': 'start_run',
        'actionToken': '',
        'dungeonId': 1,
        'data': {
            'consumables': [],
            'itemId': 0,
            'index': 0,
            'isJuiced': False,
            'gearInstanceIds': [],
        },
    }

    response = requests.post('https://gigaverse.io/api/game/dungeon/action', headers=headers, json=json_data)
    if response.status_code == 200:
        data = response.json()
        logger.success("Run started successfully")
        return data['actionToken']
    else:
        logger.error(f'Error starting run: {response.status_code}, {response.json()}')

def action_claim_reward(action_token):
    logger.info("Getting loot...")
    json_data = {
        'action': 'loot_one',
        'actionToken': action_token,
        'dungeonId': 0,
        'data': {
            'consumables': [],
            'itemId': 0,
            'index': 0,
            'isJuiced': False,
            'gearInstanceIds': [],
        },
    }

    response = requests.post('https://gigaverse.io/api/game/dungeon/action', headers=headers, json=json_data)
    if response.status_code == 200:
        data = response.json()
        logger.success("Loot obtained")
        return data['actionToken']
    else:
        logger.error(f'Error getting loot: {response.status_code}, {response.json()}')

def action(action_token, charges):
    available_actions = [move for move, charge in charges.items() if charge > 0]
    if not available_actions:
        logger.warning("No available actions!")
        return None, charges

    action = 'rock' if 'rock' in available_actions else random.choice(available_actions)
    logger.info(f'Selected move: {action}')

    json_data = {
        'action': action,
        'actionToken': action_token,
        'dungeonId': 0,
        'data': {
            'consumables': [],
            'itemId': 0,
            'index': 0,
            'isJuiced': False,
            'gearInstanceIds': [],
        },
    }

    response = requests.post('https://gigaverse.io/api/game/dungeon/action', headers=headers, json=json_data)
    if response.status_code == 200:
        data = response.json()
        room_num = data['data']['entity']['ROOM_NUM_CID']
        logger.info(f'Battle in room #{room_num}')

        player = data['data']['run']['players'][0]
        charges = {
            'rock': player['rock']['currentCharges'],
            'paper': player['paper']['currentCharges'],
            'scissor': player['scissor']['currentCharges'],
        }

        if data['data']['run'].get('lootPhase'):
            logger.info('Loot phase - choosing reward')
            action_token = action_claim_reward(data['actionToken'])
            return action_token, charges

        if player['health']['current'] == 0:
            logger.info('Player died. Game over.')
            return None, charges

        return data['actionToken'], charges
    else:
        logger.error(f'Error during move: {response.status_code}, {response.json()}')
        return None, charges

def main():
    for i in range(10):
        time.sleep(5)
        acctoken = start_game()
        if acctoken:
            charges = {'rock': 3, 'paper': 3, 'scissor': 3}
            while True:
                time.sleep(2)
                action_token, new_charges = action(acctoken, charges)
                if action_token:
                    acctoken = action_token
                    charges = new_charges
                else:
                    logger.info('Run completed')
                    break
        else:
            logger.error('Failed to start run')
            break

if __name__ == '__main__':
    private_key = ''
    wallet_address = ''
    jwt_token = get_token(private_key, wallet_address)
    if jwt_token:
        headers["authorization"] = f"Bearer {jwt_token}"
        logger.success("JWT saved in headers")
        main()
    else:
        logger.error("Failed to authenticate, terminating program.")
