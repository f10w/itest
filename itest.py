import asyncio
import platform
import sys
import os
import shutil

DEFAULT_HOSTS = [
    ("1.1.1.1", False),
    ("8.8.8.8", False),
    ("google.com", True),
    ("ya.ru", True),
]

HOSTS_FILE = "hosts"
MAX_HOPS = 10  # Ограничение количества узлов в traceroute

def load_hosts():
    """Загружает дополнительные хосты из файла, если он существует"""
    if not os.path.isfile(HOSTS_FILE):
        return []
    
    hosts = []
    with open(HOSTS_FILE, "r") as f:
        for line in f:
            host = line.strip()
            if host and not host.startswith("#"):
                needs_dns = not host.replace(".", "").isdigit()
                hosts.append((host, needs_dns))
    return hosts

async def run_command(command):
    """Запускает команду в subprocess и возвращает её вывод"""
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode().strip(), stderr.decode().strip()

async def check_host(host, needs_dns, index, total_hosts, results):
    """Проверяет доступность узла с помощью ping и traceroute"""
    system = platform.system().lower()
    ping_cmd = "ping -c 4" if system in ("linux", "darwin") else "ping -n 4"
    trace_cmd = f"traceroute -m {MAX_HOPS}" if system in ("linux", "darwin") else f"tracert -h {MAX_HOPS}"

    results[index] = f"[{index+1}/{total_hosts}] Проверка {host}..."
    print_display(results)

    ping_result, _ = await run_command(f"{ping_cmd} {host}")
    trace_result, _ = await run_command(f"{trace_cmd} {host}")

    results[index] = f"[{index+1}/{total_hosts}] {host} проверен\n{ping_result}\n{trace_result}"
    print_display(results)


def print_display(results):
    """Выводит результаты проверки в колонках"""
    terminal_width = shutil.get_terminal_size((80, 20)).columns
    columns = 4
    col_width = terminal_width // columns
    lines = max(len(res.split('\n')) for res in results)
    
    display = ["" for _ in range(lines)]
    
    for i, res in enumerate(results):
        res_lines = res.split("\n")
        for j in range(lines):
            line = res_lines[j] if j < len(res_lines) else ""
            display[j] += line.ljust(col_width)[:col_width] + " "
    
    print("\033c", end="")  # Очистка экрана
    for line in display:
        print(line)

async def main():
    """Запускает проверку всех узлов параллельно"""
    hosts = DEFAULT_HOSTS + load_hosts()
    total_hosts = len(hosts)
    results = ["" for _ in range(total_hosts)]
    tasks = [check_host(host, needs_dns, i, total_hosts, results) for i, (host, needs_dns) in enumerate(hosts)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
