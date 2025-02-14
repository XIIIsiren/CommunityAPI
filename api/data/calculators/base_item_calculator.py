from data.constants.jerry_price_list import PRICES
from data.constants.lowest_bin import LOWEST_BIN
from data.constants.bazaar import BAZAAR
from data.constants.reforges import REFORGE_DICT

from data.calculators.dungeon_calculator import calculate_dungeon_item
from data.calculators.enchantment_calculator import calculate_enchantments


def calculate_reforge_price(price):
    item = price.item
    # This "+;item.item_group prevents warped for armor and AOTE breaking
    reforge_data = REFORGE_DICT.get(item.reforge+";"+item.item_group, None)
    # This will not calculate reforges that are from the blacksmith, e.g. "Wise", "Demonic", they're just not worth anything.
    if reforge_data is not None:
        reforge_item = reforge_data["INTERNAL_NAME"]  # Gets the item, e.g. BLESSED_FRUIT
        item_rarity = item.rarity
        if item_rarity in ["SPECIAL", "VERY_SPECIAL"]:  # The dataset doesn't include special, use LEGENDARY instead
            item_rarity = "LEGENDARY"
        #print("All data:", reforge_data, "\nInternal name:", item.internal_name)
        #print(reforge_data["REFORGE_COST"], item_rarity)
        reforge_cost = reforge_data["REFORGE_COST"].get(item_rarity, 0)  # Cost to apply for each rarity
        reforge_item_cost = LOWEST_BIN.get(reforge_item, 0)  # How much does the reforge stone cost

        price.value["reforge"] = {}
        price.value["reforge"]["item"] = {reforge_item: reforge_item_cost}
        price.value["reforge"]["apply_cost"] = reforge_cost

    return price

def calculate_item(price, print_prices=False):

    item = price.item
    value = price.value

    converted_name = item.name.upper().replace("- ", "").replace(" ", "_").replace("✪", "").replace("'", "").rstrip("_") # The Jerry price list uses the item name, not the internal_id.
    
    if item.internal_name in BAZAAR:
        value["base_price"] = BAZAAR[item.internal_name]
        value["price_source"] = "Bazaar"
    elif item.internal_name in LOWEST_BIN:
        value["base_price"] = LOWEST_BIN[item.internal_name]
        value["price_source"] = "BIN"
    else:
        value["price_source"] = "Jerry"
        value["base_price"] = PRICES.get(converted_name, None) 
        if value["base_price"] is None:
            value["base_price"] = 0
            value["price_source"] = "None"
    #=============================================================================
    # Hoe calculations
    if item.type == "HOE" and item.hoe_material != None:
        value["base_price"] = 1_000_000+256*(BAZAAR[item.hoe_material]*(144**(item.hoe_level-1)))
        value["price_source"] = "Calculated"
    #=============================================================================
    # Hot potato books:
    if item.hot_potatoes > 0:
        value["hot_potatoes"] = {}
        if item.hot_potatoes <= 10:
            value["hot_potatoes"]["hot_potato_books"] = item.hot_potatoes*BAZAAR["HOT_POTATO_BOOK"]
        else:
            value["hot_potatoes"]["hot_potato_books"] = 10*BAZAAR["HOT_POTATO_BOOK"]
            value["hot_potatoes"]["fuming_potato_books"] = (item.hot_potatoes-10)*BAZAAR["FUMING_POTATO_BOOK"]
    # Recombobulation
    if item.recombobulated:
        value["recombobulator_value"] = BAZAAR["RECOMBOBULATOR_3000"]
    # Enchantments
    if item.enchantments:
        price = calculate_enchantments(price)
    # Reforge:
    if item.item_group is not None and item.reforge is not None:
        price = calculate_reforge_price(price)
    # Talisman enrichments
    if item.talisman_enrichment:
        value["talisman_enrichment"] = {item.talisman_enrichment: LOWEST_BIN.get("TALISMAN_ENRICHMENT_"+item.talisman_enrichment, 0)} 
    # Dungeon items/stars
    if item.star_upgrades:
        price = calculate_dungeon_item(price)
    # Art of war
    if item.art_of_war:
        value["art_of_war_value"] = LOWEST_BIN.get("THE_ART_OF_WAR", 0)  # Get's the art of war book from BIN
    # Wood singularty
    if item.wood_singularity:
        value["wood_singularty_value"] = LOWEST_BIN.get("WOOD_SINGULARITY", 0)
    # Armor skins
    if item.skin:
        value["skin"] = {}
        value["skin"][item.skin] = LOWEST_BIN.get(item.skin, 0)
    # Power ability scrolls:
    if item.power_ability_scroll:
        value["power_ability_scroll"] = {}
        value["power_ability_scroll"][item.power_ability_scroll] = LOWEST_BIN.get(item.power_ability_scroll, 0)
    # Gems
    if item.gems:
        value["gems"] = {}
        for gem, condition in item.gems.items():
            value["gems"][gem] = BAZAAR.get(f"{condition}_{gem.rstrip('_0')}_GEM", 0)
    # Gemstone chambers
    if item.gemstone_chambers:
        value["gemstone_chambers"] = item.gemstone_chambers*LOWEST_BIN.get("GEMSTONE_CHAMBER", 0)
    # Farming for dummies books on hoes
    if item.farming_for_dummies:
        value["farming_for_dummies_bonus"] = item.farming_for_dummies*LOWEST_BIN.get("FARMING_FOR_DUMMIES", 0)
    # Drills (upgrades)
    if item.type == "DRILL" and item.has_drill_upgrade:
        value["drill_upgrades"] = {}
        if item.drill_module_upgrade:
            value["drill_upgrades"][item.drill_module_upgrade] = LOWEST_BIN.get(item.drill_module_upgrade, 0)
        if item.drill_engine_upgrade:
            value["drill_upgrades"][item.drill_engine_upgrade] = LOWEST_BIN.get(item.drill_engine_upgrade, 0)
        if item.drill_tank_upgrade:
            value["drill_upgrades"][item.drill_tank_upgrade] = LOWEST_BIN.get(item.drill_tank_upgrade, 0)
    # Tuned transmission:
    if item.tuned_transmission:
        value["tuned_transmission"] = item.tuned_transmission*LOWEST_BIN.get("TRANSMISSION_TUNER", 0)
    # Ethermerge
    if item.ethermerge:
        value["ethermerge"] = LOWEST_BIN.get("ETHERWARP_MERGER", 0)+LOWEST_BIN.get("ETHERWARP_CONDUIT", 0)
    # Winning bid for Midas Staff/Sword
    if item.winning_bid > 0 and item.internal_name in ["MIDAS_STAFF", "MIDAS_SWORD"]:
        value["winning_bid"] = item.winning_bid
    # Hyperion scrolls
    if item.ability_scrolls:
        value["ability_scrolls_value"] = sum([LOWEST_BIN.get(scroll, 0) for scroll in item.ability_scrolls])
    #=================
    price.value = value
    return price
