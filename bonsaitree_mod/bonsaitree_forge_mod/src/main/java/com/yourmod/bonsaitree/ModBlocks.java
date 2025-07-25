package com.yourmod.bonsaitree;

import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModBlocks {
    // 方块注册器（模组 ID 为 "bonsaitree"，需与主类一致）
    public static final DeferredRegister<Block> BLOCKS =
            DeferredRegister.create(ForgeRegistries.BLOCKS, "bonsaitree");

    // 1. 注册 BonsaiTreeBlock（对应你的 BonsaiTreeBlock.java）
    public static final RegistryObject<Block> BONSAI_TREE = BLOCKS.register("bonsai_tree",
            () -> new BonsaiTreeBlock(
                    // 方块属性：木材特性（无 Material 依赖）
                    BlockBehaviour.Properties.of()
                            .strength(2.0F) // 硬度
                            .sound(SoundType.WOOD) // 声音
                            .requiresCorrectToolForDrops() // 可选：需要工具开采
            )
    );

    // 2. 注册 BonsaiCropBlock（对应你的 BonsaiCropBlock.java）
    public static final RegistryObject<Block> BONSAI_CROP = BLOCKS.register("bonsai_crop",
            () -> new BonsaiCropBlock(
                    // 方块属性：作物特性（无 Material 依赖）
                    BlockBehaviour.Properties.of()
                            .noCollission() // 无碰撞（作物特性）
                            .randomTicks() // 随机 ticks（生长需要）
                            .instabreak() // 可瞬间破坏
                            .sound(SoundType.CROP) // 作物声音
            )
    );
}
