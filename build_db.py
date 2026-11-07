#!/usr/bin/env python3
"""words.txt -> data.json. Dùng: python build_db.py [words.txt] [data.json]"""
import json, sys

# id: (type p|s, từ loại tạo ra ("=" = giữ nguyên), nghĩa VI, nghĩa EN)
AFF = {
 "un-": ("p","=","không; ngược lại","not; opposite of"),
 "re-": ("p","=","lại; làm lại","again"),
 "dis-": ("p","=","không; ngược lại; tách ra","not; opposite; apart"),
 "mis-": ("p","=","sai; nhầm","wrongly"),
 "in-": ("p","=","không","not"),
 "im-": ("p","=","không","not (before m/p)"),
 "il-": ("p","=","không","not (before l)"),
 "ir-": ("p","=","không","not (before r)"),
 "over-": ("p","=","quá mức; vượt","too much; above"),
 "under-": ("p","=","dưới; thiếu; chưa đủ","below; not enough"),
 "out-": ("p","=","hơn; vượt","exceeding"),
 "anti-": ("p","=","chống lại","against"),
 "inter-": ("p","=","giữa; liên","between"),
 "non-": ("p","=","không","not"),
 "en-": ("p","v","làm cho; đưa vào","make; put into"),
 "-er": ("s","n","người/vật thực hiện hành động","one who does"),
 "-or": ("s","n","người/vật thực hiện hành động","one who does"),
 "-ist": ("s","n","người làm nghề / theo chủ nghĩa","person who practises"),
 "-ee": ("s","n","người nhận / chịu hành động","one who receives"),
 "-ment": ("s","n","hành động; kết quả","action; result"),
 "-ion": ("s","n","hành động; trạng thái; kết quả","action; state; result"),
 "-tion": ("s","n","hành động; trạng thái; kết quả","action; state; result"),
 "-ation": ("s","n","hành động; trạng thái; kết quả","action; state; result"),
 "-sion": ("s","n","hành động; trạng thái; kết quả","action; state; result"),
 "-ition": ("s","n","hành động; trạng thái; kết quả","action; state; result"),
 "-ness": ("s","n","trạng thái; tính chất","state; quality"),
 "-ity": ("s","n","tính chất; trạng thái","quality; state"),
 "-ty": ("s","n","tính chất; trạng thái","quality; state"),
 "-ance": ("s","n","hành động; trạng thái","action; state"),
 "-ence": ("s","n","hành động; trạng thái","action; state"),
 "-ship": ("s","n","trạng thái; mối quan hệ; kỹ năng","state; relationship; skill"),
 "-hood": ("s","n","giai đoạn; trạng thái; cộng đồng","period; state; community"),
 "-dom": ("s","n","trạng thái; lĩnh vực","state; domain"),
 "-th": ("s","n","trạng thái; mức độ","state; degree"),
 "-ure": ("s","n","hành động; kết quả","action; result"),
 "-age": ("s","n","tập hợp; mức độ; hành động","collection; amount; action"),
 "-able": ("s","adj","có thể được","able to be"),
 "-ible": ("s","adj","có thể được","able to be"),
 "-ful": ("s","adj","đầy; có","full of"),
 "-less": ("s","adj","không có","without"),
 "-ive": ("s","adj","có xu hướng; có tính","tending to"),
 "-al": ("s","adj","thuộc về; liên quan đến","relating to"),
 "-ous": ("s","adj","có tính chất; đầy","full of; having"),
 "-ic": ("s","adj","thuộc về; có tính","relating to"),
 "-ish": ("s","adj","hơi; giống như","somewhat; like"),
 "-y": ("s","adj","có; đầy; giống","having; full of"),
 "-ly": ("s","adv","một cách","in a ... way"),
 "-en": ("s","v","làm cho; trở nên","make; become"),
 "-ize": ("s","v","làm cho; biến thành","make; turn into"),
 "-ify": ("s","v","làm cho; trở nên","make; become"),
 "-ed": ("s","adj","bị/được; cảm thấy (tính từ từ quá khứ phân từ)","affected by; feeling"),
 "-ing": ("s","adj","gây ra cảm giác; đang (tính từ từ V-ing)","causing; ongoing"),
 "-ent": ("s","adj","có tính; ở trạng thái","having the quality of"),
}

