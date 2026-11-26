"""统计会话里每个工具的花销占比。

用法：python tools/analyze_session.py <session.v4.jsonl.zstd>
"""

import collections
import json
import sys

import zstandard

path = sys.argv[1]
raw = zstandard.ZstdDecompressor().stream_reader(open(path, "rb")).read()
lines = raw.decode("utf-8", errors="replace").splitlines()

call_name = {}          # callId -> tool name
call_args = collections.Counter()
call_count = collections.Counter()
result_by_tool = collections.Counter()
result_count = collections.Counter()
kind_bytes = collections.Counter()

for L in lines:
    L = L.strip()
    if not L:
        continue
    try:
        r = json.loads(L)
    except Exception:
        continue
    t = r.get("type")
    data = r.get("data") or {}

    if t == "tool/call":
        msg = data.get("message") or {}
        cid = msg.get("toolCallId") or msg.get("id")
        name = msg.get("name") or (data.get("toolName"))
        if cid:
            call_name[cid] = name
        n = len(json.dumps(msg.get("arguments", {}), ensure_ascii=False))
        call_args[name] += n
        call_count[name] += 1
        kind_bytes["工具参数(我发的)"] += n

    elif t == "tool/result":
        msg = data.get("message") or {}
        cid = msg.get("toolCallId")
        name = call_name.get(cid, "?")
        n = len(json.dumps(msg.get("content", []), ensure_ascii=False))
        result_by_tool[name] += n
        result_count[name] += 1
        kind_bytes["工具结果(返回的)"] += n

    elif t == "assistant/message":
        msg = data.get("message") or {}
        content = msg.get("content")
        if isinstance(content, list):
            for c in content:
                if not isinstance(c, dict):
                    continue
                ct = c.get("type")
                n = len(json.dumps(c, ensure_ascii=False))
                if ct == "text":
                    kind_bytes["我的回复文本"] += n
                elif ct == "reasoning":
                    kind_bytes["我的思考"] += n
                elif ct == "tool-call":
                    pass  # 记在 tool/call 里
                else:
                    kind_bytes[f"assistant:{ct}"] += n

    elif t in ("system/message", "developer/message"):
        msg = data.get("message") or {}
        n = len(json.dumps(msg, ensure_ascii=False))
        kind_bytes["系统/开发者提示"] += n

    elif t == "user/message":
        msg = data.get("message") or {}
        n = len(json.dumps(msg, ensure_ascii=False))
        kind_bytes["用户输入"] += n

total = sum(kind_bytes.values()) or 1
print("=== 按类别 ===")
for k, v in kind_bytes.most_common():
    print(f"{k:24} {v:>12,} 字符  {100*v/total:5.1f}%")
print(f"{'合计':24} {total:>12,} 字符\n")

print("=== 工具结果 Top 12 ===")
for k, v in result_by_tool.most_common(12):
    print(f"{str(k):40} {v:>10,}  {result_count[k]:4} 次")

print("\n=== 工具参数 Top 12 ===")
for k, v in call_args.most_common(12):
    print(f"{str(k):40} {v:>10,}  {call_count[k]:4} 次")
