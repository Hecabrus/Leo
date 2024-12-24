from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaAnimation, InputMediaPhoto, CallbackQuery
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
import sqlite3
import logging
import time
import random
import asyncio
import secrets
import string
import urllib.parse

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Content Configuration
WELCOME_PAGE = {
    "gif": "https://i.giphy.com/media/CbPf7NXAU569vRxQgp/giphy.gif",
    "text": "🌟 *Welcome, Pal ^ ^* 🌟\n\n"
            "Get exclusive access to premium accounts:\n"
            "• 🔒 Multiple Premium Services\n"
            "• 💫 Daily Updates\n"
            "• 🎯 Instant Access",
    "type": "animation"
}

VERIFICATION_PAGE = {
    "gif": "https://i.giphy.com/media/Mf7MqY4Er2ET8z6o0X/giphy.gif",
    "text": "🔒 *Secure Verification Required* 🔒\n\n"
            "*To unlock your premium access:*\n"
            "1️⃣ Join our Official Channel\n"
            "2️⃣ Join our Updates Channel\n\n"
            "Click below to proceed! 🚀",
    "type": "animation"
}

VERIFIED_WELCOME_PAGE = {
    "gif": "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExOXlic29taG90NWo5NHJqZTJ1b2hhMWxmZmp5a3E2bnQyZ2MwY291bCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/NoKbW9kNRmi9dJhH1q/giphy.gif",
    "text": "🎉 *{greeting}, {username}!* 🎉\n\n"
            "Hey there! Ready for free premium perks? 🎁 Roll in and dive into exclusive access!\n",
    "type": "animation"
}

SERVICES_PAGE = {
    "gif": "https://i.giphy.com/media/ET4GoCG0BV0Ln9S0ec/giphy.gif",
    "text": "🌟 *Premium Services Available* 🌟\n\n"
            "Select a service to view accounts:",
    "type": "animation"
}

REFERRAL_PAGE = {
    "gif": "https://i.giphy.com/media/ET4GoCG0BV0Ln9S0ec/giphy.gif",
    "text": "🎯 Invite friends to this group and make them complete verification to earn referral points!\n\n"
            "Tap on 'Invite User' to share your referral link with friends.",
    "type": "animation"
}

PROGRESS_PAGE = {
    "gif": "https://i.giphy.com/media/ET4GoCG0BV0Ln9S0ec/giphy.gif",
    "text": "📊 *Your Current Progress* 📊\n\n"
            "Current Referrals: 0/3",
    "type": "animation"
}

UNLOCK_PAGE = {
    "gif": "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExNGZzZnFpbmh4amZlMGV4MnBqZHk0YjZsaDJtbWVsZjIxcGZqNXhxaSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/HZrx8kjIA7lyeTqXVM/giphy.gif",
    "text": "🎉 *Congratulations!* 🎉\n\n"
            "You've completed the task! You will receive your account via this bot once it's approved by the manager.\n\n"
            "Stay tuned! 🌟",
    "type": "animation"
}

# Service Configuration
SERVICES = {
    'chatgpt': {
        'name': '🤖 ChatGPT',
        'type': 'referral'
    },
    'youtube': {
        'name': '🎥 YouTube Premium',
        'type': 'referral'
    },
    'spotify': {
        'name': '🎵 Spotify',
        'type': 'referral'
    },
    'netflix': {
        'name': '🎬 Netflix',
        'type': 'referral'
    },
    'nordvpn': {
        'name': '🔐 NordVPN',
        'file': 'nordvpn.txt',
        'image': 'https://imgur.com/a/3Zw7aTa.jpeg'
    },
    'xbox': {
        'name': '🎮 Xbox Pass',
        'file': 'xbox.txt',
        'image': 'https://imgur.com/a/cunXOPK.jpeg'
    },
    'capcut': {
        'name': '✂️ CapCut',
        'file': 'capcut.txt',
        'image': 'https://imgur.com/a/JopZidN.jpeg'
    },
    'wondershare': {
        'name': '🎨 Wondershare',
        'file': 'wondershare.txt',
        'image': 'https://imgur.com/a/xEbOjHL.jpeg'
    },
    'duolingo': {
        'name': '🗣️ Duolingo',
        'file': 'duolingo.txt',
        'image': 'https://imgur.com/a/XmZZT0N.jpeg'
    },
    'crunchyroll': {
        'name': '🎌 Crunchyroll',
        'file': 'crunchyroll.txt',
        'image': 'https://imgur.com/a/LPh2OwJ.jpeg'
    },
    'hotmail': {
        'name': '📧 Hotmail',
        'file': 'hotmail.txt',
        'image': 'https://imgur.com/a/5Y9KHzd.jpeg'
    }
}

