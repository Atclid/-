package com.yourmod.bonsaitree.init;

import com.yourmod.bonsaitree.BonsaiMod;  // 修正包名大小写（bonsaitree 全小写）
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModItems {
    // 物品注册器（绑定模组ID）
    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, BonsaiMod.MOD_ID);  // 现在能正确引用 BonsaiMod

    // 盆景树方块对应的物品
    public static final RegistryObject<Item> BONSAI_TREE = ITEMS.register("bonsai_tree",
            () -> new BlockItem(ModBlocks.BONSAI_TREE.get(), new Item.Properties()));

    // 盆景种子物品
    public static final RegistryObject<Item> BONSAI_SEEDS = ITEMS.register("bonsai_seeds",
            () -> new BlockItem(ModBlocks.BONSAI_CROP.get(), new Item.Properties()));
}
