import { useEffect, useState } from 'react'
import { useWebSocket } from '../contexts/WebSocketContext'

export interface Trade {
  timestamp: number
  price: number
  amount: number
  side: 'buy' | 'sell'
  wallet: string
}

export interface WalletPerformance {
  address: string
  balance: number
  profitLoss: number
  trades: number
}

export interface BundlerStatus {
  activeBundles: number
  pendingTransactions: number
  completedBundles: number
}

export interface TradingState {
  trades: Trade[]
  wallets: WalletPerformance[]
  totalBalance: number
  totalProfitLoss: number
  activeWallets: number
  bundlerStatus: BundlerStatus
}

const initialState: TradingState = {
  trades: [],
  wallets: [],
  totalBalance: 0,
  totalProfitLoss: 0,
  activeWallets: 0,
  bundlerStatus: {
    activeBundles: 0,
    pendingTransactions: 0,
    completedBundles: 0
  }
}

export function useTradeData() {
  const [tradingState, setTradingState] = useState<TradingState>(initialState)
  const { lastMessage } = useWebSocket()

  useEffect(() => {
    if (lastMessage) {
      try {
        const data = JSON.parse(lastMessage)

        if (data.type === 'trade') {
          setTradingState(prev => ({
            ...prev,
            trades: [...prev.trades, data.trade].slice(-100), // Keep last 100 trades
          }))
        } else if (data.type === 'wallet_update') {
          setTradingState(prev => ({
            ...prev,
            wallets: data.wallets,
            totalBalance: data.totalBalance,
            totalProfitLoss: data.totalProfitLoss,
            activeWallets: data.activeWallets
          }))
        } else if (data.type === 'bundler_update') {
          setTradingState(prev => ({
            ...prev,
            bundlerStatus: {
              activeBundles: data.activeBundles,
              pendingTransactions: data.pendingTransactions,
              completedBundles: data.completedBundles
            }
          }))
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }
  }, [lastMessage])

  return tradingState
}
