import { LineChart, XAxis, YAxis, Tooltip, Line } from 'recharts'
import { Activity, Wallet, Settings } from 'lucide-react'
import { Card, CardHeader, CardContent } from './components/ui/card'
import { Button } from './components/ui/button'
import { ConfigPanel } from './components/ConfigPanel'
import { useWebSocket } from './contexts/WebSocketContext'
import { useTradeData } from './hooks/useTradeData'
import { useState } from 'react'

export default function App() {
  const { connected, sendMessage } = useWebSocket()
  const { trades, totalBalance, totalProfitLoss, activeWallets } = useTradeData()
  const [tradingMode, setTradingMode] = useState('normal')

  const chartData = trades.map(trade => ({
    time: new Date(trade.timestamp).toLocaleTimeString(),
    price: trade.price
  }))

  const handleStartTrading = () => {
    sendMessage({ type: 'start_trading', mode: tradingMode })
  }

  const handleStopTrading = () => {
    sendMessage({ type: 'stop_trading' })
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <nav className="container mx-auto p-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Activity className="h-6 w-6" />
            <h1 className="text-xl font-bold">Soda Trading Bot</h1>
          </div>
          <div className="flex items-center space-x-4">
            <Button variant="outline" className="p-2">
              <Wallet className="h-5 w-5" />
            </Button>
            <Button variant="outline" className="p-2">
              <Settings className="h-5 w-5" />
            </Button>
          </div>
        </nav>
      </header>
      <main className="container mx-auto p-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <h2 className="text-lg font-semibold">Trading Overview</h2>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <LineChart width={600} height={200} data={chartData}>
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="price" stroke="#8884d8" />
                  </LineChart>
                </div>
              </CardContent>
            </Card>
          </div>
          <div>
            <ConfigPanel
              onModeChange={setTradingMode}
              onStartTrading={handleStartTrading}
              onStopTrading={handleStopTrading}
              isConnected={connected}
              currentMode={tradingMode}
            />
          </div>
          <div className="lg:col-span-3">
            <Card>
              <CardHeader>
                <h2 className="text-lg font-semibold">Wallet Performance</h2>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 bg-secondary rounded-lg">
                    <div className="text-sm text-muted-foreground">Total Balance</div>
                    <div className="text-2xl font-semibold mt-1">{totalBalance.toFixed(2)} SOL</div>
                  </div>
                  <div className="p-4 bg-secondary rounded-lg">
                    <div className="text-sm text-muted-foreground">24h Profit/Loss</div>
                    <div className={`text-2xl font-semibold mt-1 ${totalProfitLoss >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {totalProfitLoss >= 0 ? '+' : ''}{totalProfitLoss.toFixed(2)} SOL
                    </div>
                  </div>
                  <div className="p-4 bg-secondary rounded-lg">
                    <div className="text-sm text-muted-foreground">Active Wallets</div>
                    <div className="text-2xl font-semibold mt-1">{activeWallets}</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
