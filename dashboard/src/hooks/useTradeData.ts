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
  roi: number
}

export interface Position {
  token_address: string
  entry_price: number
  amount: number
  wallet_address: string
  stop_loss_threshold: number
  trailing_stop: boolean
  trailing_distance: number
  highest_price: number
  stop_loss_price: number
}

export interface BundlerStatus {
  activeBundles: number
  pendingTransactions: number
  completedBundles: number
}

export interface TradingState {
  trades: Trade[]
  wallets: WalletPerformance[]
  positions: Position[]
  priceImpacts: Record<string, number>
  totalBalance: number
  totalProfitLoss: number
  activeWallets: number
  bundlerStatus: BundlerStatus
}

const initialState: TradingState = {
  trades: [],
  wallets: [],
  positions: [],
  priceImpacts: {},
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
      // No need to parse, lastMessage is already an object
      const data = lastMessage
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
        } else if (data.type === 'position_update') {
          setTradingState(prev => ({
            ...prev,
            positions: data.positions,
            priceImpacts: data.priceImpacts || prev.priceImpacts
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
