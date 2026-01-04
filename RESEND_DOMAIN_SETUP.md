# Resend Domain Verification for mail.ipguy.co

**Domain ID:** 1d7b4415-3732-4b5a-afa2-513273b64c42
**Status:** Pending DNS verification

## Required DNS Records

Add these 3 records to your ipguy.co DNS settings (note the `mail` subdomain):

### 1. DKIM Record (TXT)
| Field | Value |
|-------|-------|
| **Type** | TXT |
| **Name/Host** | `resend._domainkey.mail` |
| **Value** | `p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDd49//zXnEoz9QyLppz6ao+w2XqgGH0zDB4hgivSRIC3H6/OyjIw+PbrXuarIPpDqRwaWtp6pcYDNc+vDkPm7i1oIfxy4n/4DFV61KMEHPUCgInpbQxRbFPzHdninnKp75Nd+L93GCxq0AvzIuqiwiU3EudtQ2y9tpPRq8QqAgHwIDAQAB` |
| **TTL** | Auto/Default |

### 2. SPF MX Record
| Field | Value |
|-------|-------|
| **Type** | MX |
| **Name/Host** | `send.mail` |
| **Value** | `feedback-smtp.us-east-1.amazonses.com` |
| **Priority** | 10 |
| **TTL** | Auto/Default |

### 3. SPF TXT Record
| Field | Value |
|-------|-------|
| **Type** | TXT |
| **Name/Host** | `send.mail` |
| **Value** | `v=spf1 include:amazonses.com ~all` |
| **TTL** | Auto/Default |

## After Adding DNS Records

1. Wait 5-10 minutes for DNS propagation
2. Verify the domain via API:
```bash
curl -X POST "https://api.resend.com/domains/1d7b4415-3732-4b5a-afa2-513273b64c42/verify" \
  -H "Authorization: Bearer re_QQvQXrXk_96hjcZTfMSbMw3jCXtJszHro"
```

3. The `.env.local` is already configured with:
```
DIGEST_EMAIL_FROM=AI News Agent <news@mail.ipguy.co>
```

## Once Verified

The system will be able to send emails to:
- adam.sadowski@acrartex.com
- jim.story@acrartex.com
- chris.bolender@acrartex.com
- youearnedit@gmail.com
