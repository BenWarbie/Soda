import { Card, CardHeader, CardContent } from './ui/card'
import { Button } from './ui/button'
import { Tabs, TabsList, TabsTrigger } from './ui/tabs'
import { Input } from './ui/input'
import { Label } from './ui/label'

interface ConfigPanelProps {
  onModeChange: (mode: string) => void
  onStartTrading: () => void
  onStopTrading: () => void
  isConnected: boolean
  currentMode: string
  onBundlerConfigChange?: (config: {
    splitCount: number
    splitSize: number
  }) => void
}

export function ConfigPanel({
  onModeChange,
  onStartTrading,
  onStopTrading,
  isConnected,
  currentMode,
  onBundlerConfigChange
}: ConfigPanelProps) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold">Trading Configuration</h3>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div>
              <Label>Trading Mode</Label>
              <Tabs value={currentMode} onValueChange={onModeChange}>
                <TabsList className="w-full">
                  <TabsTrigger value="safe" className="flex-1">Safe</TabsTrigger>
                  <TabsTrigger value="normal" className="flex-1">Normal</TabsTrigger>
                  <TabsTrigger value="aggressive" className="flex-1">Aggressive</TabsTrigger>
                  <TabsTrigger value="high_frequency" className="flex-1">High Frequency</TabsTrigger>
                </TabsList>
              </Tabs>
            </div>

            <div>
              <Label>Risk Parameters</Label>
              <div className="grid grid-cols-2 gap-4 mt-2">
                <div>
                  <Label className="text-sm">Stop Loss (%)</Label>
                  <Input type="number" placeholder="2.5" min="0" max="100" step="0.1" />
                </div>
                <div>
                  <Label className="text-sm">Take Profit (%)</Label>
                  <Input type="number" placeholder="5.0" min="0" max="100" step="0.1" />
                </div>
              </div>
            </div>

            <div>
              <Label>Bundler Configuration</Label>
              <div className="space-y-2 mt-2">
                <div>
                  <Label className="text-sm">Split Count</Label>
                  <Input
                    type="number"
                    placeholder="3"
                    min="2"
                    max="10"
                    onChange={(e) => onBundlerConfigChange?.({
                      splitCount: parseInt(e.target.value),
                      splitSize: 0.5
                    })}
                  />
                </div>
                <div>
                  <Label className="text-sm">Split Size (SOL)</Label>
                  <Input
                    type="number"
                    placeholder="0.5"
                    min="0.1"
                    step="0.1"
                    onChange={(e) => onBundlerConfigChange?.({
                      splitCount: 3,
                      splitSize: parseFloat(e.target.value)
                    })}
                  />
                </div>
              </div>
            </div>

            <div>
              <Label>Wallet Management</Label>
              <div className="space-y-2 mt-2">
                <div>
                  <Label className="text-sm">Number of Wallets</Label>
                  <Input type="number" placeholder="5" min="1" max="100" />
                </div>
                <div>
                  <Label className="text-sm">SOL per Wallet</Label>
                  <Input type="number" placeholder="1.0" min="0.1" step="0.1" />
                </div>
              </div>
            </div>

            <div>
              <Label>Session Settings</Label>
              <div className="space-y-2 mt-2">
                <div>
                  <Label className="text-sm">Trade Interval (ms)</Label>
                  <Input type="number" placeholder="1000" min="100" step="100" />
                </div>
                <div>
                  <Label className="text-sm">Max Trade Size (SOL)</Label>
                  <Input type="number" placeholder="0.5" min="0.1" step="0.1" />
                </div>
              </div>
            </div>

            <div>
              <Label>Trading Controls</Label>
              <div className="space-y-2 mt-2">
                <Button
                  className="w-full"
                  disabled={!isConnected}
                  onClick={onStartTrading}
                >
                  Start Trading
                </Button>
                <Button
                  variant="outline"
                  className="w-full"
                  disabled={!isConnected}
                  onClick={onStopTrading}
                >
                  Stop Trading
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
