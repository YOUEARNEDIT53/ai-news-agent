import { NextRequest, NextResponse } from 'next/server';
import { supabaseAdmin } from '@/lib/supabase';
import { sendWelcomeDigestEmail } from '@/lib/resend';
import { DigestContent } from '@/types';

export const maxDuration = 60;

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { recipients } = body;

    if (!recipients || !Array.isArray(recipients) || recipients.length === 0) {
      return NextResponse.json(
        { error: 'recipients array is required' },
        { status: 400 }
      );
    }

    // Get the latest digest
    const { data: digest, error: digestError } = await supabaseAdmin
      .from('digests')
      .select('*')
      .order('date', { ascending: false })
      .limit(1)
      .single();

    if (digestError || !digest) {
      return NextResponse.json(
        { error: 'No digest found' },
        { status: 404 }
      );
    }

    // Send welcome email
    const result = await sendWelcomeDigestEmail(
      digest.date,
      digest.content as unknown as DigestContent,
      recipients
    );

    return NextResponse.json({
      success: result.success,
      error: result.error,
      sent_to: result.sent_to,
      digest_date: digest.date,
    });
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
