#!/usr/bin/env python3
# ===== MR KING TIKTOK BOT - TERMUX OPTIMIZED =====

# ===== PYTHON 3.14 TYPING PATCH =====
import typing
if not hasattr(typing, "UnionType"):
    typing.UnionType = type(int | str)
# ===================================

import asyncio
import json
import time
import os
import random
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import config

# ===== SELENIUM FOR TERMUX =====
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ===== LOGGING SETUP =====
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== GLOBAL VARIABLES =====
driver = None
active_accounts = []
bot_start_time = datetime.now()

# ===== ACCOUNT MANAGEMENT =====
def load_accounts():
    """Load accounts from JSON file"""
    try:
        with open("accounts.json", "r") as f:
            accounts = json.load(f)
        logger.info(f"✅ Loaded {len(accounts)} accounts")
        return accounts
    except FileNotFoundError:
        logger.error("❌ accounts.json not found!")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON error in accounts.json: {e}")
        return []

def save_accounts(accounts):
    """Save accounts to JSON file"""
    with open("accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)
    logger.info("✅ Accounts saved")

def get_random_user_agent():
    """Get random user agent"""
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "com.zhiliaoapp.musically/2024603040 (Linux; U; Android 13; en_US; Pixel 6; Build/TQ1A.230205.002; Cronet/TTNetVersion:017a3d8c)"
    ]
    return random.choice(agents)

# ===== BROWSER MANAGEMENT =====
def init_driver():
    """Initialize Chrome driver for Termux"""
    global driver
    
    options = Options()
    
    # Termux-specific options
    options.add_argument("--headless=new")  # Run in background
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"--user-agent={get_random_user_agent()}")
    
    # Experimental options
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Termux chromium path
    options.binary_location = "/data/data/com.termux/files/usr/bin/chromium"
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        logger.info("✅ Browser initialized")
        return True
    except Exception as e:
        logger.error(f"❌ Browser init failed: {e}")
        return False

def close_driver():
    """Close browser"""
    global driver
    if driver:
        try:
            driver.quit()
        except:
            pass
        driver = None

# ===== TIKTOK ACTIONS =====
def login_tiktok(email, password):
    """Login to TikTok"""
    global driver
    
    if not driver:
        if not init_driver():
            return False
    
    try:
        logger.info(f"🔑 Logging in: {email}")
        driver.get("https://www.tiktok.com/login/phone-or-email/email")
        time.sleep(config.LOGIN_WAIT)
        
        # Find and fill email
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        email_input.clear()
        for char in email:
            email_input.send_keys(char)
            time.sleep(random.uniform(0.05, 0.1))
        
        # Find and fill password
        password_input = driver.find_element(By.NAME, "password")
        password_input.clear()
        for char in password:
            password_input.send_keys(char)
            time.sleep(random.uniform(0.05, 0.1))
        
        # Submit
        password_input.send_keys(Keys.ENTER)
        time.sleep(config.LOGIN_WAIT)
        
        # Check if login successful
        if "login" not in driver.current_url.lower():
            logger.info(f"✅ Login successful: {email}")
            return True
        else:
            logger.warning(f"❌ Login failed: {email}")
            return False
            
    except TimeoutException:
        logger.error(f"⏰ Timeout for {email}")
        return False
    except Exception as e:
        logger.error(f"❌ Error logging in {email}: {str(e)[:50]}")
        return False

def follow_user(username):
    """Follow a TikTok user"""
    try:
        logger.info(f"👤 Following: @{username}")
        driver.get(f"https://www.tiktok.com/@{username}")
        time.sleep(config.ACTION_WAIT)
        
        # Try multiple selectors for follow button
        selectors = [
            '//button[contains(text(),"Follow")]',
            '//button[contains(@class,"Follow")]',
            '//button[@data-e2e="follow-button"]'
        ]
        
        for selector in selectors:
            try:
                follow_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                driver.execute_script("arguments[0].click();", follow_btn)
                time.sleep(2)
                logger.info("✅ Followed successfully")
                return True
            except:
                continue
        
        logger.warning("❌ Follow button not found")
        return False
        
    except Exception as e:
        logger.error(f"❌ Follow error: {str(e)[:50]}")
        return False

