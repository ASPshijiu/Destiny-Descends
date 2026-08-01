# -*- coding: utf-8 -*-
"""钢之工坊（hagane.works）平台 REST 客户端——所有构建脚本共享的样板。

用法（与脚本同目录，直接 import）：
    import api_client as A
    s, b = A.call("GET", f"/api/projects/{A.PID}/ideas")
    A.ensure_ok(s, b, "GET ideas")
    A.report_validation()              # export/validate + lint 报告
    names, mod_folder = A.export_and_install(zip_path)  # 导出 zip 并覆盖安装

环境变量：HOI4_PLATFORM_URL / HOI4_PLATFORM_TOKEN（令牌绝不入库），
HOI4_PROJECT_ID 可覆盖默认项目 2008。
"""
import io, json, os, shutil, sys, urllib.request, urllib.error, zipfile

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = os.environ["HOI4_PLATFORM_URL"].rstrip("/")
TOKEN = os.environ["HOI4_PLATFORM_TOKEN"]
PID = int(os.environ.get("HOI4_PROJECT_ID", "2008"))
MODDIR = r"C:\Users\xw130\Documents\Paradox Interactive\Hearts of Iron IV\mod"


def call(m, p, body=None, timeout=60):
    """平台 API 调用。成功返回 (status, 解析后 JSON 或 None)；HTTP 错误返回 (code, 响应文本)。"""
    d = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    r = urllib.request.Request(BASE + p, data=d, method=m)
    r.add_header("Content-Type", "application/json; charset=utf-8")
    r.add_header("Authorization", "Bearer " + TOKEN)
    r.add_header("User-Agent", "hoi4-modmaking-skills/1.x")
    try:
        x = urllib.request.urlopen(r, timeout=timeout)
        s = x.read().decode("utf-8", "replace")
        return x.status, (json.loads(s) if s else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def ensure_ok(s, b, what):
    """关键调用失败即中断，避免静默产出坏包。"""
    if s >= 300:
        msg = b if isinstance(b, str) else json.dumps(b, ensure_ascii=False)[:400]
        raise RuntimeError(f"{what} 失败：HTTP {s} -> {msg}")


def get_ids(kind, key):
    """解析实体 id 映射 {业务 id: 平台内部 id}。kind 如 ideas/decisions/dynamic-modifiers。"""
    _, b = call("GET", f"/api/projects/{PID}/{kind}")
    if not isinstance(b, list):
        return {}
    return {d[key]: d["id"] for d in b if key in d}


def get_first_category_id():
    _, b = call("GET", f"/api/projects/{PID}/decisions/categories")
    return b[0]["id"] if isinstance(b, list) and b else None


def report_validation():
    """导出前校验 + lint 报告（打印全部问题，供人工把关）。"""
    s, b = call("POST", f"/api/projects/{PID}/export/validate", {})
    print("\nexport/validate ->", s)
    if isinstance(b, dict):
        for it in b.get("issues", []):
            print("  issue:", it.get("severity"), it.get("code"), str(it.get("message"))[:150])
    s, b = call("GET", f"/api/lint/tree-validation/{PID}")
    print("lint ->", s)
    if isinstance(b, dict):
        issues = [(k, it.get("level"), it.get("msg"))
                  for k in ("idea", "focus", "event", "decision", "character")
                  for it in b.get(k, [])]
        print("lint issues:", len(issues))
        for k, lv, msg in issues[:30]:
            print(f"  [{k}] {lv}: {str(msg)[:140]}")


def export_and_install(zip_path, tmpdir=None):
    """导出项目 zip 到 zip_path，并覆盖安装到游戏 mod 目录。返回 (zip 文件列表, 安装目录名)。"""
    r = urllib.request.Request(BASE + f"/api/projects/{PID}/export/download")
    r.add_header("Authorization", "Bearer " + TOKEN)
    r.add_header("User-Agent", "hoi4-modmaking-skills/1.x")
    data = urllib.request.urlopen(r, timeout=120).read()
    print("\nexport bytes:", len(data))
    with open(zip_path, "wb") as f:
        f.write(data)
    z = zipfile.ZipFile(io.BytesIO(data))
    names = z.namelist()
    mod_folder = [n.split("/")[0] for n in names if "/" in n][0]
    mod_file = [n for n in names if n.endswith(".mod")][0]
    tmp = tmpdir or os.path.join(os.path.dirname(os.path.abspath(zip_path)), "_install_tmp")
    if os.path.isdir(tmp):
        shutil.rmtree(tmp)
    z.extractall(tmp)
    shutil.copy(os.path.join(tmp, mod_file), MODDIR)
    dst = os.path.join(MODDIR, mod_folder)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(os.path.join(tmp, mod_folder), dst)
    shutil.rmtree(tmp)
    print(f"installed {mod_folder} to {MODDIR}")
    return names, mod_folder