class Database:
    def __init__(self):
        with sqlite3.connect('bot_users.db') as conn:
            c = conn.cursor()
            # Create users table
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    verification_started TEXT,
                    verification_completed INTEGER DEFAULT 0,
                    last_verification_attempt TEXT,
                    referral_code TEXT UNIQUE,
                    referrer_id INTEGER,
                    FOREIGN KEY (referrer_id) REFERENCES users (user_id)
                )
            ''')
            
            # Create service-specific referrals table
            c.execute('''
                CREATE TABLE IF NOT EXISTS service_referrals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_id INTEGER,
                    referee_id INTEGER,
                    service_id TEXT,
                    created_at TEXT,
                    verified_at TEXT,
                    status TEXT,
                    notification_sent INTEGER DEFAULT 0,
                    FOREIGN KEY (referrer_id) REFERENCES users (user_id),
                    FOREIGN KEY (referee_id) REFERENCES users (user_id)
                )
            ''')
            
            # Create service unlocks table
            c.execute('''
                CREATE TABLE IF NOT EXISTS service_unlocks (
                    user_id INTEGER,
                    service_id TEXT,
                    unlocked_at TEXT,
                    PRIMARY KEY (user_id, service_id),
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            conn.commit()
            
    def generate_referral_code(self):
        while True:
            code = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
            with sqlite3.connect('bot_users.db') as conn:
                c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM users WHERE referral_code = ?", (code,))
                if c.fetchone()[0] == 0:
                    return code
                    
    def deduct_referral_point(self, referrer_id, referee_id, service_id=None):
        """
        Deduct referral point when a referee leaves the channel.
        Returns True if point was deducted, False otherwise.
        """
        with sqlite3.connect('bot_users.db') as conn:
            c = conn.cursor()
            
            # Find and update the referral record
            if service_id:
                c.execute('''
                    UPDATE service_referrals 
                    SET status = 'revoked',
                        notification_sent = 0
                    WHERE referrer_id = ? 
                    AND referee_id = ? 
                    AND service_id = ?
                    AND status = 'completed'
                    RETURNING id
                ''', (referrer_id, referee_id, service_id))
            else:
                c.execute('''
                    UPDATE service_referrals 
                    SET status = 'revoked',
                        notification_sent = 0
                    WHERE referrer_id = ? 
                    AND referee_id = ? 
                    AND status = 'completed'
                    RETURNING id
                ''', (referrer_id, referee_id))
                
            result = c.fetchone()
            conn.commit()
            return bool(result)

    def get_referrer_info(self, referee_id):
        """
        Get referrer information for a given referee.
        """
        with sqlite3.connect('bot_users.db') as conn:
            c = conn.cursor()
            c.execute('''
                SELECT DISTINCT sr.referrer_id, sr.service_id, u.first_name
                FROM service_referrals sr
                JOIN users u ON u.user_id = sr.referee_id
                WHERE sr.referee_id = ? AND sr.status = 'completed'
            ''', (referee_id,))
            return c.fetchall()

    def add_user(self, user_id, first_name, referrer_code=None, service_id=None):
        with sqlite3.connect('bot_users.db') as conn:
            c = conn.cursor()
            
            # Check if user exists
            c.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            if c.fetchone() is not None:
                return
            
            # Generate new referral code
            new_referral_code = self.generate_referral_code()
            
            # Get referrer_id if referral code provided
            referrer_id = None
            if referrer_code:
                c.execute("SELECT user_id FROM users WHERE referral_code = ?", (referrer_code,))
                result = c.fetchone()
                if result:
                    referrer_id = result[0]
            
            # Insert new user
            c.execute('''
                INSERT INTO users 
                (user_id, first_name, verification_started, verification_completed, 
                 referral_code, referrer_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, first_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                 0, new_referral_code, referrer_id))
            
            # Create service-specific referral record if there's a referrer
            if referrer_id and service_id:
                c.execute('''
                    INSERT INTO service_referrals 
                    (referrer_id, referee_id, service_id, created_at, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (referrer_id, user_id, service_id, 
                     datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'pending'))
            
            conn.commit()
            
    def check_and_unlock_service(self, user_id, service_id):
        with sqlite3.connect('bot_users.db') as conn:
            c = conn.cursor()
            stats = self.get_service_referral_stats(user_id, service_id)
            
            if stats['completed_referrals'] >= 5 and not stats['is_unlocked']:
                c.execute('''
                    INSERT INTO service_unlocks (user_id, service_id, unlocked_at)
                    VALUES (?, ?, ?)
                ''', (user_id, service_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
                return True
            return False
            
    def get_service_referral_stats(self, user_id, service_id):
        with sqlite3.connect('bot_users.db') as conn:
            c = conn.cursor()
            
            # Get completed referrals for specific service
            c.execute('''
                SELECT COUNT(*) 
                FROM service_referrals 
                WHERE referrer_id = ? AND service_id = ? AND status = 'completed'
            ''', (user_id, service_id))
            completed_referrals = c.fetchone()[0]
            
            # Check if service is unlocked
            c.execute('''
                SELECT COUNT(*) 
                FROM service_unlocks 
                WHERE user_id = ? AND service_id = ?
            ''', (user_id, service_id))
            is_unlocked = c.fetchone()[0] > 0
            
            return {
                'completed_referrals': completed_referrals,
                'is_unlocked': is_unlocked
            }
            
    def get_referral_stats(self, user_id):
        with sqlite3.connect('bot_users.db') as conn:
            c = conn.cursor()
            c.execute('''
                SELECT COUNT(*) 
                FROM referrals 
                WHERE referrer_id = ? AND status = 'completed'
            ''', (user_id,))
            completed_referrals = c.fetchone()[0]
            
            c.execute('''
                SELECT referral_points, premium_unlocked
                FROM users
                WHERE user_id = ?
            ''', (user_id,))
            user_stats = c.fetchone()
            
            return {
                'completed_referrals': completed_referrals,
                'points': user_stats[0] if user_stats else 0,
                'premium_unlocked': user_stats[1] if user_stats else 0
            }

    def get_user(self, user_id):
        with sqlite3.connect('bot_users.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            return c.fetchone()
            
    def check_and_unlock_premium(self, user_id):
        with sqlite3.connect('bot_users.db') as conn:
            c = conn.cursor()
            stats = self.get_referral_stats(user_id)
            
            if stats['completed_referrals'] >= 5 and not stats['premium_unlocked']:
                c.execute('''
                    UPDATE users
                    SET premium_unlocked = 5
                    WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
                return True
            return False

    def update_user_verification(self, user_id, completed):
        """Update user verification status and handle referral notifications"""
        with sqlite3.connect('bot_users.db') as conn:
            c = conn.cursor()
            
            # Update user verification status
            c.execute('''
                UPDATE users 
                SET verification_completed = ?,
                    last_verification_attempt = ?
                WHERE user_id = ?
            ''', (completed, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_id))
            
            if completed:
                # Get all pending referrals for this user
                c.execute('''
                    SELECT r.referrer_id, r.service_id, r.id, u.first_name
                    FROM service_referrals r
                    JOIN users u ON u.user_id = r.referee_id
                    WHERE r.referee_id = ? AND r.status = 'pending' AND r.notification_sent = 0
                ''', (user_id,))
                pending_referrals = c.fetchall()
                
                notifications = []
                # Update each pending referral
                for referrer_id, service_id, referral_id, referee_name in pending_referrals:
                    c.execute('''
                        UPDATE service_referrals
                        SET status = ?, verified_at = ?, notification_sent = 1
                        WHERE id = ?
                    ''', ('completed', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), referral_id))
                    
                    # Get service name
                    service_name = SERVICES[service_id]['name'] if service_id in SERVICES else "Premium"
                    
                    # Create notification message
                    notification = {
                        'referrer_id': referrer_id,
                        'message': (
                            f"🎉 *Referral Success!*\n\n"
                            f"Your friend {referee_name} has completed verification for "
                            f"{service_name} access!\n\n"
                            
                            "• Keep inviting friends to unlock premium access!"
                        )
                    }
                    notifications.append(notification)
            
            conn.commit()
            return notifications if completed else []
            
    def mark_notification_sent(self, referral_id):
        """Mark a referral notification as sent"""
        with sqlite3.connect('bot_users.db') as conn:
            c = conn.cursor()
            c.execute('''
                UPDATE service_referrals
                SET notification_sent = 1
                WHERE id = ?
            ''', (referral_id,))
            conn.commit()
            
    def get_pending_notifications(self, referrer_id):
        """Get all pending notifications for a referrer"""
        with sqlite3.connect('bot_users.db') as conn:
            c = conn.cursor()
            c.execute('''
                SELECT r.id, u.first_name, s.name
                FROM service_referrals r
                JOIN users u ON u.user_id = r.referee_id
                JOIN services s ON s.id = r.service_id
                WHERE r.referrer_id = ? AND r.status = 'completed' AND r.notification_sent = 0
            ''', (referrer_id,))
            return c.fetchall()
       
    def update_referral_points(self, user_id, points):
        with sqlite3.connect('bot_users.db') as conn:
            c = conn.cursor()
            c.execute('''
                UPDATE users 
                SET referral_points = referral_points + ? 
                WHERE user_id = ?
            ''', (points, user_id))
            conn.commit()

class Bot:
    def __init__(self):
        self.db = Database()
        self.channel1_link = "https://t.me/maxxxystore"
        self.channel2_link = "https://t.me/hecabruss"
        self.channel2_id = "@hecabruss"
        self.service_accounts = {}
        self.load_all_accounts()
        self.referral_link = "Google.com"
        self.bot_username = "Ishteros_bot"
        self.referral_services = {'netflix', 'chatgpt', 'spotify', 'youtube'}
        self.unlock_timestamps = {}
        self.didnt_get_account_clicked = {}
        self.reverify_button_visible = {}
        self.help_button_visible = {}
        self.reverify_status = {}
        self.reverify_requests = {}  # Track reverify requests per user
        self.voice_message_sent = set()  # Track users who received voice messages

        # Replace the file paths with Telegram file IDs
        self.english_voice_file_id = "CQACAgUAAxkBAAIE3GdLBK7FhSkXrzm4_EqTPFaBrlMLAALBEQACyuZYVrrx7HkwKqSoNgQ"
        self.hindi_voice_file_id = "CQACAgUAAxkBAAIE3WdLBK436dLP9H0nLfw78dy-v314AALCEQACyuZYVqtEHjqWLdETNgQ"  # Replace with actual Hindi file ID if different

        # Help page configuration
        self.HELP_PAGE = {
            "image": "https://imgur.com/a/5woLdBZ.jpeg",
            "text": "Choose your option:",
            "type": "photo"
        }

        self.LIVE_CHAT_PAGE = {
            "image": "https://imgur.com/a/5woLdBZ.jpeg",
            "text": "Select your desired problem",
            "type": "photo"
        }

        # Task and Spin page configurations
        self.TASKS_PAGE = {
            "gif": "https://i.giphy.com/media/ET4GoCG0BV0Ln9S0ec/giphy.gif",
            "text": "Choose any task to skip a referral point",
            "type": "animation"
        }

        self.SPIN_PAGE = {
            "image": "https://imgur.com/a/DwCgikc.jpeg",
            "text": (
                "Hey there, Buddy 🍭\n\n"
                "• First, click on 'Spin Now' option to begin your journey! 💕\n\n"
                "• You'll be taken to a Web bot. Inside, join the channel and spin the wheel for fun! 🎡\n\n"
                "• Once you've spun the wheel, come back here to continue!\n\n"
                "• Click 'completed' option, and get ready for a point! 🥳"
            ),
            "type": "photo"
        }

        # Existing GIFs and page templates
        self.referral_gif = "https://i.giphy.com/media/ET4GoCG0BV0Ln9S0ec/giphy.gif"
        self.services_gif = "https://i.giphy.com/media/ET4GoCG0BV0Ln9S0ec/giphy.gif"
        self.progress_gif = "https://i.giphy.com/media/ET4GoCG0BV0Ln9S0ec/giphy.gif"

        self.page_templates = {
            'referral': {
                'gif': self.referral_gif,
                'text': (
                    "🎯 *Share Premium Access*\n\n"
                    "Share your exclusive invitation with friends!\n\n"
                    "📱 *How it works:*\n"
                    "1️⃣ Click 'Share with Friends'\n"
                    "2️⃣ Select friends to share with\n"
                    "3️⃣ They verify & you get rewards!"
                )
            },
            'services': {
                'gif': self.services_gif,
                'text': "Choose a service to access premium accounts:"
            },
            'progress': {
                'gif': self.progress_gif,
                'text': "Check your referral progress:"
            }
        }
        self.spin_timers = {}  # Store user spin timers
        self.spin_started = {}  # Track if user started spinning
        self.current_service = {}  # Track current service for each user
        self.spin_revealed = {}  # Add this to track permanently revealed spin states
        self.skip_point_used = set()  # Add this to track users who have used their skip option

    def load_all_accounts(self):
        for service_id, service_info in SERVICES.items():
            if 'file' in service_info:
                self.service_accounts[service_id] = self.load_accounts(service_info['file'])
                
    def requires_referral(self, service_id):
        """Check if a service requires referral"""
        return service_id.lower() in self.referral_services

    def load_accounts(self, filename):
        try:
            with open(filename, 'r') as file:
                return [line.strip().split(':') for line in file.readlines()]
        except FileNotFoundError:
            logger.error(f"Account file {filename} not found")
            return []            
        
    def format_referral_message(self, username, referral_link):
        """Generate an engaging referral message"""
        message = (
            "🎁 *Exclusive Premium Access Invitation!* 🎁\n\n"
            "Hey there! I've found an amazing opportunity to get *FREE* premium accounts for various services!\n\n"
            "✨ *What You Get:*\n"
            "• Premium accounts for Netflix, Spotify, YouTube & more\n"
            "• Instant access after verification\n"
            "• 100% Free through referral system\n\n"
            "🔥 *Limited Time Offer*\n"
            f"Join now through my exclusive link:\n{referral_link}\n\n"
            "Don't miss out on this amazing opportunity! 🚀"
        )
        return message

    def get_greeting(self):
        current_hour = datetime.now().hour
        if 5 <= current_hour < 12:
            return "Good morning"
        elif 12 <= current_hour < 17:
            return "Good afternoon"
        else:
            return "Good evening"
            
    def build_progress_bar(self, percentage):
        """Creates a visual progress bar based on percentage"""
        bar_length = 10
        filled = int(bar_length * (percentage / 100))
        bar = '■' * filled + '□' * (bar_length - filled)
        return f"[{bar}] {percentage}%"

    def build_services_keyboard(self, page=0):
        items_per_page = 4
        services_list = list(SERVICES.items())
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        current_services = services_list[start_idx:end_idx]
        
        keyboard = []
        for service_id, service_info in current_services:
            keyboard.append([
                InlineKeyboardButton(service_info['name'], 
                                   callback_data=f"service_{service_id}")
            ])
            
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("⬅️ Previous", 
                                              callback_data=f"service_page_{page-1}"))
        if end_idx < len(services_list):
            nav_row.append(InlineKeyboardButton("Next ➡️", 
                                              callback_data=f"service_page_{page+1}"))
        if nav_row:
            keyboard.append(nav_row)
            
        return InlineKeyboardMarkup(keyboard)

    def build_referral_service_keyboard(self, service_id):
        keyboard = [
            [InlineKeyboardButton("🎁 Get Referral", callback_data=f"get_referral_{service_id}")],
            [InlineKeyboardButton("📊 Check Progress", callback_data=f"check_progress_{service_id}")],
            [InlineKeyboardButton("🔙 Back to Services", callback_data="back_to_services")]
        ]
        return InlineKeyboardMarkup(keyboard)

    def build_referral_page_keyboard(self, service_id):
        keyboard = [
            [InlineKeyboardButton("📲 Invite User", url=self.referral_link)],
            [InlineKeyboardButton("🔙 Back", callback_data=f"service_{service_id}")]
        ]
        return InlineKeyboardMarkup(keyboard)
        
    def generate_referral_link(self, user_code):
        """Generates a referral link for the given user code."""
        return f"https://t.me/{self.bot_username}?start={user_code}"
        
    def create_share_url(self, referral_link, share_text):
        """Creates a Telegram share URL with the referral link and text."""
        encoded_text = urllib.parse.quote(share_text)
        return f"https://t.me/share/url?url={urllib.parse.quote(referral_link)}&text={encoded_text}"

    def build_progress_page_keyboard(self, service_id):
        keyboard = [
            [InlineKeyboardButton("🔓 Unlock", callback_data=f"unlock_{service_id}")],
            [InlineKeyboardButton("🔙 Back", callback_data=f"service_{service_id}")]
        ]
        return InlineKeyboardMarkup(keyboard)

    def build_unlock_page_keyboard(self):
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Services", callback_data="back_to_services")]
        ]
        return InlineKeyboardMarkup(keyboard)
        
    async def show_live_chat(self, query: CallbackQuery, service_id):
        """Display the live chat options based on selected language."""
        language = query.data.split('_')[1]  # Extract 'hindi' or 'english'

        # Define text content for each language
        texts = {
            'english': {
                'title': "📱 *Live Chat Support* 📱\n\n",
                'problem_text': "Please select your issue:",
                'options': [
                    "❌ Didn't get your account?"
                ]
            },
            'hindi': {
                'title': "📱 *लाइव चैट सहायता* 📱\n\n",
                'problem_text': "कृपया अपनी समस्या चुनें:",
                'options': [
                    "❌ अकाउंट नहीं मिला?"
                ]
            }
        }

        # Get the appropriate text based on the selected language
        content = texts.get(language, texts['english'])  # Default to English if language not found

        # Build the message text
        message_text = (
            f"{content['title']}"
            f"{content['problem_text']}"
        )

        # Build the keyboard with only the "Didn't get your account?" option
        keyboard = [
            [InlineKeyboardButton(option, callback_data=f"didnt_get_acc_{service_id}")]
            for option in content['options']
        ]
        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f"help_{service_id}")])

        await query.message.edit_media(
            media=InputMediaPhoto(
                media=self.LIVE_CHAT_PAGE["image"],
                caption=message_text,
                parse_mode='Markdown'
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def show_verification_progress(self, message):
        try:
            verification_text = "Verifying... [□□□□□□□□□□] 0%"
            current_caption = message.caption or ""  # Handle None caption
            
            for i in range(1, 11):
                percentage = i * 10
                blocks = "■" * i + "□" * (10 - i)
                new_text = f"{current_caption}\n\n{verification_text}"
                try:
                    await message.edit_caption(
                        caption=new_text.replace(verification_text, 
                                              f"Verifying... [{blocks}] {percentage}%"),
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Error updating verification progress: {e}")
                    break
                await asyncio.sleep(0.25)

            for _ in range(3):
                for dots in ["...", "..", "."]:
                    try:
                        new_text = f"{current_caption}\n\nVerification complete{dots}"
                        await message.edit_caption(
                            caption=new_text,
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.error(f"Error updating verification complete: {e}")
                        break
                    await asyncio.sleep(0.2)
        except Exception as e:
            logger.error(f"Error in verification progress: {e}")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        
        # Check membership status
        is_member = await self.handle_membership_check(user.id, context)
        
        # Handle referral code in start parameter
        referral_code = None
        service_id = None
        if context.args:
            start_param = context.args[0]
            if '_' in start_param:
                referral_code, service_id = start_param.split('_')
            elif len(start_param) == 8:
                referral_code = start_param
        
        # Add/update user in database
        self.db.add_user(user.id, user.first_name, referral_code, service_id)
        
        # Get current verification status
        user_data = self.db.get_user(user.id)
        is_verified = user_data and user_data[3] == 1 and is_member
        
        if is_verified:
            # Show verified welcome page
            keyboard = [[InlineKeyboardButton("🎁 Roll in 🎁", callback_data="roll_in")]]
            greeting = self.get_greeting()
            verified_text = VERIFIED_WELCOME_PAGE["text"].format(
                greeting=greeting,
                username=user.first_name
            )
            await update.message.reply_animation(
                animation=VERIFIED_WELCOME_PAGE["gif"],
                caption=verified_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            # Show initial welcome page for unverified users
            keyboard = [[
                InlineKeyboardButton("🚀 Start Verification 🚀", 
                                   callback_data="show_verification")
            ]]
            await update.message.reply_animation(
                animation=WELCOME_PAGE["gif"],
                caption=WELCOME_PAGE["text"],
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
    async def format_receipt(self, user_id, service_id):
        """Generate a nicely formatted receipt with service-specific details"""
        try:
            with sqlite3.connect('bot_users.db') as conn:
                c = conn.cursor()
                # Get unlock timestamp and service details
                c.execute("""
                    SELECT su.unlocked_at, s.name
                    FROM service_unlocks su
                    WHERE su.user_id = ? AND su.service_id = ?
                    ORDER BY su.unlocked_at ASC LIMIT 1
                """, (user_id, service_id))
                result = c.fetchone()
                
                unlock_date = result[0] if result else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                service_name = SERVICES[service_id]['name'] if service_id in SERVICES else "Unknown Service"
                
                receipt = (
                    "🧾 *PREMIUM ACCESS RECEIPT*\n"
                    "━━━━━━━━━━━━━━━━━━\n\n"
                    f"🆔 User ID: `{user_id}`\n"
                    f"📦 Package: {service_name}\n"
                    "💰 Cost: $0.00 (Referral Reward)\n\n"
                    "📋 *Status Details*\n"
                    "━━━━━━━━━━━━━━━━━━\n"
                    "🔄 Approval Status: Pending\n"
                    "🟢 Bot Status: Online\n"
                    "⏱ Est. Processing Time: 12-24h\n\n"
                    "📞 *Support Information*\n"
                    "━━━━━━━━━━━━━━━━━━\n"
                    "Contact: @hecabruss\n\n"
                    "✨ Thank you for choosing our service!\n"
                    "   Your premium access will be\n"
                    "   activated after approval."
                )
                return receipt
        except Exception as e:
            logger.error(f"Error formatting receipt: {e}")
            return "Error generating receipt. Please try again."

    async def show_verification_page(self, query: CallbackQuery):
        keyboard = [
            [
                InlineKeyboardButton("📢 Channel 1", url=self.channel1_link),
                InlineKeyboardButton("🔔 Channel 2", url=self.channel2_link)
            ],
            [InlineKeyboardButton("✨ Verify Access ✨", callback_data="verify_access")]
        ]
        await query.message.edit_media(
            media=InputMediaAnimation(
                media=VERIFICATION_PAGE["gif"],
                caption=VERIFICATION_PAGE["text"],
                parse_mode='Markdown'
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    async def show_receipt(self, query: CallbackQuery, service_id: str):
        """Display the receipt to the user."""
        try:
            user_id = query.from_user.id
            
            # Get service name with error handling
            service_name = SERVICES.get(service_id, {}).get('name', 'Unknown Service')
            
            # Get current timestamp
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Format receipt text
            receipt_text = (
                "🧾 *PREMIUM ACCESS RECEIPT*\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                f"🆔 User ID: `{user_id}`\n"
                f"📦 Package: {service_name}\n"
                "💰 Cost: $0.00 (Referral Reward)\n\n"
                "📋 *Status Details*\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "🔄 Approval Status: Pending\n"
                "🟢 Bot Status: Online\n"
                "⏱ Est. Processing Time: 12-24h\n\n"
                "📞 *Support Information*\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "Contact: @hecabruss\n\n"
                "✨ Thank you for choosing our service!\n"
                "   Your premium access will be\n"
                "   activated after approval."
            )
            
            # Build keyboard with back button
            keyboard = [[
                InlineKeyboardButton("🔙 Back", callback_data=f"back_to_unlock_{service_id}")
            ]]
            
            # Update message with receipt
            await query.message.edit_media(
                media=InputMediaAnimation(
                    media=UNLOCK_PAGE["gif"],
                    caption=receipt_text,
                    parse_mode='Markdown'
                ),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        except Exception as e:
            logger.error(f"Error showing receipt: {e}")
            error_message = (
                "⚠️ Error displaying receipt. Please try again.\n"
                "If the problem persists, contact support."
            )
            await query.message.edit_caption(
                caption=error_message,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back", callback_data=f"back_to_unlock_{service_id}")
                ]])
            )

    async def show_services_page(self, query: CallbackQuery, page=0):
        await query.message.edit_media(
            media=InputMediaAnimation(
                media=SERVICES_PAGE["gif"],
                caption=SERVICES_PAGE["text"],
                parse_mode='Markdown'
            ),
            reply_markup=self.build_services_keyboard(page)
        )

    async def show_referral_page(self, query: CallbackQuery, service_id):
        """Displays the referral page with working share functionality."""
        try:
            user_data = self.db.get_user(query.from_user.id)
            if not user_data or not user_data[5]:  # Check referral_code index
                logger.error("No referral code found for user")
                await query.answer("Error generating referral link. Please try again.")
                return

            referral_code = user_data[5]  # Get referral code
            service_name = SERVICES[service_id]['name']
            
            # Generate referral link with service ID
            referral_link = f"https://t.me/{self.bot_username}?start={referral_code}_{service_id}"
            
            # Create share message
            share_text = (
                f"🎁 Get FREE {service_name} Premium Access!\n\n"
                "I found an amazing opportunity to get premium accounts completely FREE!\n\n"
                "✨ What you get:\n"
                f"• Full {service_name} Premium Access\n"
                "• Instant activation after verification\n"
                "• 100% Free through referral system\n\n"
                "🔥 Limited Time Offer!\n"
                f"Join now: {referral_link}"
            )
            
            # Create Telegram share URL
            encoded_text = urllib.parse.quote(share_text)
            share_url = f"tg://msg_url?url={urllib.parse.quote(referral_link)}&text={encoded_text}"
            
            # Modified keyboard - removed copy link option
            keyboard = [
                [InlineKeyboardButton("📱 Share on Telegram", url=share_url)],
                [InlineKeyboardButton("🔙 Back", callback_data=f"service_{service_id}")]
            ]
            
            text = (
                f"🎯 *Share {service_name} Premium Access*\n\n"
                "Share your exclusive invitation with friends:\n\n"
                "1️⃣ Click 'Share on Telegram'\n"
                "2️⃣ Send to your friends\n"
                "3️⃣ Earn a referral point when your friend completes verification!\n\n"
                f"Your Referral Link:\n`{referral_link}`"
            )
            
            await query.message.edit_media(
                media=InputMediaAnimation(
                    media=self.referral_gif,
                    caption=text,
                    parse_mode='Markdown'
                ),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        except Exception as e:
            logger.error(f"Error in show_referral_page: {e}")
            await query.answer("Error displaying referral page. Please try again.")

    async def show_progress_page(self, query: CallbackQuery, service_id):
        stats = self.db.get_service_referral_stats(query.from_user.id, service_id)
        percentage = (stats['completed_referrals'] / 5) * 100

        progress_bar = self.build_progress_bar(percentage)
        service_name = SERVICES[service_id]['name']
        text = (f"📊 *{service_name} Referral Progress*\n\n"
                f"Progress: {progress_bar}\n"
                f"Completed Referrals: {stats['completed_referrals']}/5\n\n"
                f"{'🎉 Ready to unlock!' if stats['completed_referrals'] >= 5 else '📱 Keep inviting friends!'}")

        keyboard = []
        if stats['completed_referrals'] >= 5:
            keyboard.append([InlineKeyboardButton("🔓 Unlock Now", callback_data=f"unlock_{service_id}")])
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f"service_{service_id}")])
        
        await query.message.edit_media(
            media=InputMediaAnimation(
                media=PROGRESS_PAGE["gif"],
                caption=text,
                parse_mode='Markdown'
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    async def unlock_premium(self, query: CallbackQuery, service_id: str):
        """Handle the premium unlock process"""
        try:
            user_id = query.from_user.id
            stats = self.db.get_service_referral_stats(user_id, service_id)

            if stats['completed_referrals'] >= 5:
                # Show unlock loading animation
                loading_message = await query.message.reply_text("Starting unlock process...")
                
                # Loading animation stages
                stages = [
                    "Wait a sec",
                    "Sending log",
                    "Sending user data", 
                    "Receiving approval",
                    "Getting your account"
                ]
                
                spinner = ['|', '/', '—', '\\']
                dots = ['.', '..', '...']
                
                # Loop through each stage to show the loading animation
                for stage in stages:
                    for spin_count in range(3):  # Loop for spinner cycles
                        for spin in spinner:
                            for dot in dots:
                                try:
                                    # Update the message with the current spinner and stage
                                    text = f"{spin} {stage}{dot}"
                                    await loading_message.edit_text(text)
                                    await asyncio.sleep(0.2)
                                except Exception as e:
                                    self.logger.error(f"Error updating loading animation: {e}")
                                    continue

                # Finalize loading message
                await loading_message.edit_text("✅ Verification complete! Getting your premium access...")
                await asyncio.sleep(1)

                # Clean up loading message
                try:
                    await loading_message.delete()
                except Exception as e:
                    self.logger.error(f"Error deleting loading message: {e}")
                
                # Unlock the service
                self.db.check_and_unlock_service(user_id, service_id)

                # Show unlock page
                await self.show_unlock_page(query, service_id)

            else:
                # Notify the user if referrals are not completed
                await query.answer("Complete 5 referral to unlock this service!")
                await self.show_progress_page(query, service_id)

        except Exception as e:
            self.logger.error(f"Error in unlock_premium: {e}")
            await query.answer("An error occurred. Please try again.")
            
    async def show_unlock_animation(self, message, query):
        """Shows an animated unlocking sequence"""
        try:
            loading_text = "🔄 Processing your unlock request..."
            current_caption = message.caption or ""
            
            # Show initial processing message
            await message.edit_caption(
                caption=f"{current_caption}\n\n{loading_text}",
                parse_mode='Markdown'
            )
            
            # Animation stages
            stages = [
                ("🔍 Verifying referrals", 1),
                ("✨ Preparing account access", 1),
                ("🔑 Generating credentials", 1),
                ("📦 Finalizing setup", 1)
            ]
            
            for stage_text, delay in stages:
                await message.edit_caption(
                    caption=f"{current_caption}\n\n{stage_text}",
                    parse_mode='Markdown'
                )
                await asyncio.sleep(delay)
            
            # Success animation
            for _ in range(3):
                for dots in [".", "..", "..."]:
                    await message.edit_caption(
                        caption=f"{current_caption}\n\n✅ Unlock complete{dots}",
                        parse_mode='Markdown'
                    )
                    await asyncio.sleep(0.3)
            
            # Show final unlock page
            await self.show_unlock_page(query)
            
        except Exception as e:
            logger.error(f"Error in unlock animation: {e}")
            # Fallback to direct unlock page if animation fails
            await self.show_unlock_page(query)
            
    async def show_tasks_page(self, query: CallbackQuery):
        """Display the tasks page with spin option."""
        user_id = query.from_user.id
        service_id = query.data.split('_')[2] if query.data.startswith('skip_point_') else None
        
        # Store the current service
        if service_id:
            self.current_service[user_id] = service_id
        
        keyboard = [
            [InlineKeyboardButton("🎡 Spin for a point", callback_data="spin_wheel")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_services")]
        ]
        
        await query.message.edit_media(
            media=InputMediaAnimation(
                media=self.TASKS_PAGE["gif"],
                caption=self.TASKS_PAGE["text"],
                parse_mode='Markdown'
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def show_spin_page(self, query: CallbackQuery):
        """Display the spin page with completion options."""
        user_id = query.from_user.id
        
        # Check if spin has been revealed for this user
        if user_id in self.spin_revealed and self.spin_revealed[user_id]:
            # Show revealed state with URL button
            keyboard = [
                [InlineKeyboardButton("🎡 Spin Here", url="https://t.me/LuckyDrawMasterBot/app?startapp=Y2g9a1FqOXh2SFI3RyZnPXNwJmw9a1FqOXh2SFI3RyZzbz1TaGFyZSZ1PTc5MDM1MDA0NTA")],
                [InlineKeyboardButton("✅ Completed", callback_data="spin_completed")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_to_tasks")]
            ]
        else:
            # Show initial state with start_spin_timer button
            keyboard = [
                [InlineKeyboardButton("🎡 Start Spin", callback_data="start_spin_timer")],
                [InlineKeyboardButton("✅ Completed", callback_data="spin_completed")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_to_tasks")]
            ]
        
        await query.message.edit_media(
            media=InputMediaPhoto(
                media=self.SPIN_PAGE["image"],
                caption=self.SPIN_PAGE["text"],
                parse_mode='Markdown'
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def show_referral_service_page(self, query: CallbackQuery, service_id):
        """Display the referral service page with optional skip."""
        user_id = query.from_user.id
        
        # Build keyboard based on whether user has used skip option
        if service_id in ['chatgpt', 'netflix', 'youtube', 'spotify'] and user_id not in self.skip_point_used:
            keyboard = [
                [InlineKeyboardButton("🎁 Get Referral", callback_data=f"get_referral_{service_id}")],
                [InlineKeyboardButton("📊 Check Progress", callback_data=f"check_progress_{service_id}")],
                [InlineKeyboardButton("⏭️ Skip one point", callback_data=f"skip_point_{service_id}")],
                [InlineKeyboardButton("🔙 Back to Services", callback_data="back_to_services")]
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("🎁 Get Referral", callback_data=f"get_referral_{service_id}")],
                [InlineKeyboardButton("📊 Check Progress", callback_data=f"check_progress_{service_id}")],
                [InlineKeyboardButton("🔙 Back to Services", callback_data="back_to_services")]
            ]
        
        stats = self.db.get_service_referral_stats(query.from_user.id, service_id)
        service_name = SERVICES[service_id]['name']
        text = (f"🎯 *Get {service_name} Premium Access*\n\n"
                f"Current Referrals: {stats['completed_referrals']}/5\n"
                "Invite friends to unlock premium access!")
        
        await query.message.edit_media(
            media=InputMediaAnimation(
                media=SERVICES_PAGE["gif"],
                caption=text,
                parse_mode='Markdown'
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
            
    async def show_loading_animation(self, message):
        """Shows an advanced loading animation with multiple stages"""
        try:
            stages = [
                "Wait a sec",
                "Sending log",
                "Sending user data", 
                "Receiving approval",
                "Getting your account"
            ]
            
            spinner = ['|', '/', '—', '\\']
            dots = ['.', '..', '...']
            
            for stage in stages:
                for spin_count in range(3):
                    for spin in spinner:
                        for dot in dots:
                            try:
                                text = f"{spin} {stage}{dot}"
                                await message.edit_text(text)
                                await asyncio.sleep(0.2)
                            except Exception as e:
                                logger.error(f"Error updating loading animation: {e}")
                                continue

            await message.edit_text("✅ Verification complete! Getting your premium access...")
            await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Error in loading animation: {e}")
            try:
                await message.edit_text("Processing your request...")
            except:
                pass
                
    async def show_help_page(self, query: CallbackQuery, service_id):
        """Display the help page with language options."""
        keyboard = [
            [InlineKeyboardButton("Hindi", callback_data=f"help_hindi_{service_id}")],
            [InlineKeyboardButton("English", callback_data=f"help_english_{service_id}")],
            [InlineKeyboardButton("🔙 Back", callback_data=f"back_to_unlock_{service_id}")]
        ]

        help_text = (
            "🌟 *Need Help?* 🌟\n\n"
            "Choose your preferred language for assistance:\n\n"
            "🇬🇧 English - For English support\n"
            "🇮🇳 Hindi - हिंदी में सहायता के लिए"
        )

        await query.message.edit_media(
            media=InputMediaPhoto(
                media=self.HELP_PAGE["image"],
                caption=help_text,
                parse_mode='Markdown'
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    async def send_restriction_notice(self, context, chat_id, service_id):
        """Sends the restriction notice without blocking the main thread."""
        try:
            # Get service information
            service_name = SERVICES[service_id]['name']

            # Notification text
            notification_text = (
                "⚠️ *Access Restriction Notice* ⚠️\n\n"
                f"Your access to {service_name} Premium has been restricted.\n\n"
                "*Reason:*\n"
                "Violation of service terms and conditions detected.\n\n"
                "If you believe this is an error, please contact support:\n"
                "@hecabruss\n\n"
                "Thank you for your understanding.\n"
                "- ishterosbot Team"
            )

            # Send notification
            notification_message = await context.bot.send_message(
                chat_id=chat_id,
                text=notification_text,
                parse_mode='Markdown'
            )

            # Schedule deletion using job queue
            context.job_queue.run_once(
                lambda _: self.delete_message_wrapper(context, chat_id, notification_message.message_id),
                3600  # 1 hour
            )

        except Exception as e:
            logger.error(f"Error sending restriction notice: {e}")
        
    async def send_notification_after_delay(self, chat_id, service_id, delay, context):
        """Send a notification after a specified delay."""
        try:
            await asyncio.sleep(delay)

            # Get service information with error handling
            try:
                service_name = SERVICES[service_id]['name']
            except KeyError:
                service_name = "Service"  # Fallback if service_id not found
                logger.error(f"Service ID {service_id} not found in SERVICES")

            notification_text = (
                "⚠️ *Access Restriction Notice* ⚠️\n\n"
                f"Your access to {service_name} Premium has been restricted.\n\n"
                "*Reason:*\n"
                "Violation of service terms and conditions detected.\n\n"
                "If you believe this is an error, please contact support:\n"
                "@hecabruss\n\n"
                "Thank you for your understanding.\n"
                "- ishterosbot Team"
            )

            try:
                notification_message = await context.bot.send_message(
                    chat_id=chat_id,
                    text=notification_text,
                    parse_mode='Markdown'
                )

                # Keep notification for 1 hour
                await asyncio.sleep(3600)
                await notification_message.delete()

            except Exception as e:
                logger.error(f"Error sending/deleting notification: {e}")

        except Exception as e:
            logger.error(f"Error in notification delay: {e}")
            
    async def delete_message_after_delay(self, chat_id, message_id, delay, context):
        """Delete a message after a specified delay."""
        try:
            await asyncio.sleep(delay)
            await context.bot.delete_message(
                chat_id=chat_id,
                message_id=message_id
            )
        except Exception as e:
            logger.error(f"Error deleting message {message_id}: {e}")
            
    async def send_delayed_notification(self, chat_id, service_id, context):
        """Sends notification asynchronously without blocking main operations."""
        try:
            await asyncio.sleep(30)
            service_name = SERVICES.get(service_id, {}).get('name', 'Premium Service')

            notification_text = (
                "⚠️ *Access Restriction Notice* ⚠️\n\n"
                f"Your access to {service_name} has been restricted.\n\n"
                "*Reason:*\n"
                "Violation of service terms and conditions detected.\n\n"
                "If you believe this is an error, please contact support:\n"
                "@hecabruss\n\n"
                "Thank you for your understanding.\n"
                "- ishterosbot Team"
            )

            sent_notification = await context.bot.send_message(
                chat_id=chat_id,
                text=notification_text,
                parse_mode='Markdown'
            )

            # Schedule deletion without blocking
            asyncio.create_task(self.delete_message_after_delay(
                chat_id, sent_notification.message_id, 3600, context
            ))

        except Exception as e:
            logger.error(f"Error sending delayed notification: {e}")
        
    async def send_voice_message(self, chat_id, user_id, language, context, service_id):
        """Send voice message and enable reverify button for specific service"""
        try:
            # Show typing indicator
            await context.bot.send_chat_action(chat_id=chat_id, action="record_audio")
            await asyncio.sleep(random.uniform(2.0, 3.0))

            # Initialize tracking dictionaries if needed
            if user_id not in self.didnt_get_account_clicked:
                self.didnt_get_account_clicked[user_id] = {}
            
            # Mark this service as clicked
            self.didnt_get_account_clicked[user_id][service_id] = True
            
            # Send voice message if not sent before
            if user_id not in self.voice_message_sent:
                voice_file_id = self.english_voice_file_id if language == 'english' else self.hindi_voice_file_id
                try:
                    sent_message = await context.bot.send_voice(
                        chat_id=chat_id,
                        voice=voice_file_id,

                    )
                    self.voice_message_sent.add(user_id)
                    
                    # Schedule message deletion
                    asyncio.create_task(self.delete_message_after_delay(
                        chat_id, sent_message.message_id, 600, context
                    ))
                    
                except Exception as e:
                    logger.error(f"Error sending voice message: {e}")
            else:
                # If voice was already sent
                await context.bot.send_chat_action(chat_id=chat_id, action="typing")
                await asyncio.sleep(random.uniform(1.5, 2.0))
                
                notification_message = await context.bot.send_message(
                    chat_id=chat_id,
                    text="You have already received the voice message. The reverify option is now available in the unlock page."
                )
                
                # Schedule notification deletion
                asyncio.create_task(self.delete_message_after_delay(
                    chat_id, notification_message.message_id, 2, context
                ))
                
        except Exception as e:
            logger.error(f"Error in send_voice_message: {e}")
            
    async def delete_message_after_delay(self, chat_id, message_id, delay, context):
        """Delete a message after a specified delay."""
        try:
            await asyncio.sleep(delay)
            await context.bot.delete_message(
                chat_id=chat_id,
                message_id=message_id
            )
        except Exception as e:
            logger.error(f"Error deleting message {message_id}: {e}")
            
    async def show_unlock_page(self, query: CallbackQuery, service_id: str):
        """Show unlock page with service-specific button visibility"""
        try:
            user_id = query.from_user.id
            current_time = time.time()
            
            # Initialize nested dictionaries if needed
            if user_id not in self.unlock_timestamps:
                self.unlock_timestamps[user_id] = {}
            if user_id not in self.help_button_visible:
                self.help_button_visible[user_id] = {}
            if user_id not in self.didnt_get_account_clicked:
                self.didnt_get_account_clicked[user_id] = {}
                
            # Initialize service-specific timestamps if needed
            if service_id not in self.unlock_timestamps[user_id]:
                self.unlock_timestamps[user_id][service_id] = current_time
                self.help_button_visible[user_id][service_id] = False
            
            # Check service-specific button visibility
            show_help_button = (
                self.help_button_visible[user_id].get(service_id, False) or
                current_time - self.unlock_timestamps[user_id][service_id] >= 30
            )
            
            show_reverify_button = self.didnt_get_account_clicked[user_id].get(service_id, False)
            
            # Update help button visibility for this service
            if show_help_button:
                self.help_button_visible[user_id][service_id] = True
            
            # Build keyboard
            keyboard = []
            
            # Add status button
            keyboard.append([
                InlineKeyboardButton(
                    "📱 Check Status",
                    callback_data=f"check_status_{service_id}"
                )
            ])
            
            # Add reverify button if enabled for this service
            if show_reverify_button:
                keyboard.append([
                    InlineKeyboardButton(
                        "🔁 Reverify",
                        callback_data=f"reverify_{service_id}"
                    )
                ])
            
            # Add help button if visible
            if show_help_button:
                keyboard.append([
                    InlineKeyboardButton(
                        "❓ Help",
                        callback_data=f"help_{service_id}"
                    )
                ])
            
            # Add back button
            keyboard.append([
                InlineKeyboardButton(
                    "🔙 Back to Services",
                    callback_data="back_to_services"
                )
            ])
            
            # Update message
            text = (
                f"{UNLOCK_PAGE['text']}\n\n"
                "🎉 *Access Granted Successfully!*\n"
                "📱 Your premium account is ready.\n"
                "⏱ Please wait for approval (12-24 hours)."
            )
            
            await query.message.edit_media(
                media=InputMediaAnimation(
                    media=UNLOCK_PAGE["gif"],
                    caption=text,
                    parse_mode='Markdown'
                ),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        except Exception as e:
            logger.error(f"Error in show_unlock_page: {e}")
            await query.answer("Error displaying unlock page. Please try again.")
            
    async def delete_message_wrapper(self, context, chat_id, message_id):
        """Wrapper for safe message deletion."""
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            logger.error(f"Error deleting message {message_id}: {e}")

    async def handle_error(self, query, error_message, delete_after=5):
        """Handles errors with automatic cleanup."""
        try:
            error_msg = await query.message.reply_text(error_message)
            await asyncio.sleep(delete_after)
            await error_msg.delete()
        except Exception as e:
            logger.error(f"Error handling error message: {e}")
            
    async def handle_reverify(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, service_id: str):
        """Handles service-specific reverify process"""
        try:
            user_id = query.from_user.id
            chat_id = query.message.chat_id

            # Initialize service-specific reverify status
            if user_id not in self.reverify_status:
                self.reverify_status[user_id] = {}
            
            if self.reverify_status[user_id].get(service_id, False):
                error_msg = await query.message.reply_text(
                    f"We already received your request for {SERVICES[service_id]['name']}. Please wait for the result."
                )
                asyncio.create_task(self.delete_message_after_delay(
                    chat_id, error_msg.message_id, 2, context
                ))
                return

            self.reverify_status[user_id][service_id] = True
            loading_message = await query.message.reply_text(
                f"🔄 Starting reverify process for {SERVICES[service_id]['name']}..."
            )

            animation_task = asyncio.create_task(self.show_loading_animation(loading_message))
            notification_task = asyncio.create_task(self.send_delayed_notification(
                chat_id, service_id, context
            ))
            deletion_task = asyncio.create_task(self.delete_message_after_delay(
                chat_id, loading_message.message_id, 20, context
            ))

        except Exception as e:
            logger.error(f"Error in reverify process: {e}")
            error_msg = await query.message.reply_text("⚠️ An error occurred. Please try again later.")
            asyncio.create_task(self.delete_message_after_delay(
                chat_id, error_msg.message_id, 5, context
            ))

    async def show_loading_animation(self, message):
        """Shows loading animation without blocking."""
        try:
            stages = [
                "Connecting to server",
                "Verifying request", 
                "Processing data",
                "Checking status",
                "Finalizing"
            ]

            for stage in stages:
                for dots in ["", ".", "..", "..."]:
                    try:
                        await message.edit_text(f"🔄 {stage}{dots}")
                        await asyncio.sleep(0.3)
                    except Exception:
                        return

            await message.edit_text("✅ Completed! We will send you the result shortly.")

        except Exception as e:
            logger.error(f"Error in loading animation: {e}")
            
    async def show_reverify_button_after_delay(self, query: CallbackQuery, service_id: str):
        """Show the reverify button after 20 seconds delay"""
        try:
            await asyncio.sleep(20)
            user_id = query.from_user.id
            self.reverify_button_visible[user_id] = True
            await self.show_unlock_page(query, service_id)
        except Exception as e:
            logger.error(f"Error showing reverify button: {e}")
            
    async def check_channel_membership(self, user_id, context):
        try:
            member = await context.bot.get_chat_member(self.channel2_id, user_id)
            return member.status in ['member', 'administrator', 'creator']
        except Exception as e:
            logger.error(f"Error checking membership: {e}")
            return False
            
    async def verify_channel_membership(self, user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """
        Verify user's membership and handle point deduction if they left
        """
        try:
            member = await context.bot.get_chat_member(self.channel2_id, user_id)
            is_member = member.status in ['member', 'administrator', 'creator']
            
            if not is_member:
                # Handle point deduction if user left
                await self.handle_channel_leave(user_id, context)
                
            return is_member
            
        except Exception as e:
            logger.error(f"Error checking membership: {e}")
            return False
            
    async def handle_channel_leave(self, user_id: int, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle point deduction and notifications when a user leaves the channel
        """
        try:
            # Get referrer information
            referrers = self.db.get_referrer_info(user_id)
            
            if not referrers:
                return
                
            for referrer_id, service_id, referrer_name in referrers:
                # Attempt to deduct point
                if self.db.deduct_referral_point(referrer_id, user_id, service_id):
                    # Get service name
                    service_name = SERVICES[service_id]['name'] if service_id in SERVICES else "Premium"
                    
                    # Send notification to referrer
                    notification_text = (
                        "⚠️ *Referral Point Deducted* ⚠️\n\n"
                        f"Your referral point for {service_name} has been deducted.\n\n"
                        "📝 *Reason:*\n"
                        "Your referred user left the required channel.\n\n"
                        "💡 *Note:*\n"
                        "• Points are only valid when referred users stay in the channel\n"
                        "• You can earn new points by inviting other users"
                    )
                    
                    try:
                        await context.bot.send_message(
                            chat_id=referrer_id,
                            text=notification_text,
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.error(f"Error sending point deduction notification: {e}")
                        
        except Exception as e:
            logger.error(f"Error in handle_channel_leave: {e}")
            
    async def handle_membership_check(self, user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """
        Check membership and handle verification status updates.
        Returns True if user has valid membership, False otherwise.
        """
        is_member = await self.verify_channel_membership(user_id, context)
        user_data = self.db.get_user(user_id)
        
        if user_data and user_data[3] == 1:  # If user was previously verified
            if not is_member:
                # User left channel after verification - reset verification status
                self.db.update_user_verification(user_id, 0)
                return False
        return is_member

    async def verify_user_access(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
        try:
            user = query.from_user
            
            # Show verification progress first
            await self.show_verification_progress(query.message)
            
            # Check channel membership
            is_member = await self.check_channel_membership(user.id, context)
            if is_member:
                # Update verification status and get notifications
                notifications = self.db.update_user_verification(user.id, 1)
                
                # Send notifications to referrers
                for notification in notifications:
                    try:
                        await context.bot.send_message(
                            chat_id=notification['referrer_id'],
                            text=notification['message'],
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.error(f"Error sending notification: {e}")
                
                # Show verified welcome page
                keyboard = [[InlineKeyboardButton("🎁 Roll in 🎁", callback_data="roll_in")]]
                greeting = self.get_greeting()
                verified_text = VERIFIED_WELCOME_PAGE["text"].format(
                    greeting=greeting,
                    username=user.first_name
                )
                
                await query.message.edit_media(
                    media=InputMediaAnimation(
                        media=VERIFIED_WELCOME_PAGE["gif"],
                        caption=verified_text,
                        parse_mode='Markdown'
                    ),
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            else:
                # Show error message for unverified users
                error_text = f"{VERIFICATION_PAGE['text']}\n\n❌ *Access Denied*\nPlease join both channels"
                await query.message.edit_caption(
                    caption=error_text,
                    parse_mode='Markdown',
                    reply_markup=query.message.reply_markup
                )
        except Exception as e:
            logger.error(f"Error in verify_user_access: {e}")
            await query.answer("An error occurred during verification. Please try again.")

    def build_navigation_keyboard(self, service_id, current_page, total_accounts):
        keyboard = []
        nav_row = []
        
        if current_page > 0:
            nav_row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"prev_{service_id}"))
        if total_accounts > (current_page + 1) * 5:
            nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"next_{service_id}"))
            
        if nav_row:
            keyboard.append(nav_row)
        keyboard.append([InlineKeyboardButton("🔙 Back to Services", callback_data="back_to_services")])
        
        return keyboard

    async def show_service_accounts(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, service_id: str):
        """
        Display service accounts with proper membership verification and error handling.

        Args:
            query (CallbackQuery): The callback query from the user
            context (ContextTypes.DEFAULT_TYPE): The context object
            service_id (str): The ID of the service to display accounts for
        """
        try:
            # Verify membership status
            if not await self.handle_membership_check(query.from_user.id, context):
                await self.show_verification_page(query)
                return

            # Validate service exists
            if service_id not in SERVICES:
                await query.answer("⚠️ Service not found")
                await self.show_services_page(query)  # Redirect to services page
                return

            # Get service information
            service_info = SERVICES[service_id]

            # Check if service requires referral
            if self.requires_referral(service_id):
                await self.show_referral_service_page(query, service_id)
                return

            # Get current page from context
            current_page = context.user_data.get('current_page', 0)

            # Load accounts if not already loaded
            if service_id not in self.service_accounts:
                self.service_accounts[service_id] = self.load_accounts(service_info.get('file', ''))

            # Get accounts for the service
            accounts = self.service_accounts.get(service_id, [])

            # Calculate pagination
            start_idx = current_page * 5
            end_idx = start_idx + 5
            current_accounts = accounts[start_idx:end_idx]

            # Build message content
            message = self._build_accounts_message(service_info['name'], current_accounts)

            # Build navigation keyboard
            keyboard = self._build_accounts_keyboard(service_id, current_page, len(accounts))

            # Update message with accounts
            try:
                if 'image' in service_info:
                    await query.message.edit_media(
                        media=InputMediaPhoto(
                            media=service_info['image'],
                            caption=message,
                            parse_mode='Markdown'
                        ),
                        reply_markup=keyboard
                    )
                else:
                    await query.message.edit_caption(
                        caption=message,
                        parse_mode='Markdown',
                        reply_markup=keyboard
                    )

            except Exception as e:
                logger.error(f"Error updating message in show_service_accounts: {e}")
                error_message = (
                    "⚠️ Error displaying accounts.\n"
                    "Please try again or contact support if the issue persists."
                )
                await query.message.edit_caption(
                    caption=error_message,
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 Back to Services", callback_data="back_to_services")
                    ]])
                )

        except Exception as e:
            logger.error(f"Critical error in show_service_accounts: {e}")
            await query.answer("An error occurred. Please try again.")
            try:
                error_message = await query.message.reply_text(
                    "⚠️ Something went wrong. Please try again or contact support if the issue persists."
                )
                await asyncio.sleep(5)
                await error_message.delete()
            except Exception:
                pass

    def _build_accounts_message(self, service_name: str, accounts: list) -> str:
        """Build the message content for accounts display."""
        message = f"🔐 *{service_name} Premium Accounts* 🔐\n\n"
        
        if not accounts:
            return message + "No accounts available at the moment. Please check back later."
        
        for account, password in accounts:
            message += f"📧 Login: `{account}`\n🔑 Pass: `{password}`\n\n"
        
        message += "🔄 *Updated Daily!*"
        return message

    def _build_accounts_keyboard(self, service_id: str, current_page: int, total_accounts: int) -> InlineKeyboardMarkup:
        """Build the navigation keyboard for accounts pagination."""
        keyboard = []
        nav_row = []
        
        # Add navigation buttons
        if current_page > 0:
            nav_row.append(
                InlineKeyboardButton("⬅️ Previous", callback_data=f"prev_{service_id}")
            )
        
        if total_accounts > (current_page + 1) * 5:
            nav_row.append(
                InlineKeyboardButton("Next ➡️", callback_data=f"next_{service_id}")
            )
            
        if nav_row:
            keyboard.append(nav_row)
            
        # Add back button
        keyboard.append([
            InlineKeyboardButton("🔙 Back to Services", callback_data="back_to_services")
        ])
        
        return InlineKeyboardMarkup(keyboard)


    def build_navigation_keyboard(self, service_id, current_page, total_accounts):
        keyboard = []
        nav_row = []
        
        if current_page > 0:
            nav_row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"prev_{service_id}"))
        if total_accounts > (current_page + 1) * 5:
            nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"next_{service_id}"))
            
        if nav_row:
            keyboard.append(nav_row)
        keyboard.append([InlineKeyboardButton("🔙 Back to Services", callback_data="back_to_services")])
        
        return keyboard

    async def build_accounts_keyboard(self, service_id, current_page):
        keyboard = []
        if current_page > 0:
            keyboard.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"prev_{service_id}"))
        if len(self.service_accounts[service_id]) > (current_page + 1) * 5:
            keyboard.append(InlineKeyboardButton("Next ➡️", callback_data=f"next_{service_id}"))
        keyboard.append(InlineKeyboardButton("🔙 Back to Services", callback_data="back_to_services"))
        return InlineKeyboardMarkup([keyboard])

    async def handle_spin_start(self, query: CallbackQuery):
        """Handle when user clicks Start Spin button."""
        user_id = query.from_user.id
        
        # Set spin tracking variables
        self.spin_started[user_id] = True
        self.spin_timers[user_id] = datetime.now()
        # Mark spin as permanently revealed for this user
        self.spin_revealed[user_id] = True
        
        # Update keyboard with URL button
        keyboard = [
            [InlineKeyboardButton("🎡 Spin Here", url="https://t.me/LuckyDrawMasterBot/app?startapp=Y2g9a1FqOXh2SFI3RyZnPXNwJmw9a1FqOXh2SFI3RyZzbz1TaGFyZSZ1PTc5MDM1MDA0NTA")],
            [InlineKeyboardButton("✅ Completed", callback_data="spin_completed")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_tasks")]
        ]
        
        await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))

    async def handle_spin_completion(self, query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
        """Handle when user clicks Completed button."""
        user_id = query.from_user.id

        # Check if user has started spinning
        if user_id not in self.spin_started or not self.spin_started[user_id]:
            temp_message = await query.message.reply_text("❌ Please spin for a referal point")
            await asyncio.sleep(2)
            await temp_message.delete()
            return

        # Get the current service the user is working on
        service_id = self.current_service.get(user_id)
        if not service_id:
            temp_message = await query.message.reply_text("❌ Service not found. Please try again.")
            await asyncio.sleep(2)
            await temp_message.delete()
            return

        # Check if the minimum time has passed since spinning started
        current_time = datetime.now()
        if user_id in self.spin_timers:
            elapsed_time = (current_time - self.spin_timers[user_id]).total_seconds()
            
            if elapsed_time < 600:
                remaining = int(600 - elapsed_time)
                temp_message = await query.message.reply_text(
                    f"⏳ Please wait and Try again later"
                )
                await asyncio.sleep(2)
                await temp_message.delete()
                return

            try:
                # Add referral point for the specific service
                with sqlite3.connect('bot_users.db') as conn:
                    c = conn.cursor()
                    c.execute('''
                        INSERT INTO service_referrals 
                        (referrer_id, referee_id, service_id, created_at, status, verified_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (user_id, user_id, service_id, 
                         datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                         'completed',
                         datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                    conn.commit()

                # Mark skip option as used for this user
                self.skip_point_used.add(user_id)

                # Clear spin data
                del self.spin_timers[user_id]
                del self.spin_started[user_id]

                # Show success message
                success_msg = await query.message.reply_text(
                    f"✅ Point added successfully for {SERVICES[service_id]['name']}!"
                )
                await asyncio.sleep(2)
                await success_msg.delete()

                # Redirect to the service's progress page
                await self.show_progress_page(query, service_id)

            except Exception as e:
                logger.error(f"Error updating points: {e}")
                error_msg = await query.message.reply_text("❌ Error updating points. Please try again.")
                await asyncio.sleep(2)
                await error_msg.delete()

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        try:
            # Allow verification-related actions without membership check
            if query.data in ["show_verification", "verify_access"]:
                if query.data == "show_verification":
                    await self.show_verification_page(query)
                    return
                elif query.data == "verify_access":
                    await self.verify_user_access(query, context)
                    return

            # Handle back button from help page
            if query.data.startswith("back_to_unlock_"):
                service_id = query.data.split("_")[-1]
                await self.show_unlock_page(query, service_id)
                return

            # Handle help-related actions without membership check
            if query.data.startswith("help_"):
                parts = query.data.split("_")
                if len(parts) == 2:
                    service_id = parts[1]
                    await self.show_help_page(query, service_id)
                else:
                    language = parts[1]
                    service_id = parts[2]
                    context.user_data['language'] = language
                    await self.show_live_chat(query, service_id)
                return

            # Enforce membership check for other actions
            if not await self.handle_membership_check(query.from_user.id, context):
                await self.show_verification_page(query)
                return

            # Handle service-related actions
            if query.data.startswith("service_"):
                if query.data.startswith("service_page_"):
                    page = int(query.data.split("_")[-1])
                    await self.show_services_page(query, page)
                else:
                    service_id = query.data.split("_")[1]
                    await self.show_service_accounts(query, context, service_id)
                return

            # Handle navigation actions
            if query.data.startswith(("prev_", "next_")):
                service_id = query.data.split("_")[1]
                direction = query.data.split("_")[0]
                current_page = context.user_data.get('current_page', 0)

                if direction == "prev":
                    context.user_data['current_page'] = max(0, current_page - 1)
                else:
                    context.user_data['current_page'] = current_page + 1

                await self.show_service_accounts(query, context, service_id)
                return

            # Handle reverify process
            if query.data.startswith("reverify_"):
                service_id = query.data.split("_")[1]
                await self.handle_reverify(query, context, service_id)
                return

            # Handle "didn't get account" action
            if query.data.startswith("didnt_get_acc_"):
                service_id = query.data.split("_")[-1]
                language = context.user_data.get('language', 'english')

                if query.from_user.id not in self.didnt_get_account_clicked:
                    self.didnt_get_account_clicked[query.from_user.id] = {}

                self.didnt_get_account_clicked[query.from_user.id][service_id] = True

                await self.send_voice_message(
                    query.message.chat_id,
                    query.from_user.id,
                    language,
                    context,
                    service_id
                )

                await self.show_unlock_page(query, service_id)
                return

            # Handle referral-related actions
            if query.data.startswith("get_referral_"):
                service_id = query.data.split("_")[2]
                await self.show_referral_page(query, service_id)
                return

            # Handle progress check actions
            if query.data.startswith("check_progress_"):
                service_id = query.data.split("_")[2]
                await self.show_progress_page(query, service_id)
                return

            # Handle unlock actions
            if query.data.startswith("unlock_"):
                service_id = query.data.split("_")[1]
                await self.unlock_premium(query, service_id)
                return

            # Handle status check actions
            if query.data.startswith("check_status_"):
                service_id = query.data.split("_")[2]
                await self.show_receipt(query, service_id)
                return

            # Handle additional navigation cases
            if query.data.startswith("skip_point_"):
                service_id = query.data.split("_")[2]
                await self.show_tasks_page(query)
            elif query.data == "spin_wheel":
                await self.show_spin_page(query)
            elif query.data == "back_to_tasks":
                await self.show_tasks_page(query)
            elif query.data == "spin_completed":
                await self.handle_spin_completion(query, context)
            elif query.data == "start_spin_timer":
                await self.handle_spin_start(query)

            # Handle basic navigation actions
            match query.data:
                case "back_to_services":
                    await self.show_services_page(query)
                case "roll_in":
                    await self.show_services_page(query)

        except Exception as e:
            logger.error(f"Error in button_callback: {e}")
            await query.answer("An error occurred. Please try again.")
            try:
                error_message = await query.message.reply_text(
                    "⚠️ Something went wrong. Please try again or contact support if the issue persists."
                )
                await asyncio.sleep(5)
                await error_message.delete()
            except Exception:
                pass
                    
def main():
    try:
        # Initialize the bot
        bot = Bot()
        
        # Create the application and pass it your bot's token
        application = ApplicationBuilder().token('8027408030:AAEr06vn8kqahuRtCVyQRMFvlPsHD5zZGkM').build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", bot.start_command))
        application.add_handler(CallbackQueryHandler(bot.button_callback))
        
        # Start the bot
        print("Bot is starting...")
        application.run_polling()
    except Exception as e:
        logger.error(f"Critical error in main: {e}")
        raise

if __name__ == "__main__":
    main()