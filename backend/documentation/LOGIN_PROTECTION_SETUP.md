# Combat Protocol - Login Protection Setup

## 🔒 Security Features Added

Your Combat Protocol application now includes:

1. **Session-based authentication** - Single shared password protection
2. **robots.txt** - Discourages search engine crawling
3. **noindex meta tags** - Tells search engines not to index pages
4. **Protected routes** - All main pages and API endpoints require login

---

## 📦 Files Updated

### Backend
- **app.py** - Added login system, session management, and route protection

### Templates
- **index.html** - Added `<meta name="robots" content="noindex, nofollow">`
- **model_test.html** - Added `<meta name="robots" content="noindex, nofollow">`

---

## 🚀 Local Setup

### 1. Generate a Secret Key

Run this command to generate a secure random key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output (it will look like: `a1b2c3d4e5f6...`)

### 2. Create/Update .env File

Create a `.env` file in your project root (or update existing one):

```bash
# Flask secret key for sessions (generate with command above)
SECRET_KEY=your-generated-secret-key-here

# Site password (choose something secure)
SITE_PASSWORD=your-chosen-password-here

# Your existing API keys
ANTHROPIC_API_KEY=your-anthropic-key
OPENAI_API_KEY=your-openai-key
```

### 3. Test Locally

```bash
# Activate your virtual environment
source venv/bin/activate

# Run the app
python app.py
```

Visit `http://127.0.0.1:5001` - you should see the login page!

---

## 🌐 Render.com Deployment

### 1. Update Environment Variables on Render

Go to your Render dashboard:
- Navigate to your Combat Protocol service
- Go to **Environment** tab
- Add these new environment variables:

```
SECRET_KEY = [paste the generated secret key]
SITE_PASSWORD = [your chosen password]
```

**Important:** Make sure these are set as **Secret** variables!

### 2. Deploy Updated Code

```bash
# Commit your changes
git add app.py templates/index.html templates/model_test.html
git commit -m "Add login protection system"

# Push to GitHub
git push origin main
```

Render will automatically detect the changes and redeploy.

### 3. Test Production

Visit `https://combatprotocol.com` (or your Render URL)
- You should see the login page
- Enter your password
- You should be redirected to the main app

---

## 🔑 Protected Routes

The following routes now require authentication:

- `/` - Main fighter selection page
- `/model-test` - 3D model test page
- `/api/fighters` - Get list of fighters
- `/api/simulate/<fighter_a>/<fighter_b>` - Simulate fights
- `/api/fighter/<fighter_id>` - Get fighter details
- `/api/generate-fighter` - Generate custom fighters

### Public Routes (No Login Required)

- `/login` - Login page (obviously!)
- `/logout` - Clear session
- `/robots.txt` - Search engine instructions
- `/api/version` - Version check endpoint

---

## 🔐 Security Notes

### Current Implementation (Simple Password)

✅ **Pros:**
- Quick to implement
- No database needed
- Easy to share with Niki or other collaborators
- Single password = single point of control

⚠️ **Limitations:**
- Everyone shares the same password
- No individual user tracking
- Can't revoke access for specific people
- Session stored in browser cookie (cleared on logout or browser close)

### Future Enhancements (When Needed)

If you want to upgrade later:

1. **Individual user accounts** - Each person has their own login
2. **Password hashing** - Store hashed passwords instead of plain text
3. **User roles** - Admin vs viewer access levels
4. **Database storage** - Track users and sessions properly
5. **Password reset** - Email-based recovery system
6. **Two-factor auth** - Extra security layer

For now, the simple approach protects your IP while keeping things lightweight.

---

## 🎨 Customizing the Login Page

The login page template is embedded in `app.py` (lines 63-141). To customize:

1. Find the `LOGIN_PAGE` variable
2. Modify the HTML/CSS as needed
3. Keep the form fields: `<input type="password" name="password">`

---

## 🔍 Search Engine Protection

Three layers of protection from search engines:

### 1. robots.txt
Route: `/robots.txt`
```
User-agent: *
Disallow: /
```
Tells search engines: "Don't crawl this site"

### 2. noindex Meta Tag
In `<head>` of templates:
```html
<meta name="robots" content="noindex, nofollow">
```
Tells search engines: "Don't index this page, don't follow links"

### 3. Login Gate
The strongest protection - pages aren't accessible without authentication.

**Note:** Already-indexed pages may take time to drop from search results. You can use Google Search Console to request removal if needed.

---

## 🧪 Testing Checklist

- [ ] Can access login page at `/login`
- [ ] Wrong password shows error message
- [ ] Correct password redirects to main page
- [ ] Session persists across page navigation
- [ ] `/logout` clears session and redirects to login
- [ ] Direct access to `/` redirects to login when not authenticated
- [ ] API endpoints return 302 redirect when not authenticated
- [ ] robots.txt accessible at `/robots.txt`
- [ ] Meta tags present in page source

---

## 🆘 Troubleshooting

### "Using default SECRET_KEY" warning
**Problem:** Environment variable not set
**Solution:** Add `SECRET_KEY` to your `.env` file or Render environment

### "Using default password 'fubar'" warning
**Problem:** Environment variable not set
**Solution:** Add `SITE_PASSWORD` to your `.env` file or Render environment

### Can't login / "Incorrect password"
**Problem:** Password mismatch or session issues
**Solution:** 
1. Double-check the password in your `.env` or Render settings
2. Clear browser cookies/cache
3. Try incognito/private browsing window

### Already logged in but can't access pages
**Problem:** Session cookie issues
**Solution:**
1. Visit `/logout` to clear session
2. Clear browser cookies
3. Log in again

### Search engines still showing the site
**Problem:** Previously indexed pages take time to drop
**Solution:**
- Give it time (weeks to months)
- Use Google Search Console to request removal
- The login gate prevents new crawling

---

## 📝 Version History

- **v0.2.0** - Added login protection system (Jan 2026)
- **v0.1.2** - Event-based architecture with SSE streaming
- **v0.1.0** - Initial Combat Protocol release

---

## 🤝 Sharing Access

To give someone access:
1. Share the password (via secure channel - Signal, encrypted email, etc.)
2. They visit combatprotocol.com
3. Enter the password
4. They're in!

To revoke access:
1. Change the `SITE_PASSWORD` environment variable
2. Redeploy (or restart server)
3. Everyone needs the new password

---

## Questions?

This setup protects your IP while keeping the system simple and easy to manage. As Combat Protocol grows, you can always upgrade to a more sophisticated auth system.

For now, enjoy your password-protected fighting simulator! 🥊
