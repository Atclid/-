package com.yourmod.bonsaitree.init;

import com.yourmod.bonsaitree.BonsaiCropBlock;
import com.yourmod.bonsaitree.BonsaiTreeBlock;
import com.yourmod.bonsaitree.BonsaiMod;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModBlocks {
    public static final DeferredRegister<Block> BLOCKS =
            DeferredRegister.create(ForgeRegistries.BLOCKS, BonsaiMod.MOD_ID);

    public static final RegistryObject<Block> BONSAI_TREE = BLOCKS.register("bonsai_tree",
            () -> new BonsaiTreeBlock(BlockBehaviour.Properties.of(Material.WOOD)
                    .strength(2.0F).sound(SoundType.WOOD)));

    public static final RegistryObject<Block> BONSAI_CROP = BLOCKS.register("bonsai_crop",
            () -> new BonsaiCropBlock(BlockBehaviour.Properties.of(Material.PLANT)
                    .noCollission().randomTicks().instabreak().sound(SoundType.CROP)));
}
