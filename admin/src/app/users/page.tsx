import { prisma } from '@/lib/prisma'
import { Sidebar } from '@/components/sidebar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

async function getUsers() {
  return prisma.user.findMany({
    include: { balance: true },
    orderBy: { createdAt: 'desc' },
    take: 100,
  })
}

const statusColors: Record<string, string> = {
  PENDING: 'bg-yellow-100 text-yellow-800',
  ACTIVE: 'bg-green-100 text-green-800',
  INACTIVE: 'bg-gray-100 text-gray-800',
  BANNED: 'bg-red-100 text-red-800',
}

export default async function UsersPage() {
  const users = await getUsers()

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-8 bg-gray-100">
        <h1 className="text-3xl font-bold mb-8">Users</h1>
        <Card>
          <CardHeader>
            <CardTitle>All Users ({users.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4">User</th>
                    <th className="text-left py-3 px-4">Contact</th>
                    <th className="text-left py-3 px-4">Balance</th>
                    <th className="text-left py-3 px-4">Referral Code</th>
                    <th className="text-left py-3 px-4">Status</th>
                    <th className="text-left py-3 px-4">Joined</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <div className="font-medium">{user.firstName} {user.lastName}</div>
                        <div className="text-sm text-gray-500">@{user.username || 'N/A'}</div>
                        <div className="text-xs text-gray-400">ID: {user.telegramId.toString()}</div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="text-sm">{user.email || '-'}</div>
                        <div className="text-sm text-gray-500">{user.whatsapp || '-'}</div>
                      </td>
                      <td className="py-3 px-4 font-medium">
                        Rp {Number(user.balance?.amount || 0).toLocaleString('id-ID')}
                      </td>
                      <td className="py-3 px-4">
                        <code className="bg-gray-100 px-2 py-1 rounded text-sm">
                          {user.referralCode}
                        </code>
                      </td>
                      <td className="py-3 px-4">
                        <Badge className={statusColors[user.status]}>
                          {user.status}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-500">
                        {new Date(user.createdAt).toLocaleDateString('id-ID')}
                      </td>
                    </tr>
                  ))}
                  {users.length === 0 && (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-gray-500">
                        No users found
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
