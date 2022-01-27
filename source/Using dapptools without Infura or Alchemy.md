# Using dapptools without Infura or Alchemy

To interact with the Ethereum blockchain, you naturally need some tooling. E.g. you can use something like [seth](https://github.com/dapphub/dapptools/blob/master/src/seth/README.md) to send ether (among many other things):

```
seth send --value 1 0xfB6916095ca1df60bB79Ce92cE3Ea74c37c5d359
```

`seth` is part of [dapptools](https://dapp.tools/), a nice suite of CLI tools that allow you to do pretty much everything from make calls to existing smart contracts to develop and deploy new smart contracts on the Ethereum blockchain.

However, these tools need a way to "talk" to the Ethereum blockchain. The easiest and quickest way to get started is to use either the [Infura](https://infura.io) or [Alchemy](https://www.alchemy.com/) services. After signing up, it's as simple as setting the `ETH_RPC_URL` environment variable, e.g.

```
export ETH_RPC_URL=https://mainnet.infura.io/v3/<YOUR API KEY>
```
and running your command. However, using these two API services means your access to Ethereum, which is foundationally a decentralized platform, is gated by one of two *centralized services*. A bit of irony.

This was noted recently by Moxie Marlinespike on his [blog](https://moxie.org/2022/01/07/web3-first-impressions.html):

>  Almost all dApps use either Infura or Alchemy in order to interact with the blockchain. In fact, even when you connect a wallet like MetaMask to a dApp, and the dApp interacts with the blockchain via your wallet, MetaMask is just making calls to Infura!

> These client APIs are not using anything to verify blockchain state or the authenticity of responses. The results aren’t even signed...

> This was surprising to me. So much work, energy, and time has gone into creating a trustless distributed consensus mechanism, but virtually all clients that wish to access it do so by simply trusting the outputs from these two companies without any further verification.

You may be happy to learn however, that while using these services is the path of least resistance to getting started, it's not really that difficult to actually connect to the blockchain directly, using an Ethereum [light client](https://medium.com/@rauljordan/a-primer-on-ethereum-blockchain-light-clients-f3cadde49137).

The first thing you'll need to do is install [geth](https://geth.ethereum.org/docs/install-and-build/installing-geth). You can run a full node with this tool if you want, but you will need some serious resources!

We're just going to run a light client to give us accesss to Ethereum directly. Once `geth` is installed, you'll need to start it with the following command:

```
geth --http --syncmode "light"
```

The above starts `geth` in light sync mode. The `--http` option enables the HTTP-RPC listener. This is necessary for giving access to your tools like `seth`.

The first time you run your light node, you will likely need to wait a bit while it discovers peers and does some syncing. I think I waited around 15 minutes or so before I was able to use it, but you may need to wait a bit longer. You'll know when your commands work.

Once your `geth` node is in a good sync state, you set `ETH_RPC_URL` (or equivalent) to your locally running node:

```
export ETH_RPC_URL=http://localhost:8545
```

(The port `8545` is the default, but you may change this as necessary.)

Now, you're free to use your tools just like you would with Infura or Alchemy, but with a more direct connection into Ethereum.