def like_video(video_url):
    """Like a TikTok video"""
    try:
        logger.info(f"❤️ Liking video")
        driver.get(video_url)
        time.sleep(config.ACTION_WAIT)
        
        # Wait for video to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "video"))
        )
        
        # Try multiple selectors for like button
        selectors = [
            '//span[@data-e2e="like-icon"]',
            '//button[@data-e2e="like-button"]',
            '//div[contains(@class,"LikeButton")]'
        ]
        
        for selector in selectors:
            try:
                like_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                
                # Check if already liked
                if 'active' in like_btn.get_attribute('class').lower():
                    logger.info("⏭️ Already liked")
                    return True
                
                driver.execute_script("arguments[0].click();", like_btn)
                time.sleep(2)
                logger.info("✅ Liked successfully")
                return True
            except:
                continue
        
        logger.warning("❌ Like button not found")
        return False
        
    except Exception as e:
        logger.error(f"❌ Like error: {str(e)[:50]}")
        return False

def comment_on_video(video_url, comment_text):
    """Comment on a TikTok video"""
    try:
        logger.info(f"💬 Commenting: {comment_text[:30]}...")
        driver.get(video_url)
        time.sleep(config.ACTION_WAIT)
        
        # Wait for comment box
        comment_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"]'))
        )
        
        # Type comment with human-like delay
        comment_box.click()
        for char in comment_text:
            comment_box.send_keys(char)
            time.sleep(random.uniform(0.03, 0.08))
        
        time.sleep(1)
        comment_box.send_keys(Keys.ENTER)
        time.sleep(3)
        
        logger.info("✅ Comment posted")
        return True
        
    except Exception as e:
        logger.error(f"❌ Comment error: {str(e)[:50]}")
        return False

