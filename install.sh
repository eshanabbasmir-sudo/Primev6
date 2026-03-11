#!/data/data/com.termux/files/usr/bin/bash

echo "🚀 Installing MR KING TIKTOK BOT..."

# Update packages
echo "📦 Updating packages..."
pkg update -y && pkg upgrade -y

# Install Python
echo "🐍 Installing Python..."
pkg install python -y

# Install Chromium
echo "🌐 Installing Chromium browser..."
pkg install chromium -y
pkg install chromium-chromedriver -y

# Install pip packages
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Check config
if ! grep -q "YOUR_BOT_TOKEN_HERE" config.py; then
    echo "✅ Bot token found in config.py"
else
    echo "⚠️ Please edit config.py and add your bot token!"
fi

# Check accounts
if [ -s accounts.json ]; then
    echo "✅ accounts.json found"
else
    echo "⚠️ Please add your accounts to accounts.json"
fi

echo ""
echo "✅ INSTALLATION COMPLETE!"
echo "▶️ Run: python app.py"
echo ""
