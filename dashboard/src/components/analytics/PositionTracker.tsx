import { FC } from 'react'
import { Card, Table } from 'antd'
import { useTradeData } from '../../hooks/useTradeData'
import type { ColumnsType } from 'antd/es/table'

// Interface matching Position class from risk_manager.py
interface Position {
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

const columns: ColumnsType<Position> = [
  {
    title: 'Token',
    dataIndex: 'token_address',
    key: 'token_address',
    width: 120,
  },
  {
    title: 'Entry Price',
    dataIndex: 'entry_price',
    key: 'entry_price',
    render: (value: number) => value.toFixed(4),
  },
  {
    title: 'Amount',
    dataIndex: 'amount',
    key: 'amount',
    render: (value: number) => value.toFixed(4),
  },
  {
    title: 'Stop Loss',
    dataIndex: 'stop_loss_price',
    key: 'stop_loss_price',
    render: (value: number) => value.toFixed(4),
  },
  {
    title: 'Trailing',
    dataIndex: 'trailing_stop',
    key: 'trailing_stop',
    render: (value: boolean, record: Position) =>
      value ? `${(record.trailing_distance * 100).toFixed(1)}%` : 'Off',
  },
  {
    title: 'Highest Price',
    dataIndex: 'highest_price',
    key: 'highest_price',
    render: (value: number) => value.toFixed(4),
  },
]

export function PositionTracker() {
  const { positions = [] } = useTradeData()

  return (
    <Card title="Active Positions" className="h-full">
      <Table<Position>
        columns={columns}
        dataSource={positions}
        rowKey={(record) => `${record.wallet_address}:${record.token_address}`}
        pagination={false}
        scroll={{ y: 400 }}
      />
    </Card>
  )
}
