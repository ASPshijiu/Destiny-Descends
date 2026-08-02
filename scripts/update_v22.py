# -*- coding: utf-8 -*-
"""天命降临 v22：将领特质本地化（拼音 token → 中文名 + 英文名）"""
import json, os, sys, urllib.request, urllib.error
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = os.environ["HOI4_PLATFORM_URL"].rstrip("/")
TOKEN = os.environ["HOI4_PLATFORM_TOKEN"]
PID = 2008

def call(m, p, body=None):
    d = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    r = urllib.request.Request(BASE + p, data=d, method=m)
    r.add_header("Content-Type", "application/json; charset=utf-8")
    r.add_header("Authorization", "Bearer " + TOKEN)
    r.add_header("User-Agent", "x")
    try:
        x = urllib.request.urlopen(r, timeout=90)
        s = x.read().decode("utf-8", "replace")
        return x.status, (json.loads(s) if s else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")

# token -> (中文名, 英文名, 中文描述)
TRAITS = {
    "bu_bing": ("步兵", "Infantry Commander", "指挥步兵部队时获得攻击与组织度加成。"),
    "zhuang_jia": ("装甲", "Armored Commander", "指挥装甲部队时获得速度与攻击加成。"),
    "ji_dong": ("机动", "Mobile Warfare", "骑兵、摩托化与机械化部队攻击与突破提升。"),
    "deng_lu": ("登陆", "Amphibious Assault", "两栖登陆能力提升，登陆准备时间缩短。"),
    "lianbingdashi": ("练兵大师", "Drill Master", "部队经验获取增加，经验损失减少。"),
    "jixianfeng": ("急先锋", "Vanguard", "部队移动损耗减少，速度与计划速度提升。"),
    "jianrenbuba": ("坚韧不拔", "Unyielding", "部队强度提升，补给消耗减少。"),
    "huopaozhiyuan": ("火炮支援", "Artillery Support", "炮兵部队攻击与防御提升。"),
    "kongdiyite": ("空地一体", "Ground-Air Coordination", "拥有空中优势时陆军加成提升，侦察效率提高。"),
    "tezhongjinying": ("特种精英", "Special Forces Elite", "特种部队攻击防御提升，地形惩罚减少。"),
    "congxingl": ("从容撤退", "Composed Retreat", "海军与护航部队撤退几率与速度优化。"),
    "dapaojujianl": ("大炮巨舰", "Big Gun Fleet", "主力舰攻击防御与防空能力提升。"),
    "hangkongmujianl": ("航空母舰", "Carrier Commander", "舰载机打击与出击效率提升。"),
    "pingweijianhail": ("屏卫舰海", "Screen Fleet", "防空与索敌能力提升，鱼雷反制增强。"),
    "shenhailimaol": ("深海利矛", "Deep Sea Spear", "鱼雷命中与穿透提升。"),
}

def build(lang, key):
    lines = [f"l_{key}:"]
    for tok, (nz, ne, dz) in TRAITS.items():
        name = nz if lang == "zh" else ne
        lines.append(f" {tok}: \"{name}\"")
        lines.append(f" {tok}_desc: \"{dz if lang == 'zh' else ne + ' trait.'}\"")
    return "\n".join(lines) + "\n"

loc_zh = build("zh", "simp_chinese")
loc_en = build("en", "english")

for dest, content in [("localisation/simp_chinese/qin_traits_l_simp_chinese.yml", loc_zh),
                      ("localisation/english/qin_traits_l_english.yml", loc_en)]:
    _, b = call("GET", f"/api/projects/{PID}/raw-files")
    old = None
    if isinstance(b, list):
        for f in b:
            if f.get("dest_path") == dest:
                old = f.get("id")
    if old:
        call("DELETE", f"/api/projects/{PID}/raw-files/{old}")
    s, b = call("POST", f"/api/projects/{PID}/raw-files", {"dest_path": dest, "content": content})
    print(f"upload {dest} ->", s, (str(b)[:120] if s >= 300 else ""))

# 校验
s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
print("\nexport/validate ->", s)
if isinstance(b, dict):
    for it in b.get("issues", []):
        if it.get("severity") == "blocker":
            print("  blocker:", it.get("code"), str(it.get("message"))[:160])

# 导出安装
import zipfile, shutil, io
r = urllib.request.Request(BASE + f"/api/projects/{PID}/export/download")
r.add_header("Authorization", "Bearer " + TOKEN); r.add_header("User-Agent", "x")
data = urllib.request.urlopen(r, timeout=120).read()
MODDIR = r"C:\Users\xw130\Documents\Paradox Interactive\Hearts of Iron IV\mod"
z = zipfile.ZipFile(io.BytesIO(data)); names = z.namelist()
mod_folder = [n.split("/")[0] for n in names if "/" in n][0]
mod_file = [n for n in names if n.endswith(".mod")][0]
tmp = r"C:\Users\xw130\Desktop\hoi4\_tm_install"
z.extractall(tmp)
shutil.copy(os.path.join(tmp, mod_file), MODDIR)
dst = os.path.join(MODDIR, mod_folder)
if os.path.isdir(dst): shutil.rmtree(dst)
shutil.copytree(os.path.join(tmp, mod_folder), dst)
shutil.rmtree(tmp)
print("installed", mod_folder, "| bytes:", len(data))
# 验证 loc
p = os.path.join(MODDIR, mod_folder, "localisation", "simp_chinese", "qin_traits_l_simp_chinese.yml")
print(open(p, encoding="utf-8-sig").read()[:300])
