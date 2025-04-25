import asyncio
import os
import random
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SetTypingRequest
from telethon.tl.types import SendMessageTypingAction
from telethon.errors import FloodWaitError

# 加载环境变量
load_dotenv(dotenv_path='info.env')

MESSAGE_VARIANTS = [  # 消息模板池（至少准备5种变体）
    '''Modal akun WHATSAPP 
Sehari 30k hingga 1juta 
baru lagi nih mirip dengan GOSHARE
tugasnya cuma tautin akun whatsapp gak ribet langsung cuan tanpa syarat, langsung gas 

- TIDAK DIPERLUKAN DEPOSIT/ GRATISAN 
- 100% SUDAH TERBUKTI MEMBAYAR🤯

-  BISA WD HARIAN = Rp.30.000 hingga tidak terbatas 🤩 

Klik linknya disini :
https://rent.wsdev.xin#/?code=CU6k3RyAbixi

Link group / Bukti transfer :
https://t.me/RentraWhatsappOfficial
''',
    '''Hallo.. kak di sini saya ingin menawarkan pekerjaan partime hanya dengan modal akun WHATSAPP kk sudah bisa menghasikan Sehari 30k hingga 1juta  tugasnya cuma tautin akun whatsapp gak ribet langsung cuan tanpa syarat, langsung gas   - TIDAK DIPERLUKAN DEPOSIT/ GRATISAN  - 100% SUDAH TERBUKTI MEMBAYAR🤯 -  BISA WD HARIAN = Rp.30.000 hingga tidak terbatas 🤩  
Klik linknya disini :   https://rent.wsdev.xin#/?code=CU6k3RyAbixi
''',
 '''- TIDAK DIPERLUKAN DEPOSIT/ GRATISAN 
- 100% SUDAH TERBUKTI MEMBAYAR🤯

-  WD/Penarikan no ribet, gak pake alasan klasik seperti platform lain
- Banyak bonus lainnya, Platform baru... Bonus melimpah

JOINN LANGSUNG DI BAWAH INI ⬇️⬇️⬇️
Linknya ada disini  :
https://rent.wsdev.xin#/?code=CU6k3RyAbixi

Ini grup diskusi dan penarikannya :
https://t.me/RentraWhatsappOfficial/15
''',
    # 补充至少3个不同模板...
]

# 调整间隔参数
SEND_INTERVAL = (1.2, 3.5)  # 新消息间隔范围
CYCLE_INTERVAL = (120, 300)  # 新循环间隔范围

async def safe_send(client, group, message):
    try:
        # 精确控制发送间隔
        await asyncio.sleep(random.uniform(*SEND_INTERVAL))
        
        await client.send_message(
            entity=group,
            message=message,
            schedule=random.randint(10, 300)
        )
        return True
    except FloodWaitError as e:
        print(f'⚠️ 触发流控，等待 {e.seconds} 秒')
        await asyncio.sleep(e.seconds + 10)
    except Exception as e:
        print(f'❌ 发送失败: {str(e)[:50]}')
    return False

async def send_to_groups():
    # 移除代理配置
    client = TelegramClient(
        'session_name', 
        int(os.getenv('API_ID')),
        os.getenv('API_HASH')
    )
    
    await client.start(os.getenv('PHONE'))
    
    dialogs = await client.get_dialogs()
    groups = [d.entity for d in dialogs if d.is_group]
    
    for index, group in enumerate(groups):
        if random.random() < 0:
            print(f'⏭ 随机跳过 {group.title}')
            continue
            
        msg_template = random.choice(MESSAGE_VARIANTS)
        success = await safe_send(client, group, msg_template)
        
        if success:
            print(f'✅ 成功发送至第{index+1}个群组：{group.title}')

    await client.disconnect()

async def main():
    while True:
        await send_to_groups()
        wait = random.uniform(*CYCLE_INTERVAL)
        print(f'⏳ 进入循环间隔：{wait:.1f}秒')
        await asyncio.sleep(wait)

if __name__ == '__main__':
    asyncio.run(main())