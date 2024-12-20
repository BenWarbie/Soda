import React, { createContext, useContext, useEffect, useState } from 'react'

interface WebSocketContextType {
  connected: boolean
  sendMessage: (message: any) => void
  lastMessage: any | null
}

const WebSocketContext = createContext<WebSocketContextType>({
  connected: false,
  sendMessage: () => {},
  lastMessage: null,
})

export function WebSocketProvider({ children }: { children: React.ReactNode }) {
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [connected, setConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<any>(null)

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws')

    ws.onopen = () => {
      setConnected(true)
    }

    ws.onclose = () => {
      setConnected(false)
    }

    ws.onmessage = (event) => {
      setLastMessage(JSON.parse(event.data))
    }

    setSocket(ws)

    return () => {
      ws.close()
    }
  }, [])

  const sendMessage = (message: any) => {
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message))
    }
  }

  return (
    <WebSocketContext.Provider value={{ connected, sendMessage, lastMessage }}>
      {children}
    </WebSocketContext.Provider>
  )
}

export const useWebSocket = () => useContext(WebSocketContext)
