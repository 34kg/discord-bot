# This example requires the 'message_content' intent.

import discord
import asyncio
import os
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True
intents.reactions       = True
intents.members         = True

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
BOTNAME = 'douBot'
client = discord.Client(intents=intents)
emoji_join      = '\N{THUMBS UP SIGN}'
emoji_pass      = '\N{THUMBS DOWN SIGN}'
emoji_end       = '\N{NO ENTRY SIGN}'
emoji_times = {
        '\N{CLOCK FACE ONE OCLOCK}':    '1:00-',
        '\N{CLOCK FACE ONE-THIRTY}':    '1:30-',
        '\N{CLOCK FACE TWO OCLOCK}':    '2:00-',
        '\N{CLOCK FACE TWO-THIRTY}':    '2:30-',
        '\N{CLOCK FACE THREE OCLOCK}':  '3:00-',
        '\N{CLOCK FACE THREE-THIRTY}':  '3:30-',
        '\N{CLOCK FACE FOUR OCLOCK}':   '4:00-',
        '\N{CLOCK FACE FOUR-THIRTY}':   '4:30-',
        '\N{CLOCK FACE FIVE OCLOCK}':   '5:00-',
        '\N{CLOCK FACE FIVE-THIRTY}':   '5:30-',
        '\N{CLOCK FACE SIX OCLOCK}':    '6:00-',
        '\N{CLOCK FACE SIX-THIRTY}':    '6:30-',
        '\N{CLOCK FACE SEVEN OCLOCK}':  '7:00-',
        '\N{CLOCK FACE SEVEN-THIRTY}':  '7:30-',
        '\N{CLOCK FACE EIGHT OCLOCK}':  '8:00-',
        '\N{CLOCK FACE EIGHT-THIRTY}':  '8:30-',
        '\N{CLOCK FACE NINE OCLOCK}':   '9:00-',
        '\N{CLOCK FACE NINE-THIRTY}':   '9:30-',
        '\N{CLOCK FACE TEN OCLOCK}':    '10:00-',
        '\N{CLOCK FACE TEN-THIRTY}':    '10:30-',
        '\N{CLOCK FACE ELEVEN OCLOCK}': '11:00-',
        '\N{CLOCK FACE ELEVEN-THIRTY}': '11:30-',
        '\N{CLOCK FACE TWELVE OCLOCK}': '12:00-',
        '\N{CLOCK FACE TWELVE-THIRTY}': '12:30-'
}


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('/dou'):
        cmd_list = message.content.split()
        if cmd_list[0] == '/dou?' or '-h' in cmd_list:
            await asyncio.gather(
                message.channel.send('usage: /dou [@n] [-e event_name] [-t title] [-s start time]'),
                message.delete(),
            )
            return

        # Default value
        title       = '今日どう？'
        color       = 0x007700
        description = '回答受付中' if not '-d' in cmd_list else ''
        capacity    = message.guild.member_count - 1
        start_time  = 'いつでも'
        event_name  = 'なんでも'

        # Overwrite value
        for idx in range(1, len(cmd_list)):
            if cmd_list[idx].startswith('@'):
                capacity    = int(cmd_list[idx].split('@')[-1]) + 1
            elif cmd_list[idx] == '-t':
                title       = cmd_list[idx+1]
            elif cmd_list[idx] == '-s':
                start_time  = cmd_list[idx+1]
            elif cmd_list[idx] == '-e':
                event_name  = cmd_list[idx+1]

        embed = discord.Embed(
                  title=title,
                  color=color,
                  description=description,
                )
        embed.add_field(name='Time',
                        value=f'{start_time}',
                        inline=False)
        embed.add_field(name='Status',  value=f'0/{capacity}')
        embed.add_field(name='Event',   value=event_name)
        embed.add_field(name='Join',
                        value='',
                        inline=False)
        embed.add_field(name='Pass',
                        value='',
                        inline=False)
        embed.add_field(name='Reserve',
                        value='',
                        inline=False)

        reply = await message.channel.send(content='@here', embed=embed)

        # Delete command massage
        await message.delete()

        # Add emoji
        await asyncio.gather(
            reply.add_reaction(emoji_join),
            reply.add_reaction(emoji_pass),
            reply.add_reaction(emoji_end),
        )

