import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params

    const withdrawal = await prisma.withdrawal.findUnique({
      where: { id },
    })

    if (!withdrawal) {
      return NextResponse.json({ error: 'Withdrawal not found' }, { status: 404 })
    }

    if (withdrawal.status !== 'PENDING') {
      return NextResponse.json({ error: 'Withdrawal already processed' }, { status: 400 })
    }

    await prisma.$transaction([
      prisma.withdrawal.update({
        where: { id },
        data: { status: 'COMPLETED' },
      }),
      prisma.transaction.updateMany({
        where: { 
          userId: withdrawal.userId,
          type: 'WITHDRAW',
          status: 'PENDING',
        },
        data: { status: 'COMPLETED' },
      }),
    ])

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Approve withdrawal error:', error)
    return NextResponse.json({ error: 'Server error' }, { status: 500 })
  }
}
