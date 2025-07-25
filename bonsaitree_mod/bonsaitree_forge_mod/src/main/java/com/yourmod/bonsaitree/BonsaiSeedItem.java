package com.yourmod.bonsaitree;

import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.ItemNameBlockItem;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;

public class BonsaiSeedItem extends ItemNameBlockItem {
    public BonsaiSeedItem(Block block, Properties properties) {
        super(block, properties);
    }

    @Override
    public InteractionResult useOn(UseOnContext context) {
        // 只能在耕地上种植
        if (context.getLevel().getBlockState(context.getClickedPos()).is(Blocks.FARMLAND)) {
            return super.useOn(context);
        }
        return InteractionResult.FAIL;
    }
}