def stems(r):
    """(rank, stem): rank nhỏ = ít biến đổi gốc hơn"""
    out = [(0, r), (1, r[:-1]), (1, r + r[-1])]
    if r.endswith("y"): out.append((1, r[:-1] + "i"))
    if r.endswith("le"): out.append((1, r[:-2]))
    return out

def infer(base, res):
    best = {}
    for a, (t, *_r) in AFF.items():
        if t == "p":
            if res == a[:-1] + base: best[a] = 0
        else:
            for rk, st in stems(base):
                if st + a[1:] == res: best[a] = min(best.get(a, 9), rk)
    if not best: return []
    m = min(best.values())
    c = [a for a, rk in best.items() if rk == m]
    if len(c) > 1:
        L = max(len(a) for a in c)
        c = [a for a in c if len(a) == L]
    return c

src = sys.argv[1] if len(sys.argv) > 1 else "words.txt"
dst = sys.argv[2] if len(sys.argv) > 2 else "data.json"
W, roots, raw, errs = {}, [], {}, []

for n, line in enumerate(open(src, encoding="utf-8").read().splitlines(), 1):
    line = line.strip()
    if not line or line.startswith("#"): continue
    f = line.split("|") + [""] * 5
    w, pos, vi, ders, note = [x.strip() for x in f[:5]]
    is_root = w.startswith("*")
    w = w.lstrip("*")
    if w in W: errs.append(f"L{n}: trùng '{w}'"); continue
    W[w] = {"p": pos, "vi": vi}
    if note: W[w]["n"] = note
    if is_root: roots.append(w)
    raw[w] = ders.split()

parent = {}
for base, items in raw.items():
    d = {}
    for it in items:
        res, _, aff = it.partition("=")
        if res not in W: errs.append(f"{base}: '{res}' chưa có dòng định nghĩa"); continue
        if aff:
            if aff not in AFF: errs.append(f"{base}: affix lạ '{aff}'"); continue
        else:
            c = infer(base, res)
            if len(c) != 1: errs.append(f"{base} -> {res}: ứng viên affix = {c}"); continue
            aff = c[0]
        if aff in d: errs.append(f"{base}: trùng affix {aff}"); continue
        d[aff] = res
        parent.setdefault(res, (base, aff))
    if d: W[base]["d"] = d

def pos_of(w, depth=0):
    if W[w]["p"]: return W[w]["p"]
    if w not in parent or depth > 8:
        errs.append(f"{w}: không xác định được từ loại"); return "?"
    b, a = parent[w]
    prod = AFF[a][1]
    W[w]["p"] = pos_of(b, depth + 1) if prod == "=" else prod
    return W[w]["p"]

for w in list(W): pos_of(w)

orph = [w for w in W if w not in roots and w not in parent]
used = {a for v in W.values() for a in v.get("d", {})}
for o in orph: errs.append(f"mồ côi (không root nào dẫn tới): {o}")

if errs:
    print("\n".join(errs)); print(f"\n{len(errs)} lỗi"); sys.exit(1)

out = {"affixes": {a: {"t": AFF[a][0], "vi": AFF[a][2], "en": AFF[a][3]} for a in AFF if a in used},
       "roots": roots, "words": W}
json.dump(out, open(dst, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
nd = sum(len(v.get("d", {})) for v in W.values())
print(f"OK: {len(roots)} root, {len(W)} từ, {nd} phép ghép, {len(used)} affix")
print("affix không dùng:", sorted(set(AFF) - used))
