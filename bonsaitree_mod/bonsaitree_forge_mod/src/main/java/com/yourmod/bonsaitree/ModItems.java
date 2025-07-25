package com.yourmod.bonsaitree.init;

import com.yourmod.bonsaitree.BonsaiMod;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModItems {
    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, BonsaiMod.MOD_ID);

    // 方块物品
    public static final RegistryObject<Item> BONSAI_TREE = ITEMS.register("bonsai_tree",
            () -> new BlockItem(ModBlocks.BONSAI_TREE.get(), new Item.Properties()));

    // 种子物品
    public static final RegistryObject<Item> BONSAI_SEEDS = ITEMS.register("bonsai_seeds",
            () -> new BlockItem(ModBlocks.BONSAI_CROP.get(), new Item.Properties()));
}
