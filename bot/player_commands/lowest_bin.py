import discord
from discord.ext import commands

import requests  # For making the api call
from datetime import datetime  # To convert hypixel time string to object

from utils import error, hf, format_duration, RARITY_DICT, find_closest

def format_enchantments(enchantments):
    if not enchantments:
        return ""
    enchantment_pairs = [enchantments[i:i + 2] for i in range(0, len(enchantments), 2)]
    if len(enchantment_pairs[-1]) == 1:
        enchantment_pairs[-1] = (enchantment_pairs[-1][0], "")

    enchantment_string = "\n".join([f"[{first} {second}]" for first, second in enchantment_pairs])

    formatted_enchants = f'''```ini
[Enchantments]
{enchantment_string}
```
'''
    return formatted_enchants


class lowest_bin_cog(commands.Cog):
    def __init__(self, bot):
        self.client = bot

    @commands.command(aliases=['lb', 'bin', 'lbin'])
    async def lowest_bin(self, ctx, *, input_item=None):
        closest = await find_closest(ctx, input_item)
        if closest is None:
            return

        response = requests.get(f"https://sky-preview.coflnet.com/api/item/price/{closest['internal_name']}/bin").json()

        if "Slug" in response.keys() or "uuid" not in response.keys():
            return await error(ctx, "Error, not items of that type could be found on the auction house!", "Try a different item instead?")
        response = requests.get(f"https://sky-preview.coflnet.com/api/auction/{response['uuid']}").json()
        data = response

        price = data['highestBidAmount'] or data['startingBid'] # 2021-07-30T11:06:19Z
        time_left = format_duration(datetime.strptime(data['end'].rstrip("Z"), '%Y-%m-%dT%H:%M:%S'))
        enchantments = format_enchantments(data["enchantments"])

        formatted_auction = f"↳ Price: {hf(price)}\n↳ Time Remaining: {time_left}"+enchantments
            
        embed = discord.Embed(title=f"Lowest bin found for {RARITY_DICT[response['tier']]} {response['itemName']}:", description=formatted_auction, colour=0x3498DB)
        embed.set_footer(text=f"Command executed by {ctx.author.display_name} | Community Bot. By the community, for the community.")        
        await ctx.send(embed=embed)

