# Can you get rugged by RocketPool?

[RocketPool](https://rocketpool.net) is a very cool "decentralized ethereum staking protocol" that lets you participate in the new Proof-of-Stake Ethereum consensus model using any amount of ETH you have. Ordinarily, [to stake](https://ethereum.org/en/staking) you'd need to have 32 ETH to deposit. RocketPool is a great concept, and a way to earn on your ETH while HODLing.

But, like all great ideas in crypto, you have to ask yourself... are my funds safe?

And in the case of RocketPool, the answer is... maybe? You see, there is a bit of a problem with how they deployed their contract, and how the balances of rETH and ETH in the contract are stored.

RocketPool uses the [RocketStorage](https://etherscan.io/address/0x1d8f8f00cfa6758d7be78336684788fb0ee0fa46#code) contract to manage many different values in the protocol. RocketStorage is basically a generic "dictionary" implementation where you pre-compute a key and then can use that to set and get a value, e.g. `setUint` or `getBool`.

The balances for rETH and ETH are each stored in this dictionary using a single key. This means that with one call, a single entity can change the entire supply value for either. So now, the question becomes, who can actually make these calls? Surely the on-chain contracts, and if we knew it was restricted to ONLY the on-chain contracts, I think it would be fine. However, it **is not** clear that access is restricted to just the on-chain contracts.

Here's the deep dive.

To get the exchange rate for `rETH / ETH` you can call `getExchangeRate()`.

```jsx
export RocketTokenRETH=0xae78736Cd615f374D3085123A210448E74Fc6393
cast call $RocketTokenRETH 'getExchangeRate()(uint256)'

1025543653492495115       # 1.0255...
```

This in turn calls [getEthValue(1 ether)](https://etherscan.io/address/0xae78736Cd615f374D3085123A210448E74Fc6393#code#F6#L93).

In [getEthValue()](https://etherscan.io/address/0xae78736Cd615f374D3085123A210448E74Fc6393#code#F6#L65), for `1 ether`, the exchange rate is determined by the following formula:

```jsx
1 ether * ETH supply / rETH supply
```

The `ETH` and `rETH` balances are gotten from the [RocketNetworkBalances](https://etherscan.io/address/0x138313f102ce9a0662f826fca977e3ab4d6e5539#code) contract, which in turn queries the [RocketStorage](https://etherscan.io/address/0x1d8f8f00cfa6758d7be78336684788fb0ee0fa46#code) contract. This is where things begin to get a bit questionable.

As we said, RocketStorage is a generic "dictionary" like contract, where for any `bytes32` key you can get or set a particular value type, e.g. `setUint` or `getUint`. The caller computes the key before setting a value.


For instance to [getTotalRETHSupply()](https://etherscan.io/address/0x138313f102ce9a0662f826fca977e3ab4d6e5539#code#F3#L79) the RocketNetworkBalances contract is really just calling

```jsx
rocketStorage.getUint(keccak256("network.balance.reth.supply"));
```

Reading the values isn’t the problem. That’s public and accessible, as expected. However, you can also do

```jsx
setUint(keccak256("network.balance.reth.supply"), _value);
```

But _who_ can `setUint()`?

In `RocketStorage` the `setUint` function is protected by the [onlyLatestRocketNetworkContract](https://etherscan.io/address/0x1d8f8f00cfa6758d7be78336684788fb0ee0fa46#code#F2#L220) modifier. However, this is also just [consulting the internal dictionary](https://etherscan.io/address/0x1d8f8f00cfa6758d7be78336684788fb0ee0fa46#code#F2#L70) for boolean values to see if the following key is present and true:

```jsx
require(booleanStorage[keccak256(abi.encodePacked("contract.exists", msg.sender))],
    "Invalid or outdated network contract");
```

This implies that at one point someone had to call `RocketStorage.setBool()` with the string `"contract.exists"` + `some address`. That address is then allowed to modify values in the `RocketStorage` dictionary.

Values in `RocketStorage` can be set by the [guardian](https://etherscan.io/address/0x0ccf14983364a7735d369879603930afe10df21e) (the contract that deployed the contract) up until [setDeployedStatus()](https://etherscan.io/address/0x1d8f8f00cfa6758d7be78336684788fb0ee0fa46#code#F2#L120) is called. Once that has been called, permissions are locked on the dictionary. However, up _until_ this function is called, any number of settings can be jabbed into the dictionary, **including who is allowed to read and write values via the `onlyLatestRocketNetworkContract` modifier.**

When `RocketStorage` was deployed there were [many values set by the guardian](https://etherscan.io/txs?a=0x1d8f8f00cfa6758d7be78336684788fb0ee0fa46&p=33) (deployer), including multiple `setBool` values. Because the dictionary key is pre-computed, it is opaque — so you really have no idea what values were set. This includes the values that apply to the `onlyLatestRocketNetworkContract` modifier.

**Put another way: during this initial deployment period, we have no idea what addresses may have been given write access to `RocketStorage` that would allow later modifications to things like the rETH supply.** 

### (Hopefully fictional) attack scenario

1. During RocketStorage setup, before calling `setDeployedStatus()`, `guardian` made the following call:
    1. `setBool(keccak256(abi.encodePacked("contract.exists", some_secret_address), true)`
    2. We have no way of knowing what this `setBool` call was setting from the txn history, since all we see is the [computed key](https://etherscan.io/tx/0xff6d158033960e115f77765d7ef59caca9180f411f3f65a660999b82088c3e7e), which is a sha3 hash.
2. In the future, let’s say the exchange rate for `rETH / ETH` is `1.0255`. Everything looks reasonable.
    1. Remember, the rate is computed from the ETH and rETH balances like:
`90348716875500680014984 / 88098362822311442527161` = `1.0255`
3. Since `some_secret_address` can call `setUint` directly on `RocketStorage`, the attacker can change the rETH balance and modify the exchange rate from, say, `1.0255` to `10.255`... e.g. by simply deleting a single decimal:
`90348716875500680014984 / 8809836282231144252716` = `10.255`

This means that an insider could potentially modify the rETH supply, swap out their rETH for ETH, and `profit$$`.

### Opaqueness is not your friend

So why did RocketPool decide to proceed in this manner? Hard to say, maybe just because it was convenient, perhaps not due to any nefarious motive.

However, it's impossible to tell without reversing all the `setBool` calls that preceded `setDeployedStatus()`. Some rando on the [RocketPool discord](https://discord.com/channels/405159462932971535/857072928155762718/906669684294823946) claims to have done this, and even offered to provide a list on request.

Interestingly, however, RocketPool seemed pretty mum on the whole conversation, and it raises the question: why should users have to try and validate anything here? RocketPool is the one who needs to build trust. So if all those `setBool()` calls were aboveboard, why don't they publish a list verifying the calls?


