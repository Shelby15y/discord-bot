import nextcord
from nextcord.ext import commands, tasks
from nextcord import DMChannel, Interaction, SlashOption, ChannelType, Message, Attachment, ApplicationCommand
from nextcord.abc import GuildChannel
from nextcord.ui import Button, View, Modal, TextInput
import string
import asyncio
from random import choice,randint
import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://Film:Film130350F@cluster0.aegll.mongodb.net/?retryWrites=true&w=majority")
DB = client.Form

intents = nextcord.Intents.default()
intents.members = True
intents.guilds = True
intents.messages = True

prefix = "-"
bot = commands.Bot(command_prefix=commands.when_mentioned_or(
    prefix), case_insensitive=True, intents=intents, help_command=None,)

guild = []


@bot.slash_command(name="purge", description="ล้างห้อง", guild_ids=guild)
async def purge_room(Interaction: Interaction, channel: GuildChannel = SlashOption(name="channel", description="ช่อง"), limit: int = SlashOption(name="limit", description="จำนวนคำที่ต้องการล้าง")):
    await Interaction.send(f"ล้างห้อง {channel.name} จำนวน {limit} คำ")
    await channel.purge(limit=limit)

@bot.slash_command(name="kick", description="เตะออกดิส", guild_ids=guild)
async def kick(Interaction: Interaction, member: nextcord.Member=SlashOption(name="member", description="คนที่คุณจะเตะออกจาดิส"), reason: str = SlashOption(name="reason", description="สาเหตุการเตะ")):
    await Interaction.response.defer(ephemeral=True)
    if Interaction.user.guild_permissions.kick_members == True:
        await member.kick(reason=reason)
        await Interaction.send("เตะเสร็จสิ้น")
        await Interaction.channel.send(f"ผู้ถูกเตะ: {member.mention}\nผู้เตะ:{Interaction.user.mention}\nสาเหตุ: {reason}")
    else:
        await Interaction.send("คุณไม่มีสิทธิ์ในการเตะผู้ใช้", ephemeral=True)


@bot.slash_command(name="ban", description="แบน", guild_ids=guild)
async def ban(Interaction: Interaction, member: nextcord.Member = SlashOption(name="member", description="คนที่คุณจะแบน"), reason: str = SlashOption(name="reason", description="สาเหตุการแบน")):
    await Interaction.response.defer(ephemeral=True)
    if Interaction.user.guild_permissions.ban_members == True:
        await member.ban(reason=reason)
        await Interaction.send("แบนเสร็จสิ้น")
        await Interaction.channel.send(f"ผู้ถูกแบน: {member.mention}\nผู้แบน: {Interaction.user.mention}\nสาเหตุ: {reason}")
    else:
        await Interaction.send("คุณไม่มีสิทธิ์ในการแบน", ephemeral=True)


@bot.slash_command(name="unban", description="ปลดแบน", guild_ids=guild)
async def unban(Interaction: Interaction, user=SlashOption(name="user", description="คนที่คุณจะปลดแบน"), reason: str = SlashOption(name="reason", description="สาเหตุการปลดแบน")):
    await Interaction.response.defer(ephemeral=True)
    if Interaction.user.guild_permissions.ban_members == True:
        BanEntry = await Interaction.guild.bans()
        user_name, user_discriminator = user.split('#')
        for i in BanEntry:
            ban_user = i.user
            if (user_name, user_discriminator) == (ban_user.name, ban_user.discriminator):
                await Interaction.guild.unban(ban_user, reason=reason)
                await Interaction.send("ปลดแบนเสร็จสิ้น")
                await Interaction.channel.send(f"ผู้ถูกปลดแบน: {ban_user.mention}\nผู้ปลดแบน: {Interaction.user.mention}\nสาเหตุ: {reason}")
                return
    else:
        await Interaction.send("คุณไม่มีสิทธิ์ในการปลดแบน", ephemeral=True)


@unban.on_autocomplete("user")
async def unban_user(Interaction: Interaction, user):
    BanEntry = await Interaction.guild.bans()
    baned_user = []
    for i in BanEntry:
        user = [i.user.name, i.user.discriminator]
        user = "#".join(user)
        baned_user.append(user)
    if not user:
        await Interaction.response.send_autocomplete(baned_user)
        return
    get_user = [
        user for user in baned_user if user.lower().startswith(user.lower())]
    await Interaction.response.send_autocomplete(get_user)


@bot.slash_command(name="randomcode",description="สุ่มรหัส", guild_ids=guild)
async def random_code(Interaction: Interaction):
    characters = string.ascii_letters  + string.digits
    code = "".join(choice(characters)for x in range(randint(8, 16)))
    await Interaction.send(code, ephemeral=True)
    
@bot.slash_command(name="getallfrom",description="ดึงข้อมูลจากแบบฟอร์ม", guild_ids=guild)
async def get_all_from(Interaction: Interaction):
    uerdb = DB.user.find()
    embed = nextcord.Embed(title="ข้อมูลผู้ใช้", color=0x00ff00)
    if len(dict(uerdb)) < 0:
        for i,u in enumerate(uerdb):
            name = u["name"]
            id = u["id"]
            number = u["number"]
            code = u["code"]
            day = u["day"]
            embed.add_field(name=f"{i}. **{name}**",value=f"┗Name: <@{id}>\n┗ID: {id}\n┗Number: {number}\n┗Code: {code}\n┗Day: {day}",inline=False)
    else:
        embed.add_field(name="ดึงข้อมูล", value="ไม่มีข้อมูล")
    await Interaction.send(embed=embed)
    
@bot.slash_command(name="getuserfrom",description="ดึงข้อมูลผู้ใช้จากแบบฟอร์ม", guild_ids=guild)
async def get_user_from(Interaction: Interaction,user:nextcord.Member = SlashOption(name="user", description="ผู้ใช้ที่คุณต้องการดึงข้อมูล")):
    uerdb = await DB.user.find_one({"name":str(user),"id":user.id})
    embed = nextcord.Embed(title="ข้อมูลผู้ใช้", color=0x00ff00)
    if uerdb:
        name = uerdb["name"]
        id = uerdb["id"]
        number = uerdb["number"]
        code = uerdb["code"]
        day = uerdb["day"]
        embed.add_field(name=f"**{name}**",value=f"┗Name: <@{id}>\n┗ID: {id}\n┗Number: {number}\n┗Code: {code}\n┗Day: {day}",inline=False)
        embed.set_thumbnail(url=user.avatar_url)
    else:
        embed.add_field(name="ข้อมูลผู้ใช้", value="ไม่มีข้อมูล")
    await Interaction.send(embed=embed)
    
bot.run("OTYwNDYyNDY1Mjk1MDY5MjE1.GF5_Rx.7DGX64Y0TIT8vSUd71FJhAIMWqgKsH_WWa9pqQ")