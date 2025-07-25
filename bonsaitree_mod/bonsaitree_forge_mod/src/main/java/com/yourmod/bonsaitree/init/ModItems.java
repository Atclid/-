package com.yourmod.bonsaitree.init;

import com.yourmod.bonsaiTree.BonsaiMod;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModItems {
    // 物品注册器（绑定模组ID）
    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, BonsaiMod.MOD_ID);

    // 盆景树方块对应的物品（放置用）
    public static final RegistryObject<Item> BONSAI_TREE = ITEMS.register("bonsai_tree",
            () -> new BlockItem(ModBlocks.BONSAI_TREE.get(), new Item.Properties()));

    // 盆景种子物品（种植用）
    public static final RegistryObject<Item> BONSAI_SEEDS = ITEMS.register("bonsai_seeds",
            () -> new BlockItem(ModBlocks.BONSAI_CROP.get(), new Item.Properties()));
}
