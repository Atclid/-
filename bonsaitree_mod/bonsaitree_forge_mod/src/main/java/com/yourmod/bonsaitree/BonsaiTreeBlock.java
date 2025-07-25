package com.yourmod.bonsaitree;

import net.minecraft.core.BlockPos;
import net.minecraft.world.Containers;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;

public class BonsaiTreeBlock extends Block {
    public BonsaiTreeBlock(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        // 右键直接收获木头
        if (!level.isClientSide && hand == InteractionHand.MAIN_HAND) {
            harvestTree(level, pos, player);
            return InteractionResult.SUCCESS;
        }
        return super.use(state, level, pos, player, hand, hit);
    }

    private void harvestTree(Level level, BlockPos pos, Player player) {
        // 掉落2-4个橡木
        int count = 2 + level.random.nextInt(3);
        ItemStack wood = new ItemStack(Items.OAK_LOG, count);
        
        // 80%几率返还种子
        if (level.random.nextFloat() < 0.8f) {
            ItemStack seed = new ItemStack(ModItems.BONSAI_SEEDS.get(), 1);
            Containers.dropItemStack(level, pos.getX(), pos.getY(), pos.getZ(), seed);
        }
        
        Containers.dropItemStack(level, pos.getX(), pos.getY(), pos.getZ(), wood);
        level.setBlock(pos, Blocks.AIR.defaultBlockState(), 3);
        
        // 经验奖励
        player.giveExperiencePoints(1);
        
        // 消耗1点饥饿值
        if (player.getFoodData().getFoodLevel() > 2) {
            player.getFoodData().setFoodLevel(player.getFoodData().getFoodLevel() - 1);
        }
    }
}
