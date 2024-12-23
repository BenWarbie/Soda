import { Activity, Wallet, Settings } from 'lucide-react'
import { Card, CardHeader, CardContent } from './components/ui/card'
import { Button } from './components/ui/button'
import { ConfigPanel } from './components/ConfigPanel'
import { useWebSocket } from './contexts/WebSocketContext'
import { useState } from 'react'
import { BundlerControls } from './components/BundlerControls'
import { Dashboard } from './components/analytics/Dashboard'

export default function App() {
  const { connected, sendMessage } = useWebSocket()
  const [tradingMode, setTradingMode] = useState('normal')

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
              <CardContent className="space-y-6">
                <Dashboard />
                <BundlerControls />
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
        </div>
      </main>
    </div>
  )
}
