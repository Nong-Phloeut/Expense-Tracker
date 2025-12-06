import requests
from decouple import config
from ..models import Alert, Notification

BOT_TOKEN = config('TELEGRAM_BOT_TOKEN')
CHAT_ID = config('TELEGRAM_CHAT_ID')  # Can be global or per user

def send_telegram_message(message, chat_id=None):
    chat_id = chat_id or CHAT_ID
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Telegram send error:", e)

def check_alerts(user, amount, category=None):
    alerts = Alert.objects.filter(user=user, status='active')
    triggered_alerts = []

    for alert in alerts:

        # category rule
        if alert.category and alert.category != category:
            continue
        
        if float(amount) > float(alert.amount):
            msg = (
                f"⚠️ Spending Alert: {alert.name}\n"
                f"\n"
                f"Limit: ${alert.amount}\n"
                f"Current Spending: ${amount}\n\n"
                "Please review your expenses to avoid exceeding your budget."
            )
            triggered_alerts.append(msg)
            send_telegram_message(msg)

            Notification.objects.create(
                user=user,
                title=f"Budget Alert: {alert.name}",
                message=msg,
                is_read=False
            )

    return triggered_alerts


# def check_alerts(user, amount, category=None):
#     from ..models import Alert

#     alerts = Alert.objects.filter(user=user, status='active')
#     triggered_alerts = []

#     for alert in alerts:
#         # If alert has a category, only check expenses in that category
#         if alert.category and alert.category != category:
#             continue

#         if float(amount) > float(alert.amount):
#             msg = f"Alert triggered: {alert.name} exceeded!"
#             triggered_alerts.append(msg)
#             send_telegram_message(msg, chat_id=user.telegram_chat_id)

#     return triggered_alerts