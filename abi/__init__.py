import json
import os
import pathlib


def get_path(file_name):
    return os.path.join(str(pathlib.Path(__file__).parent), file_name)


with open(get_path('dei.json'), 'r') as abi_file:
    DEI_ABI = json.load(abi_file)

with open(get_path('deus.json'), 'r') as abi_file:
    DEUS_ABI = json.load(abi_file)

with open(get_path('beet.json'), 'r') as abi_file:
    BEET_ABI = json.load(abi_file)

with open(get_path('dei_usdc_lending.json'), 'r') as abi_file:
    DEI_USDC_LINDING_ABI = json.load(abi_file)

with open(get_path('deus_dei_lending.json'), 'r') as abi_file:
    DEUS_DEI_LENDING_ABI = json.load(abi_file)

with open(get_path('erc20.json'), 'r') as abi_file:
    ERC20_ABI = json.load(abi_file)

with open(get_path('master_chef.json'), 'r') as abi_file:
    MASTER_CHEF_ABI = json.load(abi_file)

with open(get_path('rewarder.json'), 'r') as abi_file:
    REWARDER_ABI = json.load(abi_file)

with open(get_path('solidly_router.json'), 'r') as abi_file:
    SOLIDLY_ROUTER_ABI = json.load(abi_file)

with open(get_path('uni_pair.json'), 'r') as abi_file:
    PAIR_ABI = json.load(abi_file)
