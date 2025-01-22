from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler, filters
import requests
import requests
import time

# Constants
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
BITQUERY_API_URL = "https://graphql.bitquery.io"
BITQUERY_API_KEY = "BQY78PXi7CmQSOdnGC47bfvzm7gjZxwy"
TELEGRAM_BOT_TOKEN = "7269572848:AAEkW7BfuRKdDdn6mGHSTGZAbPZ4VOC5RTA"
DEXSCREENER_API_URL = "https://api.dexscreener.com/latest/dex/pairs/solana/"
SOLSCAN_API_BASE_URL = "https://api.solscan.io"  # Solscan API base URL
SOL_SCAN_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MzYxMTUzNTk2NDMsImVtYWlsIjoibnp1a2llZ2FuNkBnbWFpbC5jb20iLCJhY3Rpb24iOiJ0b2tlbi1hcGkiLCJhcGlWZXJzaW9uIjoidjIiLCJpYXQiOjE3MzYxMTUzNTl9.WnXhErvJgFLolC5Ywm9SUuICy7vj6t9oBxD37Veg3D4"

# Store user context
user_context = {}

import requests

def fetch_token_insights(mint_address):
    try:
        # Step 1: Check if the token is listed on Pump
        pump_url = f"https://api.dexscreener.com/latest/dex/tokens/{mint_address}"
        pump_response = requests.get(pump_url)

        if pump_response.status_code == 200:
            pump_data = pump_response.json()
            if "pairs" in pump_data and pump_data["pairs"]:
                # Token is associated with Pump
                pair = pump_data["pairs"][0]  # Assuming the first pair is relevant
                dexId = pair.get("dexId", "N/A")
                symbol = pair.get("baseToken", {}).get("symbol", "N/A")
                market_cap = pair.get("marketCap", "N/A")  # Market Cap is often available in pairs data
                priceUsd = pair.get("priceUsd", "N/A")
                liquidity = pair.get("liquidity", {}).get("usd", "N/A")
                volume24Hrs = pair.get("volume", {}).get("h24", "N/A")
                change24Hrs = pair.get("priceChange", {}).get("h24", "N/A")
                fdv = pair.get("fdv", "N/A")

                

                # Function to format numbers in 'k' or 'm'
                def format_value(value):
                    try:
                        value = float(value)  # Convert to float
                        if value >= 1_000_000:
                            return f"{value / 1_000_000:.1f}m"
                        elif value >= 1_000:
                            return f"{value / 1_000:.1f}k"
                        else:
                            return f"{value:.1f}"
                    except ValueError:
                        return "N/A"  # Handle invalid numeric input gracefully

                # Apply formatting to specific fields
                priceUsd_formatted = format_value(priceUsd)
                liquidity_formatted = format_value(liquidity)
                market_cap_formatted = format_value(market_cap)
                fdv_formatted = format_value(fdv)
                volume24Hrs_formatted = format_value(volume24Hrs)
                change24Hrs_formatted = f"{float(change24Hrs):.2f}%"  # Format change as a percentage

                # Construct the string
                s = (
                    f"🌐 Solana {dexId} | {symbol}\n"
                    f"📈 USD: ${priceUsd_formatted} ({change24Hrs_formatted})\n"
                    f"💧 Liquidity | {liquidity_formatted}\n"
                    f"💰 MC: {market_cap_formatted}\n"
                    f"💎 FDV: {fdv_formatted}\n"
                    f"📊 VOL 24h: {volume24Hrs_formatted}\n"
                    "🕑 24"
                )

                return s


        # Step 2: Check if the token is listed on Raydium
        raydium_url = f"https://api.dexscreener.com/orders/v1/solana/{mint_address}"
        raydium_response = requests.get(raydium_url)

        if raydium_response.status_code == 200:

            s = (
                "🌐 Solana - Raydium\n"
                "No Active Trading pairs available for this token"
            )

            return s

        # If neither Pump nor Raydium data is found
        return {"error": "Token is not associated with Pump or Raydium."}

    except Exception as e:
        return {"error": f"Error occurred: {str(e)}"}



# Consolidated function to fetch all token insights
async def check_token_insights(contract_address):
    # Fetch data from both APIs
    data = fetch_token_insights(contract_address)
    return data

def checkDexStatus(token_address):
    """
    Fetch order details for a given Solana token address using Dex Screener API
    and check if the 'tokenProfile' status is approved.

    Args:
        token_address (str): The Solana token address.

    Returns:
        str: Status message indicating if the DEX payment was made for tokenProfile or not.
    """
    try:
        # Construct the API URL
        url = f"https://api.dexscreener.com/orders/v1/solana/{token_address}"
        
        # Make the GET request to the API
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()  # Parse the JSON response
            
            # Check if 'tokenProfile' type exists and is approved
            for item in data:
                if item.get("type") == "tokenProfile" and item.get("status") == "approved":
                    return "✅ Dex Payment Confirmed! \n Payment for enhanced token information services has been verified for the contract address"
            
            # If no 'tokenProfile' with 'approved' status is found
            return "❌ Dex Payment Not Found! No payment detected for enhanced token information services for the contract address"
        else:
            return f"Failed to fetch data. Status code: {response.status_code}, Message: {response.text}"
    except Exception as e:
        return f"Error occurred: {str(e)}"


