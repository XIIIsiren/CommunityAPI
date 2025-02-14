import discord

from utils import hf, clean
from networth.generate_description import generate_description
from networth.constants import page_names, PAGE_TO_IMAGE, PAGE_TO_EMOJI

def format_info(total, item, value):
    name = item['name'] if 'name' in item else f"[Lvl {value['pet_level']}] {clean(item['tier'])} {clean(item['type'])}"
    reforge = "" if "reforge" not in item else clean(item['reforge'])+" "
    value = f"{reforge}{name} ➜ {hf(total)}"
    return value

def generate_page(command_author, data, username, page):

    embed = discord.Embed(colour=0x3498DB)

    # MAIN MENU
    if page == "main":
        total = hf(sum([int(x["total"]) for x in data.values()]))

        purse = float(data['purse']['total'])
        bank = float(data['banking']['total'])
        embed.add_field(name="**Purse**", value=f"{hf(purse)}", inline=True)
        embed.add_field(name="**Bank**", value=f"{hf(bank)}", inline=True)
        embed.add_field(name="**Combined**", value=f"{hf(purse+bank)}", inline=True)
        
        for page_string in page_names[1:-1]:  # Remove purse and banking
            if data[page_string]["total"] == "0":
                continue
            page_total = data[page_string]["total"]
            top_x = data[page_string]["prices"]
            
            value = [format_info(x['total'], x['item'], x['value']) for x in top_x]
            embed.add_field(name=f"**{PAGE_TO_EMOJI[page_string]} {clean(page_string)} ➜ {hf(data[page_string]['total'])}:**", value="\n".join(value), inline=False)

    # MISC
    elif page == "misc":
        embed.set_author(icon_url=PAGE_TO_IMAGE[page], name=f"Networth Command Limitations")
        embed.add_field(name="**1**: The value doesn't include minions", value="As minions aren't part of the API, they're not visible to the bot, so aren't included. However, these scale linearly (when compared to total network), and shouldn't make too much of a difference (relative wise).", inline=False)
        embed.add_field(name="**2**: The value doesn't include chests", value="Similarly, chests also aren't visible, and also aren't included, and while this is partially problematic, is impossible to add at the current time. The effect this has should be relatively minor.", inline=False)
        embed.add_field(name="**3**: Some values are subjective", value="While almost all items calculated have set prices (mostly from the auction house's BIN), two different constants have been used.\nThese values are: The value of Pet levels (e.g. Level 2 pet being worth more than a Level 1 pet), currently 0.2*xp (capped at Level 100), and the cost of essence, however this is pretty stable and accurate, so these should be a mostly minor issue.", inline=False)  
    # All the rest
    else:
        total = hf(data[page]["total"])
        top_x = data[page]["prices"]

        if top_x == []:  # For disabled APIs or empty containers
            total = ""
            embed.add_field(name=f"{username} doesn't have any items here.", value="Perhaps they disabled their API?", inline=False) ####################
        
        for price_object in top_x:
            item = price_object["item"]
            value = generate_description(price_object["value"], item)
            
            if "candyUsed" in item: # For pets only
                embed.add_field(name=f"Level {price_object['value']['pet_level']} {clean(item['type'])} ➜ {hf(price_object['total'])}", value=value, inline=False)
            else:
                name = f"{clean(item.get('reforge', ''))} {item['name']}"
                embed.add_field(name=f"{name} ➜ {hf(price_object['total'])}", value=value, inline=False)

    if page != "misc":
        ####################
        embed.set_author(icon_url=PAGE_TO_IMAGE[page], name=f"{username}'s {clean(page)} Networth - {total}", url=f"https://api.hypixelskyblock.de/api/v1/cb/display/{username}")

    embed.set_thumbnail(url=f"https://cravatar.eu/helmhead/{username}") ####################
    embed.set_footer(text=f" Command executed by {command_author.display_name} | Community Bot. By the community, for the community.")    
    return embed

