import discord
import datetime
import random
import os
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
d_guild = "The Friday 15 - Cyber Chats | Cyber Speed Networking"
bot = commands.Bot(command_prefix='!')


@commands.has_role('Admins')
@bot.command(name='check_in', help='Builds a check in message for the Friday 15!')
async def check_in(ctx):
    channel = discord.utils.get(ctx.guild.channels, name='check-in')
    next_friday = get_date()
    response = f"It's that time again!\n\nPlease add reaction \U0001f44d to check in for {next_friday}."

    send_message = await channel.send(response)

    await send_message.add_reaction('\U0001f44d')
    await ctx.send('Check in posted successfully.')


@bot.command(name='pair_up', help='Collect list of emoji-ers!')
async def pair_up(ctx):
    guild = ctx.guild
    channel = discord.utils.get(ctx.guild.channels, name='check-in')
    messages = await channel.history(limit=5).flatten()
    next_friday = get_date()
    user_list = ['user_1', 'user_2', 'user_3', 'user_4']
    group_dict = {}

    # find all users that added a reaction.
    for message in messages:
        chan_history = await channel.fetch_message(message.id)
        if f'for {next_friday}' in chan_history.content:
            for reaction in message.reactions:
                async for user in reaction.users():
                    if 'Friday15' in user.name:
                        pass
                    else:
                        user_list.append(f'{user.name}#{user.discriminator}')
            break

    # break out the users into groups of 2 (3 at the end if odd number)
    if len(user_list) > 1:
        random.shuffle(user_list)
        if len(user_list) % 2 != 0:
            user_list.append('blank_user')
        g_counter = 1

        for u1, u2 in zip(user_list[::2], user_list[1::2]):
            if 'blank_user' in u2:
                group_len = len(group_dict)
                group_dict[group_len].append(u1)
            else:
                dict_temp = {g_counter: [u1, u2]}
                # print(f'Group {g_counter} - {u1}, {u2}')
                group_dict.update(dict_temp)
            g_counter += 1

        discord_message = f'The Friday 15 Pairing List:\n\nDate - {next_friday}\n\n'
        for group in group_dict:
            discord_message = f'{discord_message}Group {str(group)}: {", ".join(group_dict[group])}\n'
            disc_cat = await ctx.guild.create_category(f'group_{str(group)}')
            await guild.create_text_channel(f'Text Channel', category=disc_cat)
            await guild.create_voice_channel(f'Voice Channel', category=disc_cat)

        # output group list to discord.
        # print(discord_message)
        await channel.send(discord_message)
        await ctx.send('Pairing list posted successfully.')
    else:
        await ctx.send('Not enough participants found.')


@bot.command(name='teardown', help='Deletes the groups and posts a thank you message.')
async def teardown(ctx):
    groups_found = False
    ci_channel = discord.utils.get(ctx.guild.channels, name='check-in')
    for category in ctx.guild.categories:
        if 'group' in category.name.lower():
            for channels in category.channels:
                if 'text' in channels.name.lower() or 'voice' in channels.name.lower():
                    channel = bot.get_channel(channels.id)
                    await channel.delete()
            await category.delete()
            groups_found = True

    if groups_found:
        await ctx.send('All groups and channels have been removed.')
        await ci_channel.send('Thank you for attending! The Friday 15 is now closed.')
    else:
        await ctx.send('No groups/channels found to teardown.')


def get_date():

    current_date = datetime.date.today()

    while current_date.strftime('%a') != 'Fri':
        current_date += datetime.timedelta(1)

    next_friday = current_date.strftime('%m/%d/%Y')

    return next_friday


if __name__ == "__main__":
    bot.run(TOKEN)
