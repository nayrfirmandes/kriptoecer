import { prisma } from '@/lib/prisma'
import { Sidebar } from '@/components/sidebar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

async function getStats() {
  const [
    totalUsers,
    activeUsers,
    pendingDeposits,
    pendingWithdrawals,
    totalDeposits,
    totalWithdrawals,
  ] = await Promise.all([
    prisma.user.count(),
    prisma.user.count({ where: { status: 'ACTIVE' } }),
    prisma.deposit.count({ where: { status: 'PENDING' } }),
    prisma.withdrawal.count({ where: { status: 'PENDING' } }),
    prisma.deposit.aggregate({
      where: { status: 'COMPLETED' },
      _sum: { amount: true },
    }),
    prisma.withdrawal.aggregate({
      where: { status: 'COMPLETED' },
      _sum: { amount: true },
    }),
  ])

  return {
    totalUsers,
    activeUsers,
    pendingDeposits,
    pendingWithdrawals,
    totalDepositsAmount: totalDeposits._sum.amount || 0,
    totalWithdrawalsAmount: totalWithdrawals._sum.amount || 0,
  }
}

export default async function DashboardPage() {
  const stats = await getStats()

  const statCards = [
    { title: 'Total Users', value: stats.totalUsers, icon: '👥', color: 'bg-blue-500' },
    { title: 'Active Users', value: stats.activeUsers, icon: '✅', color: 'bg-green-500' },
    { title: 'Pending Deposits', value: stats.pendingDeposits, icon: '⏳', color: 'bg-yellow-500' },
    { title: 'Pending Withdrawals', value: stats.pendingWithdrawals, icon: '⏳', color: 'bg-orange-500' },
    { title: 'Total Deposits', value: `Rp ${Number(stats.totalDepositsAmount).toLocaleString('id-ID')}`, icon: '💰', color: 'bg-emerald-500' },
    { title: 'Total Withdrawals', value: `Rp ${Number(stats.totalWithdrawalsAmount).toLocaleString('id-ID')}`, icon: '💸', color: 'bg-red-500' },
  ]

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-8 bg-gray-100">
        <h1 className="text-3xl font-bold mb-8">Dashboard</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {statCards.map((stat, index) => (
            <Card key={index}>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">
                  {stat.title}
                </CardTitle>
                <span className={`${stat.color} text-white p-2 rounded-lg`}>
                  {stat.icon}
                </span>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
              </CardContent>
            </Card>
          ))}
        </div>
      </main>
    </div>
  )
}
