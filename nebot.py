# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from openai import AsyncOpenAI
from discord import app_commands
import json
import asyncio
import base64
import httpx

# Message history
chat_histories = {}

class AI_Bot:
    def __init__(self, config_path="config.json", gui_app=None):
        self.gui = gui_app
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.token = self.config.get("Token") or self.config.get("discord_token")
        self.prefix = self.config.get("Prefix") or self.config.get("bot_prefix", "/")
        self.api_url = self.config.get("lm_studio_url", "http://127.0.0.1:1234/v1")

        self.ai_client = AsyncOpenAI(base_url=self.api_url, api_key="lm-studio")
        
        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = commands.Bot(command_prefix=self.prefix, intents=intents)
        
        # Command tree
        self.setup_events()

    async def get_model_name(self):
        try:
            models = await self.ai_client.models.list()
            if models.data:
                return models.data[0].id.split('/')[-1].split('\\')[-1]
            return "Model not loaded"
        except:
            return "Local Model"

    def setup_events(self):
        @self.bot.event
        async def on_ready():
            model_name = await self.get_model_name()
            
            # Sync command
            try:
                synced = await self.bot.tree.sync()
                log_msg = f"Sync command: {len(synced)}"
            except Exception as e:
                log_msg = f"Error sync: {e}"

            if self.gui:
                self.gui.add_log(f"Bot {self.bot.user.name} online!")
                self.gui.add_log(log_msg)
                self.gui.info_label.configure(text=f"Model: {model_name} | Bot: @{self.bot.user.name}")

        # Registration command
        @self.bot.tree.command(name="model", description="Find out the current AI model")
        async def model_slash(interaction: discord.Interaction):
            name = await self.get_model_name()
            await interaction.response.send_message(f"🤖 The model is running on the device: `{name}`")

        @self.bot.event
        async def on_message(message):
            if message.author == self.bot.user: return
            
            await self.bot.process_commands(message)

            if not message.content.startswith('/'):
                if self.bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
                    prompt = message.content.replace(f'<@{self.bot.user.id}>', '').strip()
                    
                    if self.gui:
                        self.gui.add_log(f"Request from: {message.author.name}")
                    
                    asyncio.create_task(self.process_ai_request(message, prompt, message.attachments))

    async def process_ai_request(self, message, prompt, attachments):
        if self.gui:
            self.gui.status_label.configure(text="Generation...", fg_color="orange")

        try:
            user_id = str(message.author.id)
            user_name = message.author.name
            
            if user_id not in chat_histories:
                chat_histories[user_id] = []

            content = []
            # AI sees who is writing
            text_val = f"[{user_name}]: {prompt}" if prompt else f"[{user_name}]: (send image)"
            content.append({"type": "text", "text": text_val})

            has_image = False
            for attach in attachments:
                if any(attach.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp']):
                    async with httpx.AsyncClient() as client:
                        resp = await client.get(attach.url)
                        b64 = base64.b64encode(resp.content).decode('utf-8')
                        content.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                        })
                        has_image = True

            chat_histories[user_id].append({"role": "user", "content": content})
            
            if has_image:
                context = [chat_histories[user_id][-1]]
            else:
                context = chat_histories[user_id][-5:]

            async with message.channel.typing():
                response = await self.ai_client.chat.completions.create(
                    model="local-model",
                    messages=context,
                    max_tokens=4096,
                    temperature=0.7
                )

                answer = response.choices[0].message.content
                if not answer: answer = "⚠️ Empty answer"

                chat_histories[user_id].append({"role": "assistant", "content": answer})
                await message.reply(answer)

        except Exception as e:
            if self.gui: self.gui.add_log(f"Ошибка: {e}")
            await message.reply(f"❌ Ошибка: {e}")

        if self.gui:
            self.gui.status_label.configure(text="Idle", fg_color="#2b2b2b")

    def clear_all_history(self):
        chat_histories.clear()
        if self.gui: self.gui.add_log("--- Memory cleared ---")
        return "History cleared."

    async def start_bot(self):
        await self.bot.start(self.token)

    async def stop_bot(self):
        await self.bot.close()