PAGE_SIZE = 1024
ADDR_SPACE = 16 * 1024  # 16 КБ (16 страниц)

def load_page_table(filename: str) -> dict[int, int | None]:
    page_table = {}
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            page = int(parts[0])
            frame = None if parts[1] in ("-", "None", "absent") else int(parts[1])
            page_table[page] = frame
    return page_table

def translate(addr: int, page_table: dict[int, int | None]) -> str:
    if addr < 0 or addr >= ADDR_SPACE:
        return f"Адрес {addr}: Ошибка — выход за пределы адресного пространства (0..{ADDR_SPACE - 1})"
    
    page = addr // PAGE_SIZE
    offset = addr % PAGE_SIZE
    
    frame = page_table.get(page)
    if frame is None:
        return f"Адрес {addr} (стр. {page}, смещ. {offset}): ОШИБКА — страница отсутствует (Page Fault)"
    
    phys_addr = frame * PAGE_SIZE + offset
    return f"Адрес {addr} (стр. {page}, смещ. {offset}) -> кадр {frame} -> Физ. адрес: {phys_addr}"

if __name__ == "__main__":
    pt = load_page_table("pagetable.txt")
    with open("refs.txt", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                logical_addr = int(line.strip())
                print(translate(logical_addr, pt))
