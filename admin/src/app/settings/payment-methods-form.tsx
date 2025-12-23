'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'

interface PaymentMethod {
  id: string
  type: string
  name: string
  accountNo: string | null
  accountName: string | null
  isActive: boolean
}

export function PaymentMethodsForm({ methods }: { methods: PaymentMethod[] }) {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [showForm, setShowForm] = useState(false)

  const handleAdd = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setLoading(true)

    const formData = new FormData(e.currentTarget)

    const res = await fetch('/api/settings/payment-methods', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: formData.get('type'),
        name: formData.get('name'),
        accountNo: formData.get('accountNo'),
        accountName: formData.get('accountName'),
      }),
    })

    if (res.ok) {
      setShowForm(false)
      router.refresh()
    } else {
      alert('Gagal menambah metode pembayaran')
    }

    setLoading(false)
  }

  const handleToggle = async (id: string, isActive: boolean) => {
    const res = await fetch(`/api/settings/payment-methods/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ isActive: !isActive }),
    })

    if (res.ok) {
      router.refresh()
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Hapus metode pembayaran ini?')) return

    const res = await fetch(`/api/settings/payment-methods/${id}`, {
      method: 'DELETE',
    })

    if (res.ok) {
      router.refresh()
    }
  }

  return (
    <div className="space-y-4">
      <table className="w-full">
        <thead>
          <tr className="border-b">
            <th className="text-left py-2">Type</th>
            <th className="text-left py-2">Name</th>
            <th className="text-left py-2">Account</th>
            <th className="text-left py-2">Status</th>
            <th className="text-left py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {methods.map(method => (
            <tr key={method.id} className="border-b">
              <td className="py-2">{method.type}</td>
              <td className="py-2">{method.name}</td>
              <td className="py-2">
                <div>{method.accountNo}</div>
                <div className="text-sm text-gray-500">{method.accountName}</div>
              </td>
              <td className="py-2">
                <Badge className={method.isActive ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                  {method.isActive ? 'Active' : 'Inactive'}
                </Badge>
              </td>
              <td className="py-2 space-x-2">
                <Button size="sm" variant="outline" onClick={() => handleToggle(method.id, method.isActive)}>
                  {method.isActive ? 'Disable' : 'Enable'}
                </Button>
                <Button size="sm" variant="destructive" onClick={() => handleDelete(method.id)}>
                  Delete
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {showForm ? (
        <form onSubmit={handleAdd} className="border rounded-lg p-4 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Type</Label>
              <select name="type" className="w-full border rounded-md p-2 mt-1" required>
                <option value="BANK">Bank</option>
                <option value="EWALLET">E-Wallet</option>
              </select>
            </div>
            <div>
              <Label>Name</Label>
              <Input name="name" placeholder="BCA / DANA / GoPay" required />
            </div>
            <div>
              <Label>Account Number</Label>
              <Input name="accountNo" placeholder="1234567890" required />
            </div>
            <div>
              <Label>Account Name</Label>
              <Input name="accountName" placeholder="PT Crypto Indonesia" required />
            </div>
          </div>
          <div className="flex gap-2">
            <Button type="submit" disabled={loading}>
              {loading ? 'Adding...' : 'Add Method'}
            </Button>
            <Button type="button" variant="outline" onClick={() => setShowForm(false)}>
              Cancel
            </Button>
          </div>
        </form>
      ) : (
        <Button onClick={() => setShowForm(true)}>Add Payment Method</Button>
      )}
    </div>
  )
}
