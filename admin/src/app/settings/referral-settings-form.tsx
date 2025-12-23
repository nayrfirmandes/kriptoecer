'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

interface ReferralSetting {
  id: string
  referrerBonus: number
  refereeBonus: number
  isActive: boolean
}

export function ReferralSettingsForm({ setting }: { setting: ReferralSetting | null }) {
  const router = useRouter()
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setLoading(true)

    const formData = new FormData(e.currentTarget)

    const res = await fetch('/api/settings/referral', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        referrerBonus: parseFloat(formData.get('referrerBonus') as string),
        refereeBonus: parseFloat(formData.get('refereeBonus') as string),
      }),
    })

    if (res.ok) {
      router.refresh()
    } else {
      alert('Gagal menyimpan pengaturan')
    }

    setLoading(false)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-md">
      <div>
        <Label>Bonus Referrer (Rp)</Label>
        <Input
          name="referrerBonus"
          type="number"
          step="0.01"
          defaultValue={setting?.referrerBonus || 10000}
          placeholder="Bonus untuk yang mengajak (Rp)"
        />
        <p className="text-sm text-gray-500 mt-1">Bonus yang didapat oleh user yang mengajak</p>
      </div>
      <div>
        <Label>Bonus Referee (Rp)</Label>
        <Input
          name="refereeBonus"
          type="number"
          step="0.01"
          defaultValue={setting?.refereeBonus || 5000}
          placeholder="Bonus untuk yang diajak (Rp)"
        />
        <p className="text-sm text-gray-500 mt-1">Bonus yang didapat oleh user baru yang diajak</p>
      </div>
      <Button type="submit" disabled={loading}>
        {loading ? 'Menyimpan...' : 'Simpan Pengaturan'}
      </Button>
    </form>
  )
}
