import { createAbstractClient } from '@abstract-foundation/agw-client'
import { http } from 'viem'
import { privateKeyToAccount } from 'viem/accounts'

const privateKey = process.env.PRIVATE_KEY.startsWith('0x') 
    ? process.env.PRIVATE_KEY 
    : `0x${process.env.PRIVATE_KEY}`
const timestamp = Date.now()
const message = `Login to Gigaverse at ${timestamp}`

async function main() {
  const account = privateKeyToAccount(privateKey)

  const client = await createAbstractClient({
    signer: account,
    chain: {
      id: 2741,
      name: "Ethereum",
      nativeCurrency: { name: "Ether", decimals: 18, symbol: "ETH" },
      rpcUrls: {
        default: {
          http: ['https://black-cosmological-telescope.abstract-mainnet.quiknode.pro/95f85c3082343bca95b16601b725dfce145f95c1/'],
        }
      }
    },
    transport: http()
  })

  const signature = await client.signMessage({ message })
  console.log(JSON.stringify({
    message,
    timestamp,
    signature,
    address: account.address
  }))
}

main()
