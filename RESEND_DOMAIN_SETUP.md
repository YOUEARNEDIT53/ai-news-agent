# Resend Domain Verification for acrartex.com

**Domain ID:** 4e8e26c7-02e8-4b50-8bea-2dff98a2217a
**Status:** Pending DNS verification

## Required DNS Records

Add these 3 records to your acrartex.com DNS settings:

### 1. DKIM Record (TXT)
| Field | Value |
|-------|-------|
| **Type** | TXT |
| **Name/Host** | `resend._domainkey` |
| **Value** | `p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC5qVeKgfNHzcIUjwl65CteFX8rMf2Ko55gqoEa6KJItcv2bNy0Pm8K2MTD4Cz04XFRxjL/WXh3fvq2imlfeJ7eVB1hha5FLvCdLguvGQ/Foabo+t8cny6ViVmXW2QI1yvHgm6F30OqP7mRv4NpEFv4F4cLjNSk9oKJrV0+r9JvEQIDAQAB` |
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
curl -X POST "https://api.resend.com/domains/4e8e26c7-02e8-4b50-8bea-2dff98a2217a/verify" \
  -H "Authorization: Bearer re_QQvQXrXk_96hjcZTfMSbMw3jCXtJszHro"
```

3. Update the email FROM address in `.env.local`:
```
DIGEST_EMAIL_FROM=AI News Agent <news@acrartex.com>
```

## Once Verified

The system will be able to send emails to any recipient including:
- adam.sadowski@acrartex.com
- jim.story@acrartex.com
- chris.bolender@acrartex.com
- youearnedit@gmail.com
