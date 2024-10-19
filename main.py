import discord
import psutil
import asyncio

TOKEN = ""
CHANNEL_ID = ""
THRESHOLD_PACKETS = 1000
CPU_THRESHOLD = 80
MEMORY_THRESHOLD = 90

intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def monitor_network():
    was_under_attack = False

    while True:
        net_io = psutil.net_io_counters()
        packets_sent = net_io.packets_sent
        packets_recv = net_io.packets_recv
        await asyncio.sleep(1)
        
        net_io_new = psutil.net_io_counters()
        new_packets_sent = net_io_new.packets_sent
        new_packets_recv = net_io_new.packets_recv

        packets_per_second_sent = new_packets_sent - packets_sent
        packets_per_second_recv = new_packets_recv - packets_recv
        total_packets_per_second = packets_per_second_sent + packets_per_second_recv

        cpu_percent = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        memory_percent = memory_info.percent

        is_under_attack = (
            total_packets_per_second > THRESHOLD_PACKETS or
            cpu_percent > CPU_THRESHOLD or
            memory_percent > MEMORY_THRESHOLD
        )

        if is_under_attack and not was_under_attack:
            was_under_attack = True
            channel = client.get_channel(CHANNEL_ID)
            await channel.send('⚠Обнаружена DDOS атака на сервере!')
        
        elif not is_under_attack and was_under_attack:
            was_under_attack = False
            channel = client.get_channel(CHANNEL_ID)
            await channel.send('✅DDOS атака прекращена!')

@client.event
async def on_ready():
    print(f'Бот {client.user} подключен и готов к работе!')
    client.loop.create_task(monitor_network())

client.run(TOKEN)
    