# Deploy LangGames to Railway

## Why Railway Instead of Vercel?

LangGames is a Python HTTP server, which doesn't work on Vercel (Node.js/serverless platform). Railway is perfect for Python applications and is free to start.

## Quick Deploy (5 Minutes)

### Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Sign in with GitHub

### Step 2: Deploy LangGames

1. Click "Deploy from GitHub repo"
2. Select your **LangGames** repository
3. Railway will automatically:
   - Detect Python
   - Install requirements from `requirements.txt`
   - Run `python LangGames.py`

### Step 3: Get Your Deployment URL

1. After deployment completes, click on your project
2. Click "Settings" → "Domains"
3. Click "Generate Domain"
4. You'll get a URL like: `langgames-production.up.railway.app`

### Step 4: Set Environment Variables (Optional)

1. Click "Variables" tab
2. Add these if you want custom config:
   ```
   PORT=9048
   HOST=0.0.0.0
   ```

### Step 5: Update WalkerAuth

Go back to WalkerAuth's `sites.json` and update:

```json
{
  "LangGames": {
    "redirect_url": "https://your-railway-url.up.railway.app/oauth/callback",
    "secret_key": "langgames_secret_key_12345"
  }
}
```

Replace `your-railway-url` with your actual Railway domain.

## Alternative: Use Custom Domain

If you want `langgames.walkerco.co`:

1. In Railway → Settings → Domains
2. Click "Custom Domain"
3. Enter: `langgames.walkerco.co`
4. Railway will give you a CNAME record
5. Add that CNAME to your DNS (Cloudflare, etc.)

## Testing

Once deployed:

1. Visit your Railway URL: `https://your-app.up.railway.app`
2. Should see LangGames game load!
3. Test OAuth: Visit `https://walkerauth.walkerco.co?id=LangGames`
4. Sign in with Google
5. Should redirect to LangGames with authentication!

## Troubleshooting

### Build Failed

Check Railway logs:
- Click on deployment
- View build logs
- Common issue: Missing dependencies in requirements.txt

### OAuth Callback Fails

- Make sure `redirect_url` in WalkerAuth sites.json matches your Railway URL
- Must end with `/oauth/callback`
- Use HTTPS not HTTP

### App Not Starting

- Check if `PORT` and `HOST` environment variables are set
- Railway automatically sets `PORT`, so your app should use `os.getenv('PORT')`

## Cost

- **Free tier**: 500 hours/month (plenty for development)
- **Pro**: $5/month for more resources

## Alternative Platforms

If you prefer something else:

### Render
- Free tier available
- Slower cold starts than Railway
- Add a `render.yaml` file

### Heroku
- $5/month minimum (no free tier anymore)
- More established platform

### PythonAnywhere
- Free tier available
- Good for learning/small projects
- Manual setup required

## Railway is Recommended

✅ Easy setup (auto-detects Python)
✅ Free tier available
✅ Fast deployments
✅ Good for Python web servers
✅ Custom domains supported

Railway is the best choice for LangGames!