async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    # Send the banner with the main message as a caption
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=open('banner.png', 'rb'),  # Replace with the path to your banner image
        caption=(
            "Welcome to Rise AI\n"

            "Your ultimate AI-powered trading companion, crafted to elevate your crypto experience with real-time insights and cutting-edge tools 🌟\n"

            "Explore Our Powerful\n\n"

            "Features:\n"

            "Token insights 📊\n"
            "Unlock detailed token insights (supports Pump.Fun / Raydium tokens)\n\n"

            "DEX payment status🦅\n"
            "Instantly verify if enhanced token information services have been paid on decentralized exchanges.\n\n"


            "Bundle Detector📦\n\n"
            "We’re working hard to bring you the ultimate tool to scan and analyze token bundles for hidden risks and opportunities.\n"
            "Stay tuned for updates—this feature will be live soon! 🚀\n\n"


            "Token sniper 🎯\n"
            "Get ready to spot tokens with significant price spikes and capitalize on the market opportunities\n"
            "Stay tuned—this powerful feature will be available soon! 🚀\n"
        ),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Token Analysis 📊", callback_data="check_token_insights"),
                InlineKeyboardButton("Dex Payment Status 🦅", callback_data="check_payment")
            ],
            [
                InlineKeyboardButton("Bundle Checker 📦", callback_data="bundle"),
                InlineKeyboardButton("Token Sniper 🎯", callback_data="sniper")
            ],
            [
                InlineKeyboardButton(" Website 🌐", url="https://riseaisolana.xyz/"),
                InlineKeyboardButton("Twitter 🐦", url="https://x.com/RiseAISolana")
            ],
            [
                InlineKeyboardButton("Tokenomics 🪙", url="https://medium.com/@riseai/riseai-your-ultimate-ai-powered-trading-companion-9b40cf0b2e2c"),
            ]
        ])
    )



async def token_insights(update: Update, context: CallbackContext):
    await update.message.reply_text("Enter the SOL Token Contract Address:")


async def handle_button_click(update: Update, context: CallbackContext):
    """
    Handles button clicks for different features.
    """
    query = update.callback_query
    user_id = query.from_user.id

    # Ensure user_context is initialized for the user
    if user_id not in user_context:
        user_context[user_id] = {}

    if query.data == "check_token_insights":
        # Set state for awaiting a contract address
        user_context[user_id]["awaiting_contract_address"] = True
        user_context[user_id]["awaiting_contract_address_transaction_id"] = False
        await query.message.reply_text("Please provide the contract address for the token to check token insights.")
    elif query.data == "check_payment":
        # Set state for awaiting a contract address and transaction ID
        user_context[user_id]["awaiting_contract_address"] = False
        user_context[user_id]["awaiting_contract_address_transaction_id"] = True
        await query.message.reply_text(
            "Please provide the contract address for the token to check dex payment status"
        )
    elif query.data == "sniper":
        await query.message.reply_text("Token Sniper feature is coming soon!")
    elif query.data == "bundle":
        await query.message.reply_text("Bundle Checker feature is coming soon!")
    else:
        await query.message.reply_text("Unknown option.")

    # Acknowledge the callback query
    await query.answer()


async def handle_token_input(update: Update, context: CallbackContext):
    """
    Handle user input for token-related features.
    """
    user_id = update.message.from_user.id
    user_message = update.message.text.strip()

    # Ensure user_context is initialized for the user
    if user_id not in user_context:
        user_context[user_id] = {}

    if user_context.get(user_id, {}).get("awaiting_contract_address", False):
        # Handle contract address for token insights
        if not user_message:
            await update.message.reply_text("Invalid contract address. Please try again.")
            return

        try:
            token_data = await check_token_insights(user_message)
            await update.message.reply_text(token_data)
        except Exception as e:
            await update.message.reply_text("No trading data found for the given token address")

        # Reset user state
        user_context[user_id]["awaiting_contract_address"] = False

    elif user_context.get(user_id, {}).get("awaiting_contract_address_transaction_id", False):
        if not user_message:
            await update.message.reply_text("Invalid contract address. Please try again.")
            return
        
        contract_address = user_message
        try:
            payment_status = checkDexStatus(contract_address)
            await update.message.reply_text(payment_status)
        except Exception as e:
            await update.message.reply_text(f"Error checking payment status: {str(e)}")

        # Reset user state
        user_context[user_id]["awaiting_contract_address_transaction_id"] = False

    else:
        await update.message.reply_text("Unexpected input. Use /start to explore the features.")


async def menu(update: Update, context: CallbackContext):
    """
    Display the main menu dynamically using CallbackContext to store menu options.
    """
    # Define default menu options if not already set in context
    if "menu_options" not in context.chat_data:
        context.chat_data["menu_options"] = [
            {"text": "Token Analysis", "callback_data": "check_token_insights"},
            {"text": "Token Sniper", "callback_data": "sniper"},
            {"text": "Bundle Checker", "callback_data": "bundle"},
            {"text": "Dex Payment Status", "callback_data": "check_payment"},
            {"text": "Website", "url": "https://example.com"},
            {"text": "Twitter", "url": "https://x.com"},
        ]

    # Retrieve menu options from context
    menu_options = context.chat_data["menu_options"]

    # Create the keyboard dynamically
    keyboard = [
        [InlineKeyboardButton(option["text"], callback_data=option["callback_data"])]
        if "callback_data" in option
        else [InlineKeyboardButton(option["text"], url=option["url"])]
        for option in menu_options
    ]

    # Send the message with the dynamically generated menu
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Explore the features:", reply_markup=reply_markup)


async def handle_payment_button(update: Update, context: CallbackContext):
    """
    Handler for when the 'Check Payment Status' button is pressed.
    """
    await update.message.reply_text("Please provide the contract address")



def main():
    # Create the application using the bot token
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(
        MessageHandler(
            (filters.TEXT & ~filters.COMMAND) | filters.PHOTO | filters.VIDEO, 
            handle_token_input
        )
    )   
    application.add_handler(CallbackQueryHandler(handle_button_click))

    # Start polling for updates
    application.run_polling()

# Start the bot
if __name__ == '__main__':
    main()