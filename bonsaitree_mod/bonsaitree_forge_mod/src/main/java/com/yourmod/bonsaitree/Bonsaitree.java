package com.yourmod.bonsaitree;

import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;

@Mod(Bonsaitree.MOD_ID)
public class Bonsaitree {
    public static final String MOD_ID = "bonsaitree";
    
    public Bonsaitree() {
        IEventBus bus = FMLJavaModLoadingContext.get().getModEventBus();
        
        // 注册方块和物品
        ModBlocks.BLOCKS.register(bus);
        ModItems.ITEMS.register(bus);
        
        MinecraftForge.EVENT_BUS.register(this);
    }
}
