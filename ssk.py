import discord
from config import settings
from discord.ui import Button, View
from discord.ext import commands
import asyncio
from discord import Option

intents = discord.Intents.all()
intents.message_content = True
intents.voice_states = True
intents.guild_messages = True
bot = commands.Bot(command_prefix='!',intents=intents)
ticket_category_name = 'Buyers'
active_timers = {} 

class HelpView(View):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    @discord.ui.button(label='Купить Nitro', style=discord.ButtonStyle.green,)
    async def members_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await ticket(interaction)

@bot.command()
async def bhelp(ctx: discord.ApplicationContext):
    emb = discord.Embed(title='\u200b')
    emb.set_image(url="https://i.imgur.com/ggxP53y.png")
    emb2 = discord.Embed(title='⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Discord Nitro')
    emb2.description = "⠀⠀<a:f_:1021333160673431583>**Nitro Full⠀⠀⠀⠀⠀⠀<a:basicclassic:1185156808185233458>Nitro Classic⠀⠀⠀⠀⠀⠀⠀⠀⠀<a:basicclassic:1185156808185233458>Nitro Basic**"
    emb2.add_field(name="<a:full:1184933699473657987>Nitro Full(1 Месяц)", value="[**Цена: 250₽ ~~350₽~~**](https://discord.com/channels/1020678578133807125/1163779229608071188)", inline=True)
    emb2.add_field(name="<a:classic:1171562237081681970>Nitro Classic(1 Месяц)", value="[**Цена: 170₽ ~~270₽~~**](https://discord.com/channels/1020678578133807125/1163779229608071188)", inline=True)
    emb2.add_field(name="<a:classic:1171562237081681970>Nitro Basic(1 Месяц)", value="[**Цена: 100₽ ~~240₽~~**](https://discord.com/channels/1020678578133807125/1163779229608071188)", inline=True)

    emb2.add_field(name="<a:full:1184933699473657987>Nitro Full(1 Год)", value="[**Цена: 2500₽ ~~3500₽~~**](https://discord.com/channels/1020678578133807125/1163779229608071188)", inline=True)
    emb2.add_field(name="<a:classic:1171562237081681970>Nitro Classic(1 Год)", value="[**Цена: 1700₽ ~~2700₽~~**](https://discord.com/channels/1020678578133807125/1163779229608071188)", inline=True)
    emb2.add_field(name="<a:classic:1171562237081681970>Nitro Basic(1 Год)", value="[**Цена: 1000₽ ~~2000₽~~**](https://discord.com/channels/1020678578133807125/1163779229608071188)", inline=True)
    view = HelpView(ctx.send)
    await ctx.send(embeds=[emb,emb2], view=view)

async def ticket(interaction: discord.Interaction):
    ticket_channel = await create_temporary_channel(interaction.user)
    await interaction.response.send_message(f'Для вас создан персональный тикет: {ticket_channel.mention}', ephemeral=True)
    await send_close_ticket_message(ticket_channel, interaction)

async def create_temporary_channel(author):
    guild = author.guild
    category = discord.utils.get(guild.categories, name=ticket_category_name)

    if category is None:
        category = await guild.create_category(name=ticket_category_name)
    ticket_channel = await category.create_text_channel(name=f"ticket-{author.name}",
                                                       overwrites=await get_channel_overwrites(guild, author))

    return ticket_channel

async def get_channel_overwrites(guild, author):
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        author: discord.PermissionOverwrite(read_messages=True)
    }
    return overwrites

