TOKEN = ""
    # YOUR BOT TOKEN
guildid = []
    # YOUR GUILD ID

import discord
from discord.ext import commands
from discord_slash import SlashContext, SlashCommand
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option, create_choice

channels = {} # ticket channels list

bot = commands.Bot(command_prefix="!")
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
    print("구동 완료")

@bot.event
async def on_command_error(ctx, error):
    pass

@slash.slash(
    name="문의채널",
    description="문의채널을 생성합니다.",
    options=[
        create_option(
            name="method",
            description="사용할 동작 (생성, 삭제)",
            option_type=SlashCommandOptionType.STRING,
            required=True,
            choices=[
                create_choice(name="create", value="create"),
                create_choice(name="delete", value="delete")
                ]
            )
        ],
    guild_ids=guildid
    )
async def ticket(ctx: SlashContext, method):
    global channels
    if (method == "create"):
        if str(ctx.author.id) in channels:
            await ctx.send("문의채널을 삭제하신 후 다시 시도해 주세요.")
            return
        if (not ctx.guild):
            await ctx.send("DM 채널에서는 사용할 수 없습니다.")
            return

        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True)
        }

        ticket_channel = await ctx.author.guild.create_text_channel(f"{ctx.author}님의 문의채널", overwrites=overwrites)
        channels.setdefault(str(ctx.author.id), ticket_channel) # global channels
        await ticket_channel.send(f'{ctx.author.mention}, 문의채널이 성공적으로 만들어졌습니다. 문의 후 문의채널을 삭제하세요.')
        await ctx.send("문의채널이 정상적으로 만들어졌습니다.")
        return

    else:
        if str(ctx.author.id) not in channels: # global channels
            await ctx.send("이용 중인 문의채널이 없습니다.")
            return
        if (not ctx.guild):
            await ctx.send("DM 채널에서는 사용할 수 없습니다.")
            return
        ticket_channel = channels.get(str(ctx.author.id)) # global channels
        channels = {k: v for k, v in channels.items() if k != str(ctx.author.id)} # delete user
        await ticket_channel.delete()
        dm = await ctx.author.create_dm()
        await dm.send("문의채널 삭제가 완료되었습니다.")

@slash.slash(
    name="강제삭제",
    description="문의채널을 강제 삭제합니다.",
    options=[
        create_option(
            name="target",
            description="강제 삭제할 유저",
            option_type=SlashCommandOptionType.USER,
            required=True
            )
        ],
    guild_ids=guildid
    )
async def 강제삭제(ctx: SlashContext, target):
    global channels
    if (not ctx.author.guild_permissions.administrator):
        await ctx.send("관리자 권한이 필요합니다.")
        return
    if (not ctx.guild):
        dm = await ctx.author.create_dm()
        await dm.send("DM 채널에서는 사용할 수 없습니다.")
        return
    if str(target.id) not in channels: # global channels
        await ctx.send(f"{target}님이 이용 중인 문의채널이 없습니다.")
        return
    ticket_channel = channels.get(str(target.id)) # global channels
    channels = {k: v for k, v in channels.items() if k != str(target.id)} # delete user
    await ticket_channel.delete()
    dm = await ctx.author.create_dm()
    await dm.send("문의채널 삭제가 완료되었습니다.")

bot.run(TOKEN)
