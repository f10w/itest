import asyncio
import platform
import sys
from colorama import Fore, Style

HOSTS = [
    ("1.1.1.1", False),
    ("8.8.8.8", False),
    ("google.com", True),
    ("ya.ru", True),
]

async def run_command(command):
    """Запускает команду в subprocess и возвращает её вывод"""
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode().strip(), stderr.decode().strip()

async def check_host(host, needs_dns):
    """Проверяет доступность узла с помощью ping и traceroute"""
    system = platform.system().lower()
    ping_cmd = "ping -c 3" if system in ("linux", "darwin") else "ping -n 3"
    trace_cmd = "traceroute" if system in ("linux", "darwin") else "tracert"

    ping_result, _ = await run_command(f"{ping_cmd} {host}")
    trace_result, _ = await run_command(f"{trace_cmd} {host}")

    color = Fore.LIGHTWHITE_EX if not needs_dns else Fore.WHITE
    print(f"{color}=== Проверка {host} ==={Style.RESET_ALL}")
    print(f"{color}{ping_result}{Style.RESET_ALL}")
    print(f"{color}{trace_result}{Style.RESET_ALL}")

async def main():
    """Запускает проверку всех узлов параллельно"""
    tasks = [check_host(host, needs_dns) for host, needs_dns in HOSTS]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
