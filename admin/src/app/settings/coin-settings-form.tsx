'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

interface CoinSetting {
  id: string
  coinSymbol: string
  network: string
  buyMargin: number
  sellMargin: number
  isActive: boolean
}

const defaultCoins = [
  { symbol: 'BTC', networks: ['Bitcoin', 'BEP20'] },
  { symbol: 'ETH', networks: ['ERC20', 'BEP20', 'Arbitrum'] },
  { symbol: 'BNB', networks: ['BEP20'] },
  { symbol: 'SOL', networks: ['Solana'] },
  { symbol: 'USDT', networks: ['TRC20', 'ERC20', 'BEP20'] },
  { symbol: 'USDC', networks: ['ERC20', 'BEP20', 'Solana'] },
]

export function CoinSettingsForm({ settings }: { settings: CoinSetting[] }) {
  const router = useRouter()
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setLoading(true)

    const formData = new FormData(e.currentTarget)
    const updates: { symbol: string; network: string; buyMargin: number; sellMargin: number }[] = []

    defaultCoins.forEach(coin => {
      coin.networks.forEach(network => {
        const key = `${coin.symbol}-${network}`
        const buyMargin = parseFloat(formData.get(`buy-${key}`) as string) || 2
        const sellMargin = parseFloat(formData.get(`sell-${key}`) as string) || 2
        updates.push({ symbol: coin.symbol, network, buyMargin, sellMargin })
      })
    })

    const res = await fetch('/api/settings/coins', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ settings: updates }),
    })

    if (res.ok) {
      router.refresh()
    } else {
      alert('Gagal menyimpan pengaturan')
    }

    setLoading(false)
  }

  const getSetting = (symbol: string, network: string) => {
    return settings.find(s => s.coinSymbol === symbol && s.network === network)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {defaultCoins.map(coin => (
        <div key={coin.symbol} className="border rounded-lg p-4">
          <h3 className="font-bold mb-3">{coin.symbol}</h3>
          <div className="grid gap-4">
            {coin.networks.map(network => {
              const setting = getSetting(coin.symbol, network)
              const key = `${coin.symbol}-${network}`
              return (
                <div key={key} className="grid grid-cols-3 gap-4 items-center">
                  <span className="text-sm text-gray-600">{network}</span>
                  <div>
                    <Label className="text-xs">Buy Margin %</Label>
                    <Input
                      name={`buy-${key}`}
                      type="number"
                      step="0.1"
                      defaultValue={setting?.buyMargin || 2}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <Label className="text-xs">Sell Margin %</Label>
                    <Input
                      name={`sell-${key}`}
                      type="number"
                      step="0.1"
                      defaultValue={setting?.sellMargin || 2}
                      className="w-full"
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      ))}
      <Button type="submit" disabled={loading}>
        {loading ? 'Menyimpan...' : 'Simpan Pengaturan'}
      </Button>
    </form>
  )
}
