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
    // 方块注册器（绑定模组ID）
    public static final DeferredRegister<Block> BLOCKS =
            DeferredRegister.create(ForgeRegistries.BLOCKS, BonsaiMod.MOD_ID);

    // 注册盆景树方块
    public static final RegistryObject<Block> BONSAI_TREE = BLOCKS.register("bonsai_tree",
            () -> new BonsaiTreeBlock(
                    BlockBehaviour.Properties.of()
                            .strength(2.0F)
                            .sound(SoundType.WOOD)
            )
    );

    // 注册盆景作物方块
    public static final RegistryObject<Block> BONSAI_CROP = BLOCKS.register("bonsai_crop",
            () -> new BonsaiCropBlock(
                    BlockBehaviour.Properties.of()
                            .noCollission()
                            .randomTicks()
                            .instabreak()
                            .sound(SoundType.CROP)
            )
    );
}
