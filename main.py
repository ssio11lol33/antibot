import discord
from discord.ext import commands
import asyncio
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

GESCHÜTZTE_ROLLEN = [
    1363573793355858124,
    1363570800363569453,
    1363570799969173697,
    1363570799520514339
    ]

OWNER_ID = int(os.getenv("OWNER_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))

@bot.event
async def on_ready():
    print(f"✅ Bot online als {bot.user}")

@bot.event
async def on_member_update(before, after):
    added_roles = [role for role in after.roles if role not in before.roles]

    for role in added_roles:
        if role.id in GESCHÜTZTE_ROLLEN:
            await asyncio.sleep(1)

            async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_role_update):
                if entry.target.id == after.id and role in entry.changes.after:
                    täter = entry.user
                    if täter.id == bot.user.id:
                        return

                    await after.remove_roles(role, reason="Verbotene Rolle vergeben")

                    try:
                        await täter.edit(roles=[], reason="Unbefugte Rollenvergabe")
                    except:
                        pass

                    log_channel = bot.get_channel(LOG_CHANNEL_ID)
                    if log_channel:
                        await log_channel.send(
                            f"⚠️ **{täter.mention}** hat `{role.name}` an {after.mention} vergeben.\n➡️ Rolle entfernt, Täter entrollt."
                        )

                    try:
                        owner = await bot.fetch_user(OWNER_ID)
                        await owner.send(
                            f"🚨 Warnung:\n**{täter}** hat `{role.name}` an **{after}** vergeben.\nIch habe eingegriffen."
                        )
                    except:
                        pass

                    break

bot.run(os.getenv("TOKEN"))
