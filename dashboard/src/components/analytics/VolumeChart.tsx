import { FC } from 'react'
import { LineChart, XAxis, YAxis, Tooltip, Line } from 'recharts'

interface VolumeData {
  time: string
  volume: number
}

interface VolumeChartProps {
  data: VolumeData[]
}

export const VolumeChart: FC<VolumeChartProps> = ({ data }) => {
  return (
    <div className="w-[600px] h-[200px]">
      <LineChart width={600} height={200} data={data}>
        <XAxis
          dataKey="time"
          tickFormatter={(time) => new Date(time).toLocaleTimeString()}
        />
        <YAxis />
        <Tooltip
          labelFormatter={(time) => new Date(time).toLocaleString()}
          formatter={(value) => [`${value} SOL`, 'Volume']}
        />
        <Line
          type="monotone"
          dataKey="volume"
          stroke="#8884d8"
          strokeWidth={2}
          dot={false}
        />
      </LineChart>
    </div>
  )
}
