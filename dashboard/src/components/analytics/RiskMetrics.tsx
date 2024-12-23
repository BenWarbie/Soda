import React from 'react'
import { Card, Statistic, Row, Col } from 'antd'
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons'
import { useTradeData } from '../../hooks/useTradeData'

export function RiskMetrics() {
  const { totalProfitLoss, priceImpacts = {}, wallets = [] } = useTradeData()

  const avgPriceImpact = Object.values(priceImpacts).length
    ? Object.values(priceImpacts).reduce((a, b) => a + b, 0) /
      Object.values(priceImpacts).length
    : 0

  const maxPriceImpact = Object.values(priceImpacts).length
    ? Math.max(...Object.values(priceImpacts))
    : 0

  const avgROI = wallets.length
    ? wallets.reduce((sum, wallet) => sum + (wallet.roi || 0), 0) / wallets.length
    : 0

  return (
    <Card title="Risk Metrics" className="h-full">
      <Row gutter={[16, 16]}>
        <Col span={8}>
          <Statistic
            title="Total P/L"
            value={totalProfitLoss}
            precision={4}
            valueStyle={{ color: totalProfitLoss >= 0 ? '#3f8600' : '#cf1322' }}
            prefix={totalProfitLoss >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
            suffix="SOL"
          />
        </Col>
        <Col span={8}>
          <Statistic
            title="Avg ROI"
            value={avgROI}
            precision={2}
            valueStyle={{ color: avgROI >= 0 ? '#3f8600' : '#cf1322' }}
            suffix="%"
          />
        </Col>
        <Col span={8}>
          <Statistic
            title="Avg Price Impact"
            value={avgPriceImpact * 100}
            precision={2}
            suffix="%"
          />
        </Col>
        <Col span={8}>
          <Statistic
            title="Max Price Impact"
            value={maxPriceImpact * 100}
            precision={2}
            suffix="%"
          />
        </Col>
      </Row>
    </Card>
  )
}
