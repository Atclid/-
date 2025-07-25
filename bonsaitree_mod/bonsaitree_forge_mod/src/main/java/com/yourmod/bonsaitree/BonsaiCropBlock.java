package com.yourmod.bonsaitree;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.CropBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.IntegerProperty;

public class BonsaiCropBlock extends CropBlock {
    public static final int MAX_AGE = 3; // 4个生长阶段（0-3）
    public static final IntegerProperty AGE = IntegerProperty.create("age", 0, MAX_AGE);
    
    public BonsaiCropBlock(Properties properties) {
        super(properties);
    }
    
    @Override
    public IntegerProperty getAgeProperty() {
        return AGE;
    }

    @Override
    public int getMaxAge() {
        return MAX_AGE;
    }
    
    @Override
    public void createBlockStateDefinition(StateDefinition.Builder<net.minecraft.world.level.block.Block, BlockState> builder) {
        builder.add(AGE);
    }
    
    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<net.minecraft.world.level.block.Block, BlockState> builder) {
        builder.add(AGE);
    }
    
    @Override
    public void entityInside(BlockState state, Level level, BlockPos pos, Entity entity) {
        // 防止生物踩踏
        if (entity instanceof LivingEntity && !(entity instanceof Player)) {
            level.destroyBlock(pos, true);
        }
    }

    @Override
    public void randomTick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        // 加速生长：比小麦快3倍
        if (level.getRawBrightness(pos, 0) >= 9) {
            int age = this.getAge(state);
            if (age < this.getMaxAge()) {
                if (random.nextInt(5) == 0) { // 20%几率生长
                    level.setBlock(pos, state.setValue(AGE, age + 1), 2);
                }
            } else {
                // 成熟后自动转化为盆景树
                level.setBlock(pos, ModBlocks.BONSAI_TREE.get().defaultBlockState(), 3);
            }
        }
    }
    
    @Override
    public boolean canSurvive(BlockState state, LevelReader level, BlockPos pos) {
        // 只能在耕地上生长
        return level.getBlockState(pos.below()).is(Blocks.FARMLAND);
    }
}
