import { prisma } from '@/lib/prisma'
import { Sidebar } from '@/components/sidebar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { CoinSettingsForm } from './coin-settings-form'
import { ReferralSettingsForm } from './referral-settings-form'
import { PaymentMethodsForm } from './payment-methods-form'

async function getSettings() {
  const [coinSettings, referralSetting, paymentMethods] = await Promise.all([
    prisma.coinSetting.findMany({ orderBy: { coinSymbol: 'asc' } }),
    prisma.referralSetting.findFirst(),
    prisma.paymentMethod.findMany({ orderBy: { name: 'asc' } }),
  ])

  return { coinSettings, referralSetting, paymentMethods }
}

export default async function SettingsPage() {
  const { coinSettings, referralSetting, paymentMethods } = await getSettings()

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-8 bg-gray-100">
        <h1 className="text-3xl font-bold mb-8">Settings</h1>
        
        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Coin Margins</CardTitle>
            </CardHeader>
            <CardContent>
              <CoinSettingsForm settings={coinSettings} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Referral Bonus</CardTitle>
            </CardHeader>
            <CardContent>
              <ReferralSettingsForm setting={referralSetting} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Payment Methods</CardTitle>
            </CardHeader>
            <CardContent>
              <PaymentMethodsForm methods={paymentMethods} />
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
