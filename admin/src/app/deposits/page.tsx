import { prisma } from '@/lib/prisma'
import { Sidebar } from '@/components/sidebar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { DepositActions } from './actions'

async function getDeposits() {
  return prisma.deposit.findMany({
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

export default async function DepositsPage() {
  const deposits = await getDeposits()

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-8 bg-gray-100">
        <h1 className="text-3xl font-bold mb-8">Deposits</h1>
        <Card>
          <CardHeader>
            <CardTitle>Recent Deposits</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4">User</th>
                    <th className="text-left py-3 px-4">Amount</th>
                    <th className="text-left py-3 px-4">Method</th>
                    <th className="text-left py-3 px-4">Status</th>
                    <th className="text-left py-3 px-4">Date</th>
                    <th className="text-left py-3 px-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {deposits.map((deposit) => (
                    <tr key={deposit.id} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <div className="font-medium">{deposit.user.firstName || deposit.user.username}</div>
                        <div className="text-sm text-gray-500">ID: {deposit.user.telegramId.toString()}</div>
                      </td>
                      <td className="py-3 px-4 font-medium">
                        Rp {Number(deposit.amount).toLocaleString('id-ID')}
                      </td>
                      <td className="py-3 px-4">{deposit.paymentMethod}</td>
                      <td className="py-3 px-4">
                        <Badge className={statusColors[deposit.status]}>
                          {deposit.status}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-500">
                        {new Date(deposit.createdAt).toLocaleString('id-ID')}
                      </td>
                      <td className="py-3 px-4">
                        {deposit.status === 'PENDING' && (
                          <DepositActions depositId={deposit.id} />
                        )}
                      </td>
                    </tr>
                  ))}
                  {deposits.length === 0 && (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-gray-500">
                        No deposits found
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
