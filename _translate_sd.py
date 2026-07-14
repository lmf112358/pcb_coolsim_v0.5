# -*- coding: utf-8 -*-
# SD 文档英译中：围栏代码块保护 + 词条替换。
# 边界用 (?<![A-Za-z]) ... (?![A-Za-z])：防止词内误替(Objective->目标s)，且允许 | > # 后匹配。
# 长短语优先替换；输出统一 CRLF。
import re

BT = chr(0x60) * 3
FENCE = re.compile(BT + r'(.*?)' + BT, re.DOTALL)

FILES = [
    r"E:\My_program\pcb_coolsim_v0.5\06-测试文档\测试策略.md",
    r"E:\My_program\pcb_coolsim_v0.5\06-测试文档\测试计划.md",
    r"E:\My_program\pcb_coolsim_v0.5\07-质量保障\质量门禁.md",
    r"E:\My_program\pcb_coolsim_v0.5\07-质量保障\文档交互规范.md",
]

REPL = []
with open(r"E:\My_program\pcb_coolsim_v0.5\_repl.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        if not line or "|||" not in line:
            continue
        eng, zh = line.split("|||", 1)
        eng = eng.strip()
        zh = zh.strip()
        if eng:
            REPL.append((eng, zh))

COMPILED = []
for eng, zh in REPL:
    pat = r"(?<![A-Za-z])" + re.escape(eng) + r"(?![A-Za-z])"
    COMPILED.append((re.compile(pat), zh))
COMPILED.sort(key=lambda kv: len(kv[0].pattern), reverse=True)

def translate_text(text):
    parts = FENCE.split(text)
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            out.append(part)
            continue
        for rx, zh in COMPILED:
            part = rx.sub(zh, part)
        out.append(part)
    return "".join(out)

for f in FILES:
    raw = open(f, "rb").read().decode("utf-8")
    norm = raw.replace("\r\n", "\n").replace("\r", "\n")
    trans = translate_text(norm)
    open(f, "wb").write(trans.replace("\n", "\r\n").encode("utf-8"))
    print("WROTE:", f)