# ===== TELEGRAM COMMANDS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    uptime = datetime.now() - bot_start_time
    hours = uptime.seconds // 3600
    minutes = (uptime.seconds % 3600) // 60
    
    keyboard = [
        [InlineKeyboardButton("📊 Status", callback_data="status"),
         InlineKeyboardButton("📁 Accounts", callback_data="accounts")],
        [InlineKeyboardButton("❓ Help", callback_data="help"),
         InlineKeyboardButton("ℹ️ Info", callback_data="info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👑 **MR KING TIKTOK BOT** 👑\n\n"
        f"⚡ Uptime: {hours}h {minutes}m\n"
        f"✅ Ready to rock!\n\n"
        f"**Commands:**\n"
        f"🔹 `/followall username`\n"
        f"🔹 `/likeall videolink`\n"
        f"🔹 `/commentall videolink text`\n"
        f"🔹 `/status`\n"
        f"🔹 `/help`",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot status"""
    accounts = load_accounts()
    uptime = datetime.now() - bot_start_time
    hours = uptime.seconds // 3600
    minutes = (uptime.seconds % 3600) // 60
    
    await update.message.reply_text(
        f"📊 **BOT STATUS**\n\n"
        f"⏰ Uptime: {hours}h {minutes}m\n"
        f"📁 Accounts: {len(accounts)}\n"
        f"🌐 Browser: {'✅ Active' if driver else '❌ Inactive'}\n"
        f"⚡ Mode: Termux Optimized"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = """
📚 **HOW TO USE**

1️⃣ **Follow All**
   `/followall username`
   Example: `/followall tiktok`

2️⃣ **Like All**
   `/likeall videolink`
   Example: `/likeall https://www.tiktok.com/@user/video/123`

3️⃣ **Comment All**
   `/commentall videolink text`
   Example: `/commentall https://www.tiktok.com/@user/video/123 nice video`

⚠️ Bot will use ALL accounts in accounts.json
⏱️ Each action takes {config.ACTION_WAIT} seconds
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def followall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Follow user with all accounts"""
    if not context.args:
        await update.message.reply_text("❌ Usage: /followall username")
        return
    
    username = context.args[0]
    accounts = load_accounts()
    
    if not accounts:
        await update.message.reply_text("❌ No accounts found in accounts.json")
        return
    
    status_msg = await update.message.reply_text(f"🔄 Following @{username} with {len(accounts)} accounts...")
    
    success = 0
    failed = 0
    
    for i, acc in enumerate(accounts):
        try:
            # Login
            if login_tiktok(acc["email"], acc["password"]):
                # Follow
                if follow_user(username):
                    success += 1
                else:
                    failed += 1
            else:
                failed += 1
            
            # Progress update
            if (i + 1) % 2 == 0:
                await status_msg.edit_text(f"🔄 Progress: {i+1}/{len(accounts)} | ✅ {success} | ❌ {failed}")
            
            # Random delay between accounts
            time.sleep(config.SWITCH_GAP + random.uniform(2, 5))
            
        except Exception as e:
            logger.error(f"Error: {e}")
            failed += 1
    
    # Close browser
    close_driver()
    
    # Final report
    await status_msg.edit_text(
        f"✅ **FOLLOW COMPLETE**\n\n"
        f"👤 Target: @{username}\n"
        f"✅ Success: {success}\n"
        f"❌ Failed: {failed}\n"
        f"📊 Total: {len(accounts)}"
    )

async def likeall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Like video with all accounts"""
    if not context.args:
        await update.message.reply_text("❌ Usage: /likeall videolink")
        return
    
    video_link = context.args[0]
    accounts = load_accounts()
    
    if not accounts:
        await update.message.reply_text("❌ No accounts found in accounts.json")
        return
    
    status_msg = await update.message.reply_text(f"🔄 Liking video with {len(accounts)} accounts...")
    
    success = 0
    failed = 0
    
    for i, acc in enumerate(accounts):
        try:
            if login_tiktok(acc["email"], acc["password"]):
                if like_video(video_link):
                    success += 1
                else:
                    failed += 1
            else:
                failed += 1
            
            if (i + 1) % 2 == 0:
                await status_msg.edit_text(f"🔄 Progress: {i+1}/{len(accounts)} | ✅ {success} | ❌ {failed}")
            
            time.sleep(config.SWITCH_GAP + random.uniform(2, 5))
            
        except Exception as e:
            logger.error(f"Error: {e}")
            failed += 1
    
    close_driver()
    
    await status_msg.edit_text(
        f"✅ **LIKE COMPLETE**\n\n"
        f"❤️ Success: {success}\n"
        f"❌ Failed: {failed}\n"
        f"📊 Total: {len(accounts)}"
    )

async def commentall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comment on video with all accounts"""
    if len(context.args) < 2:
        await update.message.reply_text("❌ Usage: /commentall videolink text")
        return
    
    video_link = context.args[0]
    comment_text = " ".join(context.args[1:])
    accounts = load_accounts()
    
    if not accounts:
        await update.message.reply_text("❌ No accounts found in accounts.json")
        return
    
    status_msg = await update.message.reply_text(f"🔄 Commenting with {len(accounts)} accounts...")
    
    success = 0
    failed = 0
    
    for i, acc in enumerate(accounts):
        try:
            if login_tiktok(acc["email"], acc["password"]):
                if comment_on_video(video_link, comment_text):
                    success += 1
                else:
                    failed += 1
            else:
                failed += 1
            
            if (i + 1) % 2 == 0:
                await status_msg.edit_text(f"🔄 Progress: {i+1}/{len(accounts)} | ✅ {success} | ❌ {failed}")
            
            time.sleep(config.SWITCH_GAP + random.uniform(2, 5))
            
        except Exception as e:
            logger.error(f"Error: {e}")
            failed += 1
    
    close_driver()
    
    await status_msg.edit_text(
        f"✅ **COMMENT COMPLETE**\n\n"
        f"💬 Text: {comment_text[:30]}...\n"
        f"✅ Success: {success}\n"
        f"❌ Failed: {failed}\n"
        f"📊 Total: {len(accounts)}"
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "status":
        accounts = load_accounts()
        uptime = datetime.now() - bot_start_time
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60
        await query.edit_message_text(
            f"📊 **STATUS**\n\n"
            f"⏰ Uptime: {hours}h {minutes}m\n"
            f"📁 Accounts: {len(accounts)}\n"
            f"🌐 Browser: {'✅ Active' if driver else '❌ Inactive'}"
        )
    
    elif query.data == "accounts":
        accounts = load_accounts()
        text = "📁 **ACCOUNTS**\n\n"
        for i, acc in enumerate(accounts, 1):
            text += f"{i}. {acc['email']}\n"
        await query.edit_message_text(text)
    
    elif query.data == "help":
        await query.edit_message_text(
            "📚 **COMMANDS**\n\n"
            "/followall username\n"
            "/likeall link\n"
            "/commentall link text\n"
            "/status\n"
            "/help"
        )
    
    elif query.data == "info":
        await query.edit_message_text(
            "ℹ️ **MR KING TIKTOK BOT**\n\n"
            "Version: 2.0\n"
            "Optimized for: Termux\n"
            "Author: @YourUsername\n\n"
            "⚠️ Educational Purpose Only"
        )

# ===== MAIN =====
def main():
    """Main function"""
    global bot_start_time
    
    # Check config
    if not config.BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not set in config.py")
        return
    
    # Check accounts.json
    accounts = load_accounts()
    if not accounts:
        logger.warning("⚠️ No accounts found in accounts.json")
    
    # Create application
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("followall", followall))
    app.add_handler(CommandHandler("likeall", likeall))
    app.add_handler(CommandHandler("commentall", commentall))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Start bot
    bot_start_time = datetime.now()
    logger.info("👑 Mr King Bot Started!")
    logger.info(f"📁 Loaded {len(accounts)} accounts")
    logger.info("🚀 Bot is running...")
    
    # Run
    app.run_polling()

if __name__ == "__main__":
    main()
