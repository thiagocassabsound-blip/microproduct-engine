# Webhook & Telemetry Deployment Guide

## Overview

This guide explains how to deploy the webhook server (`execucao/webhook_server.py`) and telemetry API (`telemetria/api.py`) to production for receiving Stripe events and frontend telemetry.

---

## Option 1: Railway (Recommended)

### Deploy Webhook Server

1. **Install Railway CLI**:
   ```bash
   npm i -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Create New Project**:
   ```bash
   railway init
   ```

4. **Deploy**:
   ```bash
   # From project root
   railway up --service webhook-server
   ```

5. **Set Environment Variables**:
   ```bash
   railway variables set WEBHOOK_SECRET=your_stripe_webhook_secret
   railway variables set PAYMENT_API_KEY=your_stripe_api_key
   railway variables set RESEND_API_KEY=your_resend_api_key
   railway variables set EMAIL_FROM=noreply@fastoolhub.com
   ```

6. **Configure Start Command**:
   In Railway dashboard → Settings → Start Command:
   ```
   python execucao/webhook_server.py
   ```

7. **Get Public URL**:
   Railway will provide a public URL like: `https://webhook-server-production-xxxx.up.railway.app`

8. **Configure Stripe Webhook**:
   - Go to Stripe Dashboard → Developers → Webhooks
   - Click "Add endpoint"
   - URL: `https://your-railway-url.up.railway.app/webhook`
   - Events: Select `checkout.session.completed`
   - Copy the signing secret and update `WEBHOOK_SECRET`

---

### Deploy Telemetry API

1. **Deploy as Separate Service**:
   ```bash
   railway up --service telemetry-api
   ```

2. **Configure Start Command**:
   ```
   python telemetria/api.py
   ```

3. **Set PORT Variable** (if needed):
   ```bash
   railway variables set PORT=5001
   ```

4. **Get Public URL**:
   Example: `https://telemetry-api-production-yyyy.up.railway.app`

5. **Update .env with Telemetry URL**:
   ```
   TELEMETRY_API_URL=https://telemetry-api-production-yyyy.up.railway.app
   ```

---

## Option 2: Render

### Deploy Webhook Server

1. **Create Web Service** on [render.com](https://render.com)
2. **Connect GitHub Repository**
3. **Configure**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python execucao/webhook_server.py`
   - **Port**: 5000 (default Flask port)

4. **Environment Variables**:
   Add in Render dashboard:
   ```
   WEBHOOK_SECRET=whsec_xxxxx
   PAYMENT_API_KEY=sk_xxx
   RESEND_API_KEY=re_xxx
   EMAIL_FROM=noreply@fastoolhub.com
   ```

5. **Get Service URL**: `https://webhook-server.onrender.com`

6. **Configure Stripe**: Same as Railway step 8

---

### Deploy Telemetry API

1. **Create Second Web Service**
2. **Start Command**: `python telemetria/api.py`
3. **Port**: 5001
4. **Get URL**: `https://telemetry-api.onrender.com`

---

## Option 3: Fly.io

### Install Fly CLI

```bash
curl -L https://fly.io/install.sh | sh
```

### Deploy Webhook

1. **Create fly.toml** in project root:
   ```toml
   app = "fastoolhub-webhook"
   
   [build]
     builder = "paketobuildpacks/builder:base"
   
   [env]
     PORT = "5000"
   
   [[services]]
     internal_port = 5000
     protocol = "tcp"
   
     [[services.ports]]
       handlers = ["http"]
       port = 80
   
     [[services.ports]]
       handlers = ["tls", "http"]
       port = 443
   ```

2. **Deploy**:
   ```bash
   fly launch
   fly secrets set WEBHOOK_SECRET=whsec_xxx PAYMENT_API_KEY=sk_xxx RESEND_API_KEY=re_xxx
   fly deploy
   ```

3. **Get URL**: `https://fastoolhub-webhook.fly.dev`

---

## Testing Webhooks Locally

### Using Stripe CLI

1. **Install Stripe CLI**:
   - macOS: `brew install stripe/stripe-cli/stripe`
   - Windows: Download from [stripe.com/docs/stripe-cli](https://stripe.com/docs/stripe-cli)

2. **Login**:
   ```bash
   stripe login
   ```

3. **Forward Events to Local Server**:
   ```bash
   stripe listen --forward-to localhost:5000/webhook
   ```

4. **Trigger Test Event**:
   ```bash
   stripe trigger checkout.session.completed
   ```

5. **Monitor Logs**:
   Check your local webhook server logs for the event

---

## Verification

### Webhook Server

```bash
curl https://your-webhook-url.com/success
# Should return: Purchase Successful! Check your email for the product.
```

### Telemetry API

```bash
curl https://your-telemetry-url.com/health
# Should return: {"status":"healthy","service":"telemetry-api"}
```

### Send Test Event

```bash
curl -X POST https://your-telemetry-url.com/api/track \
  -H "Content-Type: application/json" \
  -d '{
    "type": "visit",
    "product_id": "test-product",
    "metadata": {"test": true}
  }'
# Should return: {"status":"success","event_id":"2026-02-09T..."}
```

---

## Production Checklist

- [ ] Webhook server deployed and accessible
- [ ] Telemetry API deployed and accessible
- [ ] Stripe webhook configured with correct URL
- [ ] All environment variables set correctly
- [ ] CORS enabled on telemetry API
- [ ] Webhook signature verification working
- [ ] Email delivery tested end-to-end
- [ ] Events logged to `events.jsonl`
- [ ] Monitoring/alerts configured (optional)

---

## Troubleshooting

### Webhook Not Receiving Events
- Check Stripe dashboard → Webhooks → Recent deliveries
- Verify `WEBHOOK_SECRET` matches Stripe signing secret
- Ensure endpoint is publicly accessible (not localhost)

### Email Not Sending
- Verify `RESEND_API_KEY` is valid
- Check `logs/email_logs.jsonl` for delivery attempts
- Confirm `EMAIL_FROM` domain is verified in Resend

### CORS Errors on Telemetry
- Ensure `flask-cors` is installed: `pip install flask-cors`
- Verify CORS headers in response
- Check browser console for specific error message
