package com.yourmod.bonsaitree;

import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.Item;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModItems {
    public static final DeferredRegister<Item> ITEMS = 
        DeferredRegister.create(ForgeRegistries.ITEMS, Bonsaitree.MOD_ID);
    
    // 盆景种子
    public static final RegistryObject<Item> BONSAI_SEEDS = ITEMS.register("bonsai_seeds", 
        () -> new BonsaiSeedItem(ModBlocks.BONSAI_CROP.get(), 
            new Item.Properties().food(
                new FoodProperties.Builder()
                    .nutrition(1)
                    .saturationMod(0.3f)
                    .build())));
}