async def send_close_ticket_message(channel,interaction):
    class CloseTicketView(View):
        async def move_channel(self, channel):
            closed_category = discord.utils.get(channel.guild.categories, name='Closed Tickets')
            if closed_category is None:
                closed_category = await channel.guild.create_category(name='Closed Tickets')
                
            overwrites = {
                channel.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                channel.guild.me: discord.PermissionOverwrite(view_channel=False)
                }

            await channel.edit(category=closed_category, overwrites=overwrites)

        @discord.ui.button(label='Закрыть тикет', style=discord.ButtonStyle.danger, emoji='🔒')
        async def close_ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
            try:
                await self.move_channel(channel)
                await interaction.response.send_message("Тикет Закрыт.")
            except Exception as e:
                print(f'Ошибка при закрытии тикета: {e}')

        @discord.ui.button(label='Оплатить товар', style=discord.ButtonStyle.green)
        async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
            try:
                last_message = await channel.fetch_message(channel.last_message_id)

                if last_message.attachments:
                    file_name = last_message.attachments[0].filename
                    if file_name.lower().endswith(('png', 'jpeg', 'jpg', 'gif')):
                        await interaction.response.send_message("<@350970672769662976> \nВам отправят фотку QR CODE, Вам нужно будет с телефона отсканировать его, И разрешить вход в аккаунт продавцу.\nПосле этого останеться ожидать пару минут")
                    else:
                        await interaction.response.send_message("Последнее сообщение не является чеком оплаты", ephemeral=True)
                else:
                    await interaction.response.send_message("Последнее сообщение не является чеком оплаты", ephemeral=True)
            except Exception as e:
                print(f'Ошибка при обработке взаимодействия "Оплатил": {e}')
                
    embed = discord.Embed(title='Способы Оплаты', description='\n<:usdt:1185162792874024990> USDT - Обговаривается с @en0ken  \n\n<:sb:1021362818211123200> Сбербанк - 2202202382042251 Егор А.М  \n\n<:tink:1185162482701054012> Тинькоф - 2200700950019496 Михаил Д.  \n\n**После оплаты присылайте чек и нажимайте на зеленую кнопку.**')
    second_message_content = f"<@{interaction.user.id}>, Привет, я SSK, твой пероснальный помощник в выборе и покупке Nitro, давай начнем с того какое ты Nitro хочешь на выбор есть \n1) Nitro Full(1 Месяц) \n2) Nitro Classic(1 Месяц) \n3) Nitro Basic(1 Месяц) \n4) Nitro Full(1 Год) \n5) Nitro Classic(1 Год) \n6) Nitro Basic(1 Год) \n **Выбери номер и напиши его в чат!**"
    second_message = await channel.send(second_message_content)
    view = CloseTicketView()
    message = await channel.send(embed = embed, view=view)
    return second_message,message

@bot.event
async def on_message(message):
    if message.author.bot:
        return 

    content = message.content.lower()

    if "1" in content:
        response = "Вы выбрали Nitro Full(1 месяц) - его цена 200р \nМожете проводить оплату, после чего кидайте чек в канал и нажимайте на зеленую кнопку в 1 сообщении"
    elif "2" in content:
        response = "Вы выбрали Nitro Classic(1 месяц) - его цена 200р \nМожете проводить оплату, после чего кидайте чек в канал и нажимайте на зеленую кнопку в 1 сообщении"
    elif "3" in content:
        response = "Вы выбрали Nitro Basic(1 месяц) - его цена 200р \nМожете проводить оплату, после чего кидайте чек в канал и нажимайте на зеленую кнопку в 1 сообщении"
    elif "4"  in content:
        response = "Вы выбрали Nitro Full(1 год) - его цена 2000р \nМожете проводить оплату, после чего кидайте чек в канал и нажимайте на зеленую кнопку в 1 сообщении"
    elif "5" in content:
        response = "Вы выбрали Nitro Classic(1 год) - его цена 2000р \nМожете проводить оплату, после чего кидайте чек в канал и нажимайте на зеленую кнопку в 1 сообщении"
    elif "6" in content:
        response = "Вы выбрали Nitro Basic(1 год) - его цена 2000р \nМожете проводить оплату, после чего кидайте чек в канал и нажимайте на зеленую кнопку в 1 сообщении"
    else:
        response = None 
    if response:
        await message.channel.send(response)

    await bot.process_commands(message)

target_channel_id = 1173239464588476507  

@bot.slash_command(id_server = [settings['id_server']])
async def timerstart(ctx: discord.ApplicationContext, user: discord.User, duration: Option(str, name='период', description='Месяц/Год', required=True)):
    duration = duration.lower()
    
    if duration not in ['месяц', 'год']:
        await ctx.send("Неверный формат длительности. Используйте 'месяц' или 'год'.")
        return

    if duration == 'месяц':
        time_seconds = 30 * 24 * 60 * 60 
    else: 
        time_seconds = 365 * 24 * 60 * 60  

    active_timers[user.id] = time_seconds
    await ctx.send(f"Таймер на {duration} для {user.mention} запущен.")

    await asyncio.sleep(time_seconds)  
    del active_timers[user.id]

    target_channel = bot.get_channel(target_channel_id)
    await target_channel.send(f"{user.mention}, у вас кончилось нитро. Давайте оформим новое!")


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

bot.run(settings['token'])