@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.author.name.startswith(BOTNAME) and not user.name.startswith(BOTNAME):
        tmp_embed = reaction.message.embeds[0].copy()

        print(f'{user.name}: +{reaction.emoji}')
        if reaction.emoji == emoji_join:
            # 参加
            dict_embed = tmp_embed.to_dict()

            # Incliment status
            tmp_value = dict_embed['fields'][1]['value']
            dict_embed['fields'][1]['value'] = f"{reaction.count - 1}/{tmp_value.split('/')[-1]}"

            # Add to member list
            tmp_value = dict_embed['fields'][3]['value']
            dict_embed['fields'][3]['value'] = f"{tmp_value}\n<@{user.id}>"
            tmp_embed.from_dict(dict_embed)
            await asyncio.gather(
                reaction.message.edit(embed=tmp_embed),
                reaction.message.remove_reaction(emoji_pass, user),
            )

        elif reaction.emoji == emoji_pass:
            # 不参加
            dict_embed = tmp_embed.to_dict()

            # Add to member list
            tmp_value = dict_embed['fields'][4]['value']
            dict_embed['fields'][4]['value'] = f"{tmp_value}\n<@{user.id}>"
            tmp_embed.from_dict(dict_embed)

            await asyncio.gather(
                reaction.message.edit(embed=tmp_embed),
                reaction.message.remove_reaction(emoji_join, user),
            )

        elif reaction.emoji in emoji_times:
            # リザーブメンバー追加
            dict_embed = tmp_embed.to_dict()

            # Add to member list
            tmp_value = dict_embed['fields'][5]['value']
            dict_embed['fields'][5]['value'] = f"{tmp_value}\n<@{user.id}> ({emoji_times[reaction.emoji]}"
            tmp_embed.from_dict(dict_embed)
            await reaction.message.edit(embed=tmp_embed)

        elif reaction.emoji == emoji_end:
            # イベント終了
            #await reaction.message.delete()
            tmp_embed.description = '受付終了'
            await asyncio.gather(
                reaction.message.edit(embed=tmp_embed),
                reaction.message.clear_reactions(),
            )

@client.event
async def on_reaction_remove(reaction, user):
    if reaction.message.author.name.startswith(BOTNAME) and not user.name.startswith(BOTNAME):
        tmp_embed = reaction.message.embeds[0].copy()
        print(f'{user.name}: -{reaction.emoji}')

        if reaction.emoji == emoji_join:
            dict_embed = tmp_embed.to_dict()

            # Update status
            tmp_value = dict_embed['fields'][1]['value']
            dict_embed['fields'][1]['value'] = f"{reaction.count - 1}/{tmp_value.split('/')[-1]}"

            # Rmove from member list
            tmp_value = dict_embed['fields'][3]['value']
            list_member = tmp_value.split('\n')
            list_member.remove(f'<@{user.id}>')
            str_member = '\n'.join(list_member)
            dict_embed['fields'][3]['value'] = f"{str_member}"
            tmp_embed.from_dict(dict_embed)
            await reaction.message.edit(embed=tmp_embed)

        if reaction.emoji == emoji_pass:
            dict_embed = tmp_embed.to_dict()

            # Rmove from member list
            tmp_value = dict_embed['fields'][4]['value']
            list_member = tmp_value.split('\n')
            list_member.remove(f'<@{user.id}>')
            str_member = '\n'.join(list_member)
            dict_embed['fields'][4]['value'] = f"{str_member}"
            tmp_embed.from_dict(dict_embed)
            await reaction.message.edit(embed=tmp_embed)

        elif reaction.emoji in emoji_times:
            dict_embed = tmp_embed.to_dict()

            # Rmove from member list
            tmp_value = dict_embed['fields'][5]['value']
            list_member = tmp_value.split('\n')
            list_member.remove(f'<@{user.id}> ({emoji_times[reaction.emoji]}')
            str_member = '\n'.join(list_member)
            dict_embed['fields'][5]['value'] = f"{str_member}"
            tmp_embed.from_dict(dict_embed)
            await reaction.message.edit(embed=tmp_embed)

# Run Discord Bot
client.run(TOKEN)
