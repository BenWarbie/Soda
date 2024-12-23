import { ArrowUpIcon, ArrowDownIcon } from 'lucide-react'
import { useTradeData } from '../../hooks/useTradeData'

interface RiskMetricsProps {
  totalBalance: number
  totalProfitLoss: number
  activeWallets: number
  bundlerStatus: {
    activeBundles: number
    pendingTransactions: number
    completedBundles: number
  }
}

export function RiskMetrics({ totalBalance, totalProfitLoss, activeWallets, bundlerStatus }: RiskMetricsProps) {
  const { priceImpacts = {} } = useTradeData()

  const avgPriceImpact = Object.values(priceImpacts as Record<string, number>).length
    ? Object.values(priceImpacts as Record<string, number>).reduce((a, b) => a + b, 0) /
      Object.values(priceImpacts as Record<string, number>).length
    : 0

  return (
    <div className="grid grid-cols-2 gap-4">
      <div className="p-4 bg-secondary rounded-lg">
        <div className="text-sm text-muted-foreground">Total Balance</div>
        <div className="text-2xl font-semibold mt-1 flex items-center">
          {totalBalance.toFixed(2)} SOL
        </div>
      </div>
      <div className="p-4 bg-secondary rounded-lg">
        <div className="text-sm text-muted-foreground">24h Profit/Loss</div>
        <div className={`text-2xl font-semibold mt-1 flex items-center ${totalProfitLoss >= 0 ? 'text-green-500' : 'text-red-500'}`}>
          {totalProfitLoss >= 0 ? <ArrowUpIcon className="w-4 h-4 mr-1" /> : <ArrowDownIcon className="w-4 h-4 mr-1" />}
          {Math.abs(totalProfitLoss).toFixed(2)} SOL
        </div>
      </div>
      <div className="p-4 bg-secondary rounded-lg">
        <div className="text-sm text-muted-foreground">Active Wallets</div>
        <div className="text-2xl font-semibold mt-1">
          {activeWallets}
        </div>
      </div>
      <div className="p-4 bg-secondary rounded-lg">
        <div className="text-sm text-muted-foreground">Active Bundles</div>
        <div className="text-2xl font-semibold mt-1">
          {bundlerStatus.activeBundles}
        </div>
      </div>
      <div className="p-4 bg-secondary rounded-lg">
        <div className="text-sm text-muted-foreground">Price Impact</div>
        <div className="text-2xl font-semibold mt-1">
          {(avgPriceImpact * 100).toFixed(2)}%
        </div>
      </div>
      <div className="p-4 bg-secondary rounded-lg">
        <div className="text-sm text-muted-foreground">Pending Transactions</div>
        <div className="text-2xl font-semibold mt-1">
          {bundlerStatus.pendingTransactions}
        </div>
      </div>
    </div>
  )
}
