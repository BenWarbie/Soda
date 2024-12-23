import React, { createContext, useContext, useEffect, useState } from 'react'
import { TradingState } from '../hooks/useTradeData'

interface BundlerMessage {
  type: 'start_bundled_buy' | 'start_incremental_sell' | 'stop_bundler'
  token_address?: string
  split_count?: number
  split_size?: number
  timestamp?: number
}

interface TradeMessage {
  type: 'start_trading' | 'stop_trading'
  mode?: string
  timestamp?: number
}

interface PositionMessage {
  type: 'position_update'
  positions: Array<{
    token_address: string
    entry_price: number
    amount: number
    wallet_address: string
    stop_loss_threshold: number
    trailing_stop: boolean
    trailing_distance: number
    highest_price: number
    stop_loss_price: number
  }>
  priceImpacts: Record<string, number>
}

type WebSocketMessage = BundlerMessage | TradeMessage | PositionMessage

interface WebSocketContextType {
  connected: boolean
  sendMessage: (message: WebSocketMessage) => void
  lastMessage: WebSocketMessage | null
  tradingState: TradingState
}

const WebSocketContext = createContext<WebSocketContextType>({
  connected: false,
  sendMessage: () => {},
  lastMessage: null,
  tradingState: {
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
})

export function WebSocketProvider({ children }: { children: React.ReactNode }) {
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [connected, setConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<any>(null)
  const [tradingState, setTradingState] = useState<TradingState>({
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
  })

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws')

    ws.onopen = () => {
      setConnected(true)
    }

    ws.onclose = () => {
      setConnected(false)
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        // Handle different message types
        if (data.type === 'position_update') {
          setTradingState(prev => ({
            ...prev,
            positions: data.positions,
            priceImpacts: data.priceImpacts || prev.priceImpacts
          }))
          setLastMessage(data)
        } else if (data.type === 'trade') {
          setLastMessage(data)
        } else if (data.type === 'wallet_update') {
          setLastMessage(data)
        } else if (data.type === 'bundler_update') {
          setLastMessage(data)
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    setSocket(ws)

    return () => {
      ws.close()
    }
  }, [])

  const sendMessage = (message: WebSocketMessage) => {
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        ...message,
        timestamp: Date.now()
      }))
    }
  }

  return (
    <WebSocketContext.Provider value={{ connected, sendMessage, lastMessage }}>
      {children}
    </WebSocketContext.Provider>
  )
}

export const useWebSocket = () => useContext(WebSocketContext)
