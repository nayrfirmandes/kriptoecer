import { prisma } from '@/lib/prisma'
import { Sidebar } from '@/components/sidebar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { WithdrawalActions } from './actions'

async function getWithdrawals() {
  return prisma.withdrawal.findMany({
    include: { user: true },
    orderBy: { createdAt: 'desc' },
    take: 50,
  })
}

const statusColors: Record<string, string> = {
  PENDING: 'bg-yellow-100 text-yellow-800',
  PROCESSING: 'bg-blue-100 text-blue-800',
  COMPLETED: 'bg-green-100 text-green-800',
  FAILED: 'bg-red-100 text-red-800',
  CANCELLED: 'bg-gray-100 text-gray-800',
}

export default async function WithdrawalsPage() {
  const withdrawals = await getWithdrawals()

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-8 bg-gray-100">
        <h1 className="text-3xl font-bold mb-8">Withdrawals</h1>
        <Card>
          <CardHeader>
            <CardTitle>Recent Withdrawals</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4">User</th>
                    <th className="text-left py-3 px-4">Amount</th>
                    <th className="text-left py-3 px-4">Destination</th>
                    <th className="text-left py-3 px-4">Status</th>
                    <th className="text-left py-3 px-4">Date</th>
                    <th className="text-left py-3 px-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {withdrawals.map((withdrawal) => (
                    <tr key={withdrawal.id} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <div className="font-medium">{withdrawal.user.firstName || withdrawal.user.username}</div>
                        <div className="text-sm text-gray-500">ID: {withdrawal.user.telegramId.toString()}</div>
                      </td>
                      <td className="py-3 px-4 font-medium">
                        Rp {Number(withdrawal.amount).toLocaleString('id-ID')}
                      </td>
                      <td className="py-3 px-4">
                        {withdrawal.bankName ? (
                          <div>
                            <div className="font-medium">{withdrawal.bankName}</div>
                            <div className="text-sm text-gray-500">{withdrawal.accountNumber}</div>
                            <div className="text-sm text-gray-500">{withdrawal.accountName}</div>
                          </div>
                        ) : (
                          <div>
                            <div className="font-medium">{withdrawal.ewalletType}</div>
                            <div className="text-sm text-gray-500">{withdrawal.ewalletNumber}</div>
                          </div>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        <Badge className={statusColors[withdrawal.status]}>
                          {withdrawal.status}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-500">
                        {new Date(withdrawal.createdAt).toLocaleString('id-ID')}
                      </td>
                      <td className="py-3 px-4">
                        {withdrawal.status === 'PENDING' && (
                          <WithdrawalActions withdrawalId={withdrawal.id} />
                        )}
                      </td>
                    </tr>
                  ))}
                  {withdrawals.length === 0 && (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-gray-500">
                        No withdrawals found
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}
