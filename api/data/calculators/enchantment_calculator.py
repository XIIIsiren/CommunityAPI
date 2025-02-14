from data.constants.jerry_price_list import PRICES
from data.constants.bazaar import BAZAAR
from data.constants.lowest_bin import LOWEST_BIN
from data.constants.enchants_top import ENCHANTS_TOP
from data.constants.enchantment_levels import ENCHANTMENT_LEVELS

ROMAN_NUMERALS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]

def calculate_enchanted_book(price):  # For enchanted books

    element = price.item

    if "Anvil" in element.description_clean[0]:
        return price
    
    rarity = element.description_clean[-1]
    first_line_of_desc = element.description_clean[0].split(" ")
    enchantment_type = " ".join(first_line_of_desc[:-1]).replace(" ", "_").upper()
    numeral_enchantment_level = first_line_of_desc[-1]

    enchantment_level = ROMAN_NUMERALS.index(numeral_enchantment_level)+1
    
    if f"{enchantment_type};{enchantment_level}" in LOWEST_BIN:
        #print("Enchanted book was found on LOWEST_BIN")
        price.value["price_source"] = "BIN"
        price.value["enchantments_value"] = LOWEST_BIN[f"{enchantment_type};{enchantment_level}"]
    else:
        #print("Enchanted book will be tried on Jerry's price list")
        price.value["price_source"] = "Jerry"
        price.value["enchantments_value"] = PRICES.get(f"{enchantment_type.lower()}_{enchantment_level}", 0)

    return price

def calculate_enchantments(price):  # For enchantments on items

    price.value["enchantments"] = {}

    #print("Calculating item enchantments")
    for enchantment, level in price.item.enchantments.items():
        level = min(level, 10)  # cap at 10 for admin items so they don't cost Septillions
        # Special case for Svavenger, a mob drop that costs 15m otherwise and would make dungeon gear broken
        if enchantment == "scavenger" and level == 5 and price.item.origin_tag == "UNKNOWN":
            # If they're dropped from regular dungeon mobs, it's "UNKNOWN", else it's like QUICK_CRAFT
            price.value["enchantments"][f"{enchantment}_{level}"] = 50_000
            continue
        # Special case for enchants obtained through doing tasks such as breaking crops
        if enchantment in ENCHANTS_TOP and ENCHANTS_TOP[enchantment] > 5:
            price.value["enchantments"][f"{enchantment}_{level}"] = LOWEST_BIN.get(f"{enchantment.upper()};{1}", 0)
            continue
        # Special case for enchantments that can be got through the enchanting table
        if enchantment in ENCHANTMENT_LEVELS and level <= len(ENCHANTMENT_LEVELS[enchantment]):
            # If it's one that might be got from the etable, and it's on the list
            price.value["enchantments"][f"{enchantment}_{level}"]= BAZAAR.get("GRAND_EXP_BOTTLE", 0)
            continue
        
        for i in range(level, 0, -1):
            if f"{enchantment.upper()};{i}" in LOWEST_BIN:
                break
        else:
            price.value["enchantments"][f"{enchantment}_{level}"] = 0
            continue  # No break, when we can't find any of that enchantment whatsoever.
        # If we can't find Sharpness 5, we try Sharpness 4
        # If the starting level is level 4, and we've found a level 2 book, we need 2**2 (4-2) books
        price.value["enchantments"][f"{enchantment}_{level}"] = LOWEST_BIN.get(f"{enchantment.upper()};{i}", 0)*(2**(level-i))
        
    return price       
