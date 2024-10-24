import base64
import json
import os
import random
from mirai import Image, MessageChain, Plain
from pkg.config.manager import ConfigManager
from pkg.plugin.context import EventContext

async def send_image_message_situational(launcher_id: int, response_fixed: str, ctx: EventContext, meme_rate: float, meme_list: list, meme_with_text: bool):
    ## launcher_id可能用来读取个性化配置
    if should_send_image(meme_rate):
        if await send_image_message(meme_list, launcher_id, response_fixed, ctx):
            if meme_with_text == "True" and should_send_image(meme_rate):
                await ctx.event.query.adapter.reply_message(ctx.event.query.message_event, MessageChain([f"{response_fixed}"]), False)
        else:
            await ctx.event.query.adapter.reply_message(ctx.event.query.message_event, MessageChain([f"{response_fixed}"]), False)
    else:
        await ctx.event.query.adapter.reply_message(ctx.event.query.message_event, MessageChain([f"{response_fixed}"]), False)

def should_send_image(probability):
    """根据设定的概率决定是否发送图片消息"""
    return random.random() < probability

async def send_image_message(meme_list: list, launcher_id: int, response_fixed: str, ctx: EventContext):
    target_type = str(ctx.event.query.launcher_type).split('.')[-1].lower()
    sender_id = ctx.event.sender_id
    group_id = ctx.event.launcher_id
    
    image_path = await random_get_image_path(meme_list, launcher_id, response_fixed)
    try:
        if image_path:
            # 读取图片并进行 base64 编码
            with open(image_path, "rb") as f:
                base64_image = base64.b64encode(f.read()).decode()
            # 创建 Image 对象
            image_message = Image(base64=base64_image)
            if target_type == "person":
                receiver_id = sender_id
            elif target_type == "group":
                receiver_id = group_id        
            # 发送图片消息
            await ctx.send_message(target_type, receiver_id, [image_message])
            return True
    except Exception as e:
        print(f"Error occurred while sending image message: {str(e)}")
        return False
        
async def random_get_image_path(meme_list: list, launcher_id: int, response_fixed: str):
    # 生成一个在 1 到 25 之间的随机整数
    meme_max_idx = len(meme_list) - 1
    random_integer = random.randint(0, meme_max_idx)

    # 返回图片路径
    if meme_list[random_integer]:
        if meme_list[random_integer]['FUrl']:
            temp_image_path = meme_list[random_integer]['FUrl']
        else:
            temp_image_path = meme_list[random_integer]
    else:
        temp_image_path = "data/plugins/Waifu/temp/XiaoBao/XiaoBao_Curious_好奇.gif"
    return temp_image_path