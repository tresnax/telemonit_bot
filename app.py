from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
import multiprocessing
import requests
import logging
import connect
import base64
import time
import os
import re

load_dotenv()

# Add env for telegram_bot
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = int(os.getenv('TELEGRAM_CHAT_ID'))


# Add log setting 
logging.basicConfig(filename='TeleMonit_bot.log', 
                    level=logging.WARNING, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S %d-%m-%Y')


# Filter escape character 
def escape_markdown(text):
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(r'([{}])'.format(re.escape(escape_chars)), r'\\\1', text)


# Monitoring Service =============================================================
def send_message(message: str) -> None:
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }

    response = requests.post(url, data=data)
    if response.status_code != 200:
        logging.error(f"Failed to send message: {response.text}")


def fetch_monit(username: str, password: str, url: str) -> None:
    password_decode = base64.b64decode(password).decode('utf-8')
    url_check = f"{url}/_status?format=xml"

    try:
        response = requests.get(url_check, auth=(username, password_decode))
        response.raise_for_status()
        response_text = response.text
        
        id_server = None
        servers = connect.list_server()

        for server in servers:
            if url == server[3]:
                id_server = f"{server[3]}"
        
        data = [{"response_text": response_text, "id_server": id_server}]
        return data
    except requests.exceptions.Timeout:
        data = [{"status": "timeout", "desc": url}]
        return data
    except requests.exceptions.ConnectionError:
        data = [{"status": "error", "url": url, "desc": "Failed to establish connection, no route to host"}]
        return data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from Monit: {escape_markdown(str(e))}")
        data = [{"status": "error", "url": url, "desc": escape_markdown(str(e))}]
        return data


def parse_monit(xml_data):
    try:
        id_server = xml_data[0].get("id_server","")
        if "timeout" in xml_data[0].get("status",""):
            message = f"🔴 ALERT : *{xml_data[0].get('desc')}* 🔴\n"
            message += "STATUS : TIEMOUT \n"

            logging.error(message)
            send_message(message)

        elif "error" in xml_data[0].get("status",""):
            message = f"🔴 ALERT : *{xml_data[0].get('url')}* 🔴\n"
            message += f"STATUS : {xml_data[0].get('desc')} \n"

            logging.error(message)
            send_message(message)

        else:
            xml_response = xml_data[0].get("response_text", "")

            root = ET.fromstring(xml_response)
            services = root.findall('.//service')

            for service in services:
                type = service.get('type')

                if type == '5':
                    name = service.find('name').text
                    status = service.find('status').text
                    monitor = service.find('monitor').text
                    memory_percent = float(service.find('.//system/memory/percent').text)
                    memory_kb = int(service.find('.//system/memory/kilobyte').text)

                    cpu_user = float(service.find('.//system/cpu/user').text)
                    cpu_system = float(service.find('.//system/cpu/system').text)
                    cpu_nice = float(service.find('.//system/cpu/nice').text) if service.find('.//system/cpu/nice') is not None else 0.0
                    cpu_wait = float(service.find('.//system/cpu/wait').text)

                    memory_gb = memory_kb / (1024 ** 2)
                    cpu_usage = cpu_user + cpu_system + cpu_nice + cpu_wait
                    
                    setting = connect.bot_setting()

                    if monitor == '1':
                        if status != '0':
                            message = f"⚠️ ALERT {id_server} ALERT ⚠️\n"
                            message += f"*Note :* Service *{name}* is down or in touble\n"
                            message += f"*Status :* {status}\n"

                            logging.warning(message)
                            send_message(message)

                        elif cpu_usage >= float(setting[2]):
                            message = f"⚠️ ALERT {id_server} ALERT ⚠️\n"
                            message += f"*Note :* CPU Usage is *{cpu_usage:.2f}* %\n"
                            message += f"*Max Usage :* CPU >= {setting[2]} %\n"
                            message += f"*Status :* High\n\n"
                            message += "*Please check your servers !*"

                            logging.warning(message)
                            send_message(message)

                        elif memory_percent >= float(setting[3]):
                            message = f"⚠️ ALERT {id_server} ALERT ⚠️\n"
                            message += f"*Note :* Memory Usage is *{memory_percent:.2f}* % \\[{memory_gb:.2f}] GB\n"
                            message += f"*Max Usage :* Memory >= {setting[3]} %\n"
                            message += f"*Status :* High\n\n"
                            message += "*Please check your servers !*"

                            logging.warning(message)
                            send_message(message)

    except ET.ParseError as e:
        logging.error(f"Error parsing XML data: {e}")


