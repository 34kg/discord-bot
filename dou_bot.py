# This example requires the 'message_content' intent.

import discord
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
emoji_join  = '\N{RAISED HAND}'
emoji_redo  = '\N{LEFTWARDS ARROW WITH HOOK}'
emoji_end   = '\N{NO ENTRY SIGN}'

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
            await message.channel.send('usage: /dou [@n] [-e event_name] [-t title] [-s start time]')
            await message.delete()
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
        embed.add_field(name='Members',
                        value='',
                        inline=False)

        reply = await message.channel.send(content='@here', embed=embed)

        # Delete command massage
        await message.delete()

        # Add emoji
        await reply.add_reaction(emoji_join)
        await reply.add_reaction(emoji_redo)
        await reply.add_reaction(emoji_end)

@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.author.name.startswith(BOTNAME) and not user.name.startswith(BOTNAME):
        tmp_embed = reaction.message.embeds[0].copy()

        if reaction.emoji == emoji_join:
            print(f'{user.name}: +{emoji_join}')
            dict_embed = tmp_embed.to_dict()

            # Incliment status
            tmp_value = dict_embed['fields'][1]['value']
            dict_embed['fields'][1]['value'] = f"{reaction.count - 1}/{tmp_value.split('/')[-1]}"

            # Add to member list
            tmp_value = dict_embed['fields'][3]['value']
            dict_embed['fields'][3]['value'] = f"{tmp_value}\n<@{user.id}>"
            tmp_embed.from_dict(dict_embed)
            await reaction.message.edit(embed=tmp_embed)

        elif reaction.emoji == emoji_redo:
            print(f'{user.name}: +{emoji_redo}')
            dict_embed = tmp_embed.to_dict()

            # Redo reaction
            await reaction.message.remove_reaction(emoji_join, user)
            await reaction.message.remove_reaction(emoji_redo, user)

        elif reaction.emoji == emoji_end:
            # Finish event
            print(f'{user.name}: +{emoji_end}')
            #await reaction.message.delete()
            await reaction.message.clear_reactions()
            tmp_embed.description = '受付終了'
            await reaction.message.edit(embed=tmp_embed)

@client.event
async def on_reaction_remove(reaction, user):
    if reaction.message.author.name.startswith(BOTNAME) and not user.name.startswith(BOTNAME):
        tmp_embed = reaction.message.embeds[0].copy()

        if reaction.emoji == emoji_join:
            print(f'{user.name}: -{emoji_join}')
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


# Run Discord Bot
client.run(TOKEN)
