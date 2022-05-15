from web3 import HTTPProvider, Web3, WebsocketProvider
from web3.middleware import geth_poa_middleware

from config import BET_ABI, CONFIG, DEI_ABI, DEI_ADDRESS, DEUS_ADDRESS, DEUS_ABI, MASTER_CHEF_ABI, REWARDER_ABI, \
    PAIR_ABI, ERC20_ABI


class NetworkApi:

    def __init__(self, rpc, rpc_http, chain_id, source_price_chain, dei_ignore_list, deus_ignore_list, usdc_address, pairs,
                 stakings, bet_address, bet_pool_ids, path_to_usdc, is_poa=False) -> None:
        self.chain_id = chain_id
        self.source_price_chain = source_price_chain
        self.dei_ignore_list = dei_ignore_list.copy()
        self.deus_ignore_list = deus_ignore_list.copy()
        self.usdc_address = usdc_address
        self.pairs = pairs
        self.stakings = stakings
        self.path_to_usdc = path_to_usdc
        self.rpc = rpc
        self.w3 = Web3(WebsocketProvider(self.rpc))
        self.rpc_http = rpc_http
        self.http_w3 = Web3(HTTPProvider(self.rpc_http))
        self.bet_address = bet_address
        self.bet_pool_ids = bet_pool_ids
        if is_poa:
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            self.http_w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.dei_contract = self.http_w3.eth.contract(DEI_ADDRESS, abi=DEI_ABI)
        self.deus_contract = self.http_w3.eth.contract(DEUS_ADDRESS, abi=DEUS_ABI)

        self.socket_dei_contract = self.w3.eth.contract(DEI_ADDRESS, abi=DEI_ABI)
        self.socket_deus_contract = self.w3.eth.contract(DEUS_ADDRESS, abi=DEUS_ABI)

    def get_source_deus_price(self):
        w3 = Web3(HTTPProvider(CONFIG[250]['rpc_http']))
        return self.get_token_price(DEUS_ADDRESS,
                                    pair_addresses=CONFIG[self.source_price_chain]['path_to_usdc'][DEUS_ADDRESS], w3=w3)

    def get_token_price(self, token_address, pair_addresses=None, w3=None):
        if not pair_addresses:
            pair_addresses = self.path_to_usdc[token_address]
        if not w3:
            w3 = self.http_w3
        price = 1
        base_address = token_address
        for pair_address in pair_addresses:
            pair = w3.eth.contract(pair_address, abi=PAIR_ABI)
            token0_address = pair.functions.token0().call()
            token1_address = pair.functions.token1().call()
            token0 = w3.eth.contract(token0_address, abi=ERC20_ABI)
            token1 = w3.eth.contract(token1_address, abi=ERC20_ABI)

            if token0_address == base_address:
                base_reserve = pair.functions.getReserves().call()[0] * 10 ** (18 - token0.functions.decimals().call())
                quote_reserve = pair.functions.getReserves().call()[1] * 10 ** (18 - token1.functions.decimals().call())
                base_address = token1_address
            else:
                base_reserve = pair.functions.getReserves().call()[1] * 10 ** (18 - token1.functions.decimals().call())
                quote_reserve = pair.functions.getReserves().call()[0] * 10 ** (18 - token0.functions.decimals().call())
                base_address = token0_address
            price *= quote_reserve / base_reserve
        return price

    def dei_total_supply(self):
        return int(self.dei_contract.functions.totalSupply().call())

    def dei_circulating_marketcap(self):
        marketcap = self.dei_total_supply()
        if self.chain_id == 250:
            marketcap -= 15 * 10 ** 6 * 10 ** 18
        for address in self.dei_ignore_list:
            marketcap -= self.dei_contract.functions.balanceOf(Web3.toChecksumAddress(address)).call()
        return int(marketcap)

    def deus_circulating_supply(self):
        total_supply = self.deus_total_supply()
        for address in self.deus_ignore_list:
            total_supply -= self.deus_contract.functions.balanceOf(Web3.toChecksumAddress(address)).call()
        return int(total_supply)

    def dei_minted_events(self, from_block):
        latest_block = self.w3.eth.block_number
        result = []
        entities = []
        size = 10000
        for i in range(from_block, latest_block + 1, size):
            entities.extend(self.socket_dei_contract.events.DEIMinted.createFilter(fromBlock=i,
                                                                            toBlock=i + size).get_all_entries())
        for ent in entities:
            result.append({
                'amount': str(ent.args.amount),
                'block': ent.blockNumber,
                'timestamp': self.w3.eth.get_block(ent.blockNumber).timestamp
            })
        return result

    def deus_total_supply(self):
        return int(self.deus_contract.functions.totalSupply().call())

    def deus_burned_events(self, from_block):
        latest_block = self.w3.eth.block_number
        result = []
        entities = []
        size = 10000
        for i in range(from_block, latest_block + 1, size):
            entities.extend(self.socket_deus_contract.events.DEUSBurned.createFilter(fromBlock=i,
                                                                              toBlock=i + size).get_all_entries())
        for ent in entities:
            result.append({
                'amount': str(ent.args.amount),
                'block': ent.blockNumber,
                'timestamp': self.w3.eth.get_block(ent.blockNumber).timestamp
            })
        return result

    def deus_dex_liquidity_for_pair(self, pair_address):
        pair = self.http_w3.eth.contract(pair_address, abi=PAIR_ABI)
        token0_address = pair.functions.token0().call()
        token1_address = pair.functions.token1().call()
        token0 = self.http_w3.eth.contract(token0_address, abi=ERC20_ABI)
        token1 = self.http_w3.eth.contract(token1_address, abi=ERC20_ABI)

        if token0_address == DEUS_ADDRESS:
            deus_reserve = pair.functions.getReserves().call()[0]
            quote_reserve = pair.functions.getReserves().call()[1] * 10 ** (18 - token1.functions.decimals().call())
            quote_address = token1_address
        else:
            deus_reserve = pair.functions.getReserves().call()[1]
            quote_reserve = pair.functions.getReserves().call()[0] * 10 ** (18 - token0.functions.decimals().call())
            quote_address = token0_address
        return int(deus_reserve * self.get_source_deus_price() + quote_reserve * self.get_token_price(quote_address))

    def dei_dex_liquidity_for_pair(self, pair_address):
        pair = self.http_w3.eth.contract(pair_address, abi=PAIR_ABI)
        token0_address = pair.functions.token0().call()
        token1_address = pair.functions.token1().call()
        token0 = self.http_w3.eth.contract(token0_address, abi=ERC20_ABI)
        token1 = self.http_w3.eth.contract(token1_address, abi=ERC20_ABI)

        if token0_address == DEI_ADDRESS:
            dei_reserve = pair.functions.getReserves().call()[0]
            quote_reserve = pair.functions.getReserves().call()[1] * 10 ** (18 - token1.functions.decimals().call())
            quote_address = token1_address
        else:
            dei_reserve = pair.functions.getReserves().call()[1]
            quote_reserve = pair.functions.getReserves().call()[0] * 10 ** (18 - token0.functions.decimals().call())
            quote_address = token0_address
        return int(dei_reserve + quote_reserve * self.get_token_price(quote_address))

    def dei_dex_liquidity_for_pair_bet(self, bet_address, pool_id):
        bet = self.http_w3.eth.contract(bet_address, abi=BET_ABI)
        data = bet.functions.getPoolTokens(pool_id).call()
        token0_address = data[0][0]
        token1_address = data[0][1]
        token0 = self.http_w3.eth.contract(token0_address, abi=ERC20_ABI)
        token1 = self.http_w3.eth.contract(token1_address, abi=ERC20_ABI)

        if token0_address == DEI_ADDRESS:
            dei_reserve = data[1][0]
            quote_reserve = data[1][1] * 10 ** (18 - token1.functions.decimals().call())
            quote_address = token1_address
        else:
            dei_reserve = data[1][1]
            quote_reserve = data[1][0] * 10 ** (18 - token0.functions.decimals().call())
            quote_address = token0_address
        return int(dei_reserve + quote_reserve * self.get_token_price(quote_address))

    def lp_total_supply(self, pair_address):
        pair = self.http_w3.eth.contract(pair_address, abi=PAIR_ABI)
        return int(pair.functions.totalSupply().call())

    def staking_lp_balance(self, pair_address, staking_address):
        pair = self.http_w3.eth.contract(pair_address, abi=PAIR_ABI)
        return int(pair.functions.balanceOf(staking_address).call())

    def staked_deus_liquidity(self):
        res = 0
        for token_name, staking_address in self.stakings['deus'].items():
            pair_address = self.pairs['deus'][token_name]
            lp_price = self.deus_dex_liquidity_for_pair(pair_address) / self.lp_total_supply(pair_address)
            res += self.staking_lp_balance(pair_address, staking_address) * lp_price
        return int(res)

    def staked_dei_liquidity(self):
        res = 0
        for token_name, staking_address in self.stakings['dei'].items():
            pair_address = self.pairs['dei'][token_name]
            lp_price = self.dei_dex_liquidity_for_pair(pair_address) / self.lp_total_supply(pair_address)
            res += self.staking_lp_balance(pair_address, staking_address) * lp_price
        return int(res)

    def deus_dex_liquidity(self):
        res = 0
        for pair_name, pair_address in self.pairs['deus'].items():
            res += self.deus_dex_liquidity_for_pair(pair_address)
        return int(res)

    def dei_dex_liquidity(self):
        res = 0
        for pair_name, pair_address in self.pairs['dei'].items():
            res += self.dei_dex_liquidity_for_pair(pair_address)

        if self.bet_pool_ids:
            for pair_name, pool_id in self.bet_pool_ids['dei'].items():
                res += self.dei_dex_liquidity_for_pair_bet(self.bet_address, pool_id)
        return int(res)

    def deus_emissions(self):
        # master_chef_contract = self.w3.eth.contract(CONFIG[self.chain_id]['master_chef'], abi=MASTER_CHEF_ABI)
        # total_alloc = 0
        # total_emission = 0
        # data = []
        # for pid in [36, 37]:
        #     rewarder = master_chef_contract.functions.rewarder(pid).call()
        #     rewarder_contract = self.w3.eth.contract(rewarder, abi=REWARDER_ABI)
        #     token_per_block = rewarder_contract.functions.rewardPerBlock().call() / 10 ** 18
        #     alloc_point = rewarder_contract.functions.poolInfo(pid).call()[2]
        #     total_alloc += alloc_point
        #     data += [(alloc_point, token_per_block)]

        # for d in data:
        #     total_emission += (d[0] / total_alloc) * d[1]
        # return total_emission
        master_chef_contract = self.http_w3.eth.contract(CONFIG[self.chain_id]['master_chef'], abi=MASTER_CHEF_ABI)
        total_emission = 0
        rewarders = set()
        for pid in [36, 37]:
            rewarder = master_chef_contract.functions.rewarder(pid).call()
            rewarders.add(rewarder)
        for rewarder in rewarders:
            rewarder_contract = self.http_w3.eth.contract(rewarder, abi=REWARDER_ABI)
            token_per_block = rewarder_contract.functions.tokenPerBlock().call()
            total_emission += token_per_block
        return total_emission
