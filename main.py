import discord
import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.getenv(TOKEN)

intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"ログインしました: {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return
    
    if message.content.startswith("!ipa"):
        args = message.content.split(" ")
        if len(args) < 2:
            await message.reply("アプリの App Store リンクを入力してください！")
            return

        app_store_url = args[1]
        if "apps.apple.com" not in app_store_url:
            await message.reply("有効な App Store のリンクを入力してください！")
            return

        try:
            app_name = get_app_name(app_store_url)
            results = search_decrypt_day(app_name)

            if not results:
                await message.reply(f"「{app_name}」に一致する IPA は見つかりませんでした。")
                return

            response = f"**{app_name} の IPA:**\n"
            for r in results:
                response += f"{r['name']}\n{r['link']}\n\n"

            await message.reply(response)

        except Exception as e:
            await message.reply("エラーが発生しました。もう一度試してください！")
            print(e)

def get_app_name(url):
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")
    return soup.title.text.split(" - ")[0].strip()

def search_decrypt_day(app_name):
    search_url = f"https://decrypt.day/search?q={app_name}"
    res = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")
    results = []

    for result in soup.select(".app-result"):
        name = result.select_one(".app-title").text.strip()
        link = result.select_one(".download-link")["href"]
        results.append({"name": name, "link": link})

    return results

client.run(TOKEN)
