import { useState } from 'react'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { useWebSocket } from '../contexts/WebSocketContext'

export function BundlerControls() {
  const [tokenAddress, setTokenAddress] = useState('')
  const { sendMessage, connected } = useWebSocket()

  const handleBundledBuy = () => {
    if (!tokenAddress) return

    sendMessage({
      type: 'start_bundled_buy',
      token_address: tokenAddress
    })
  }

  const handleIncrementalSell = () => {
    if (!tokenAddress) return

    sendMessage({
      type: 'start_incremental_sell',
      token_address: tokenAddress
    })
  }

  const handleStopBundler = () => {
    sendMessage({
      type: 'stop_bundler'
    })
  }

  return (
    <div className="space-y-4">
      <div>
        <Label>Token Address</Label>
        <Input
          placeholder="Enter token address"
          value={tokenAddress}
          onChange={(e) => setTokenAddress(e.target.value)}
        />
      </div>
      <div className="space-y-2">
        <Button
          className="w-full"
          onClick={handleBundledBuy}
          disabled={!connected || !tokenAddress}
        >
          Execute Bundled Buy
        </Button>
        <Button
          variant="outline"
          className="w-full"
          onClick={handleIncrementalSell}
          disabled={!connected || !tokenAddress}
        >
          Start Incremental Sell
        </Button>
        <Button
          variant="secondary"
          className="w-full bg-red-100 hover:bg-red-200 text-red-600"
          onClick={handleStopBundler}
          disabled={!connected}
        >
          Stop Bundler
        </Button>
      </div>
    </div>
  )
}
