# Email Configuration Guide for SunSavvy

## Gmail SMTP Setup

To receive actual emails (instead of console output), you need to configure Gmail SMTP.

### Step 1: Enable 2-Step Verification
1. Go to your Google Account: https://myaccount.google.com/
2. Click on **Security**
3. Under "Signing in to Google", enable **2-Step Verification**

### Step 2: Generate App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Select **Mail** and **Other (Custom name)**
3. Enter "SunSavvy Django" as the name
4. Click **Generate**
5. **Copy the 16-character password** (you'll need this)

### Step 3: Set Environment Variables

#### Option A: Using Windows PowerShell (Temporary - for current session)
```powershell
$env:EMAIL_HOST_USER="your-email@gmail.com"
$env:EMAIL_HOST_PASSWORD="your-16-character-app-password"
$env:DEFAULT_FROM_EMAIL="SunSavvy <your-email@gmail.com>"
```

#### Option B: Create a `.env` file (Recommended)
1. Create a file named `.env` in the project root (same folder as `manage.py`)
2. Add these lines:
```
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-app-password
DEFAULT_FROM_EMAIL=SunSavvy <your-email@gmail.com>
```

3. Install python-decouple (if not already installed):
```powershell
pip install python-decouple
```

4. Update `sunsavvy/settings.py` to use python-decouple:
```python
from decouple import config

EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='SunSavvy <noreply@sunsavvy.com>')
```

### Step 4: Restart Django Server
After setting the environment variables, restart your Django server:
```powershell
python manage.py runserver
```

### Testing Email
1. Register as an Authorized Person
2. Check your Gmail inbox (and spam folder)
3. You should receive the verification email

## Troubleshooting

### Email still not received?
1. Check the terminal/console - if you see email content printed, it means SMTP is not configured
2. Verify your App Password is correct (16 characters, no spaces)
3. Make sure 2-Step Verification is enabled
4. Check spam/junk folder
5. Verify EMAIL_HOST_USER matches the Gmail account that generated the App Password

### Security Note
- Never commit `.env` file to Git
- Add `.env` to `.gitignore`
- App Passwords are safer than using your main Gmail password

