# Resend Domain Verification for ipguy.co

**Domain ID:** a32cd07e-10b9-41c1-8581-5afbb6eff1c7
**Status:** Pending DNS verification

## Required DNS Records

Add these 3 records to your ipguy.co DNS settings:

### 1. DKIM Record (TXT)
| Field | Value |
|-------|-------|
| **Type** | TXT |
| **Name/Host** | `resend._domainkey` |
| **Value** | `p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDT/fz4arbByfmciyiDV8jYleWs90+sPBlwbTm1gN0DQ2dSNIy9FhwmWB2HizpjKa4kCxOqdiRyPmbp6zacrQHZ4S5Egt6Lv4RzEzL3ilBL5OQOwe9vytNydpONsQ+I0H5rycOxoM1pSVFZSWEL5rXtQgBhua5PzpWZqDQj65etQQIDAQAB` |
| **TTL** | Auto/Default |

### 2. SPF MX Record
| Field | Value |
|-------|-------|
| **Type** | MX |
| **Name/Host** | `send` |
| **Value** | `feedback-smtp.us-east-1.amazonses.com` |
| **Priority** | 10 |
| **TTL** | Auto/Default |

### 3. SPF TXT Record
| Field | Value |
|-------|-------|
| **Type** | TXT |
| **Name/Host** | `send` |
| **Value** | `v=spf1 include:amazonses.com ~all` |
| **TTL** | Auto/Default |

## After Adding DNS Records

1. Wait 5-10 minutes for DNS propagation
2. Verify the domain via API:
```bash
curl -X POST "https://api.resend.com/domains/a32cd07e-10b9-41c1-8581-5afbb6eff1c7/verify" \
  -H "Authorization: Bearer re_QQvQXrXk_96hjcZTfMSbMw3jCXtJszHro"
```

3. The `.env.local` is already configured with:
```
DIGEST_EMAIL_FROM=AI News Agent <news@ipguy.co>
```

## Once Verified

The system will be able to send emails to:
- adam.sadowski@acrartex.com
- jim.story@acrartex.com
- chris.bolender@acrartex.com
- youearnedit@gmail.com
