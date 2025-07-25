package com.yourmod.bonsaitree;

import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModBlocks {
    public static final DeferredRegister<Block> BLOCKS = 
        DeferredRegister.create(ForgeRegistries.BLOCKS, Bonsaitree.MOD_ID);
    
    // 盆景作物
    public static final RegistryObject<Block> BONSAI_CROP = BLOCKS.register("bonsai_crop", 
        () -> new BonsaiCropBlock(BlockBehaviour.Properties.copy(Blocks.WHEAT)
            .noCollission()
            .randomTicks()
            .instabreak()
            .sound(SoundType.CROP)));
            
    // 盆景树
    public static final RegistryObject<Block> BONSAI_TREE = BLOCKS.register("bonsai_tree", 
        () -> new BonsaiTreeBlock(BlockBehaviour.Properties.copy(Blocks.OAK_SAPLING)
            .strength(0.5f)
            .sound(SoundType.GRASS)
            .noOcclusion()));
}
