import { Card, CardHeader, CardContent } from '../ui/card'
import { VolumeChart } from './VolumeChart'
import { PositionTracker } from './PositionTracker'
import { RiskMetrics } from './RiskMetrics'
import { useTradeData } from '../../hooks/useTradeData'

export function Dashboard() {
  const { trades, totalBalance, totalProfitLoss, activeWallets, bundlerStatus } = useTradeData()

  const volumeData = trades.map(trade => ({
    time: trade.timestamp.toString(),
    volume: trade.amount
  }))

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold">Trading Volume</h3>
        </CardHeader>
        <CardContent>
          <VolumeChart data={volumeData} />
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold">Position Tracker</h3>
          </CardHeader>
          <CardContent>
            <PositionTracker />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold">Risk Metrics</h3>
          </CardHeader>
          <CardContent>
            <RiskMetrics
              totalBalance={totalBalance}
              totalProfitLoss={totalProfitLoss}
              activeWallets={activeWallets}
              bundlerStatus={bundlerStatus}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