# Command Input =======================================================================
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat_id != TELEGRAM_CHAT_ID:
        messages = f"*Welcome to TeleMonit_bot*\n"
        messages += "A project Telegram integrated tools for Monit, with our tools you can query event monitoring from Monit and reported to Telegram, helping your productivity with alert event if server have a trouble.\n\n"
        messages += "*Feature*\n"
        messages += "- Realtime monitoring (interval set)\n"
        messages += "- Multiple server monitor\n"
        messages += "- Monitoring item (Service running, uptime, CPU usage, memory usage)\n"
        messages += "- Alert (Timeout, server down, high CPU, high memory)\n\n"
        messages += "More in Github : [TeleMonit_bot](https://github.com/tresnax/telemonit_bot.git)"
        await update.message.reply_text(messages, parse_mode='Markdown')
    else:
        messages = f"*Welcome to TeleMonit_bot*\n"
        messages += "Integrate your Monit to Telegram Alert System\n\n"
        messages += "/list\\_server - List your server list\n"
        messages += "/add\\_server - Add new server for alert\n"
        messages += "/del\\_server - Delete your server list\n"
        messages += "/bot\\_setting - TeleMonit Setting\n\n"
        messages += "Enjoy to your monitoring"

        await update.message.reply_text(messages, parse_mode='Markdown')


