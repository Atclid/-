package com.yourmod.bonsaitree;

import com.yourmod.bonsaitree.init.ModBlocks;
import com.yourmod.bonsaitree.init.ModItems;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;

@Mod(BonsaiMod.MOD_ID)
public class BonsaiMod {
    public static final String MOD_ID = "bonsaitree";

    public BonsaiMod() {
        IEventBus modEventBus = FMLJavaModLoadingContext.get().getModEventBus();
        
        // 注册物品和方块
        ModItems.ITEMS.register(modEventBus);
        ModBlocks.BLOCKS.register(modEventBus);
    }
}
