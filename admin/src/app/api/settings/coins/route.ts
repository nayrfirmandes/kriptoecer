import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

export async function POST(request: NextRequest) {
  try {
    const { settings } = await request.json()

    for (const setting of settings) {
      await prisma.coinSetting.upsert({
        where: {
          coinSymbol_network: {
            coinSymbol: setting.symbol,
            network: setting.network,
          },
        },
        update: {
          buyMargin: setting.buyMargin,
          sellMargin: setting.sellMargin,
        },
        create: {
          coinSymbol: setting.symbol,
          network: setting.network,
          buyMargin: setting.buyMargin,
          sellMargin: setting.sellMargin,
          isActive: true,
        },
      })
    }

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Save coin settings error:', error)
    return NextResponse.json({ error: 'Server error' }, { status: 500 })
  }
}