async def cmd_add_server(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat_id == TELEGRAM_CHAT_ID:
        if len(context.args) < 3:
            await update.message.reply_text(
                "Usage : /add_server <username> <password> <url>\nExample : /add_server admin admin http://serverku.com"
            )
            return
        
        try:
            await update.message.delete()
        except Exception as e:
            logging.error(f"Error deleting message: {e}")

        username = context.args[0]
        password = context.args[1].encode('utf-8')
        url = context.args[2]

        hash_pass = base64.b64encode(password).decode('utf-8')

        connect.add_server(username, hash_pass, url)
        await update.message.reply_text(f"Server {url} succesfull add to TeleMonit_bot")


async def cmd_del_server(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat_id == TELEGRAM_CHAT_ID:
        servers = connect.list_server()
        if servers:
            keyboard = []
            for server in servers:
                list = [InlineKeyboardButton(f"{server[3]}", callback_data=f"delete|{server[0]}")]
                keyboard.append(list)

            keyboard.append([InlineKeyboardButton(f"Cancel", callback_data=f"delete|cancel")])
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text("Select to Delete", reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update.message.reply_text("No server in lists !")


async def cmd_list_server(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat_id == TELEGRAM_CHAT_ID:
        servers = connect.list_server()
        
        messages = f"*List Server*\n\n"
        if servers:
            for server in servers:
                messages += f"\\[{server[0]}] {server[3]}\n"
        else:
            messages += "Data Empty"
        
        await update.message.reply_text(messages, parse_mode='Markdown')


async def cmd_check_server(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat_id == TELEGRAM_CHAT_ID:
        lists = connect.list_server()

        if lists:
            for list in lists:
                xml_data = fetch_monit(list[1], list[2], list[3])

                if "timeout" in xml_data[0].get("status",""):
                    message = f"🔴 SERVER : *{list[3]}* 🔴\n"
                    message += "STATUS : TIEMOUT \n"

                    logging.error(message)
                    await update.message.reply_text(message, parse_mode='Markdown')

                elif "error" in xml_data[0].get("status",""):
                    message = f"🔴 SERVER : *{list[3]}* 🔴\n"
                    message += f"STATUS : {xml_data[0].get('desc')} \n"

                    logging.error(message)
                    await update.message.reply_text(message, parse_mode='Markdown')
                
                else:
                    xml_response = xml_data[0].get("response_text", "")
                    try:
                        root = ET.fromstring(xml_response)
                        servers = root.findall('.//server')
                        services = root.findall('.//service')

                        for server in servers:
                            hostname = server.find('localhostname').text
                            uptime = int(server.find('uptime').text)

                            for service in services:
                                name = service.find('name').text
                            
                                if name == hostname:
                                    memory_percent = service.find('.//system/memory/percent').text
                                    memory_kb = int(service.find('.//system/memory/kilobyte').text)

                                    cpu_user = float(service.find('.//system/cpu/user').text)
                                    cpu_system = float(service.find('.//system/cpu/system').text)
                                    cpu_nice = float(service.find('.//system/cpu/nice').text) if service.find('.//system/cpu/nice') is not None else 0.0
                                    cpu_wait = float(service.find('.//system/cpu/wait').text)

                                    memory_gb = memory_kb / (1024 ** 2)
                                    cpu_usage = cpu_user + cpu_system + cpu_nice + cpu_wait

                                    days = uptime // (24 * 3600)
                                    remaining_seconds = uptime % (24 * 3600)
                                    hours = remaining_seconds // 3600
                                    minutes = (remaining_seconds % 3600) // 60
                                    memory_gb = memory_kb / (1024 ** 2)

                                    uptime_formatted = f"{days} days {hours} hours, {minutes} minutes"


                                    message = f"SERVER : *{list[3]}*\n\n"
                                    message += "STATUS :\n"
                                    message += f"⏳ *Uptime* : {uptime_formatted}\n"
                                    message += f"🖥 *CPU Usage* : {cpu_usage:.2f}%\n"
                                    message += f"💾 *Memory* : {memory_percent}% \\[{memory_gb:.2f} GB]\n"

                                    keyboard = [
                                        [InlineKeyboardButton("Detail", callback_data=f"detail|{list[0]}")]
                                    ]
                                    reply_markup = InlineKeyboardMarkup(keyboard)

                                    logging.info(message)
                                    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')


                    except ET.ParseError as e:
                        logging.error(f"Error parsing XML data: {e}")
        else:
            await update.message.reply_text("No server in lists, please add server to check !")


def detail_service(host_id: int) -> str:
    servers = connect.list_server()
    if servers:
        for server in servers:
            if host_id == server[0]:
                xml_data = fetch_monit(server[1], server[2], server[3])

                for xml in xml_data:
                    xml_response = xml['response_text']

                    try:
                        root = ET.fromstring(xml_response)
                        services = root.findall('.//service')

                        detail_message = [f"*SERVER :* {server[3]}\n"]
                        for service in services:
                            name = service.find('name').text
                            status = service.find('status').text
                            monitor = service.find('monitor').text
                            type = service.get('type')

                            if type == '3':
                                if monitor == '1':
                                    if status == '0':
                                        uptime = int(service.find('uptime').text)
                                        status = int(service.find('status').text)
                                        memory_percent = service.find('.//memory/percenttotal').text
                                        memory_kb = int(service.find('.//memory/kilobytetotal').text)
                                        cpu_usage = float(service.find('.//cpu/percenttotal').text)

                                        days = uptime // (24 * 3600)
                                        remaining_seconds = uptime % (24 * 3600)
                                        hours = remaining_seconds // 3600
                                        minutes = (remaining_seconds % 3600) // 60
                                        memory_gb = memory_kb / (1024 ** 2)

                                        uptime_formatted = f"{days} days {hours} hours, {minutes} minutes"

                                        message = f"SERVICE : *{name}*\n"
                                        message += f"🟢 *Status* :  Online\n"
                                        message += f"⏳ *Uptime* : {uptime_formatted}\n"
                                        message += f"🖥 *CPU Usage* : {cpu_usage:.2f}%\n"
                                        message += f"💾 *Memory* : {memory_percent}% \\[{memory_gb:.2f} GB]\n"

                                        detail_message.append(message)
                                        logging.warning(message)
                                    else:
                                        message = f"SERVICE : *{name}*\n"
                                        message += f"🔴 *Status* : Issue\n"
                                        message += f"🗒 *Code* : {status}\n"

                                        detail_message.append(message)
                                        logging.error(message)
                                else:
                                    message = f"SERVICE : *{name}*\n"
                                    message += f"⚪️ *Status* : Monitor Disabled\n"

                                    detail_message.append(message)
                                    logging.info(message)

                        return detail_message
                    
                    except ET.ParseError as e:
                        logging.error(f"Error parsing XML data: {e}")
                        return None


async def cmd_bot_setting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat_id == TELEGRAM_CHAT_ID:
        setting = connect.bot_setting()

        message = "*Global TeleMonit_bot Setting* \n"
        message += f"⏳ Interval : {setting[1]} Second\n\n"
        message += "*Alert Parameter Setting*\n"
        message += f"🖥 CPU >= {setting[2]} %\n"
        message += f"💾 Memory >= {setting[3]} %\n\n"
        message += "*Note :* you can change this setting\nUsage : /set\\_setting <name> <value>\n"
        message += "Example : /set\\_setting interval 60\n"
        message += "Name : cpu, memory, interval"

        await update.message.reply_text(message, parse_mode='Markdown')


async def cmd_set_setting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat_id == TELEGRAM_CHAT_ID:
        if len (context.args) < 2:
            await update.message.reply_text(
                "Usage : /set_setting <name> <value>\nExample : /set_setting interval 60"
            )

        name_set = context.args[0]
        values = int(context.args[1])

        if name_set not in ("interval", "cpu", "memory"):
            await update.message.reply_text("Kamu hanya dapat mengubah interval, cpu dan memory \\!")
        else:
            connect.set_setting(name_set, values)
            await update.message.reply_text(f"Parameter {name_set} berhasil diubah menjadi {values}")


# Callback Handler ==================================================================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    action, host_id = query.data.split('|')

    if action == 'detail':
        detail_message = detail_service(int(host_id))
        await query.edit_message_text("\n".join(detail_message), parse_mode='Markdown')
    elif action == 'delete':
        if host_id == 'cancel':
            await query.edit_message_text(text="Delete server canceled")
        else:
            connect.del_server(int(host_id))
            await query.edit_message_text(text="Deleting server successfull")
    else:
        unknown_message = "Unknown action !"
        await query.edit_message_text(text=unknown_message)


# Runtime App =======================================================================
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', cmd_start))
    application.add_handler(CommandHandler('add_server', cmd_add_server))
    application.add_handler(CommandHandler('list_server', cmd_list_server))
    application.add_handler(CommandHandler('del_server', cmd_del_server))
    application.add_handler(CommandHandler('check_server', cmd_check_server))
    application.add_handler(CommandHandler('bot_setting', cmd_bot_setting))
    application.add_handler(CommandHandler('set_setting', cmd_set_setting))

    application.add_handler(CallbackQueryHandler(button_callback))

    application.run_polling()


if __name__ == '__main__':
    separator = "-" * 50
    ascii_art = r"""
  ______     __     __  ___            _ __       ____        __ 
 /_  __/__  / /__  /  |/  /___  ____  (_) /_     / __ )____  / /_
  / / / _ \/ / _ \/ /|_/ / __ \/ __ \/ / __/    / __  / __ \/ __/
 / / /  __/ /  __/ /  / / /_/ / / / / / /_     / /_/ / /_/ / /_  
/_/  \___/_/\___/_/  /_/\____/_/ /_/_/\__/____/_____/\____/\__/  
                                        /_____/                  
"""
                                 

    print(separator)
    print(ascii_art)
    print(separator)

    print("Starting TeleMonit_bot ...")
    
    monitor_thread = multiprocessing.Process(target=main)
    monitor_thread.start()

    print("Starting Monitor Alert ...")
    while True:
        servers = connect.list_server()
        setting = connect.bot_setting()

        for server in servers:
            xml_data = fetch_monit(server[1], server[2], server[3])
            if xml_data is None:
                logging.info("Monitoring is not performed as no servers are available.")
            else:
                parse_monit(xml_data)

        time.sleep(setting[1])