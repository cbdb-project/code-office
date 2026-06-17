#!/usr/bin/env python3
"""
update.py — 從 CBDB main server 拉取最新的 OFFICE_CODES 全量資料，覆寫本地 OFFICE_CODES.txt。

何時用：當有人在 CBDB 後台新增/修改 office code 後、你需要立即取得最新資料時，手動執行本腳本，
再照常跑 code_office.py 即可（read_office 不需任何改動）。平時不需要跑——這是「改了就要、平時不用」
的按需刷新工具，不是排程。

    python update.py              # 從正式站拉取並覆寫 OFFICE_CODES.txt
    python update.py --dry-run    # 只報告差異，不覆寫
    python update.py --url <URL>  # 指定來源（測試/自架用；亦可用環境變數 CBDB_OFFICE_EXPORT_URL）

來源為 CBDB main server 的 GET /codes/OFFICE_CODES/export，輸出為 tab 分隔、quote-aware CSV、
無表頭、UTF-8、LF、11 欄。本腳本以 csv 模組解析驗證後，原子覆寫 OFFICE_CODES.txt。

僅用 Python 標準庫。設計見 cbdb-online-main-server: docs/OFFICE_CODES_EXPORT_SYNC.md。
"""

import argparse
import csv
import io
import os
import sys
import tempfile
import urllib.request

DEFAULT_URL = "https://input.cbdb.fas.harvard.edu/codes/OFFICE_CODES/export"
TARGET_FILE = "OFFICE_CODES.txt"
EXPECTED_COLUMNS = 11
TIMEOUT_SECONDS = 30


def fetch(url):
    """GET endpoint，回傳解碼後的文字。狀態非 200 或 Content-Type 非 text/plain 即 raise。"""
    req = urllib.request.Request(url, headers={"Accept": "text/plain"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
        status = getattr(resp, "status", None) or resp.getcode()
        if status != 200:
            raise RuntimeError(f"endpoint 回應非 200（HTTP {status}）：{url}")
        content_type = resp.headers.get("Content-Type", "")
        if "text/plain" not in content_type.lower():
            raise RuntimeError(
                f"Content-Type 非 text/plain（得到 '{content_type}'）；"
                "可能被導向登入頁或錯誤頁，未覆寫本地檔。"
            )
        # utf-8-sig：若伺服端意外輸出 BOM 則主動剝除（契約要求無 BOM，此為防禦性）。
        return resp.read().decode("utf-8-sig")


def validate(text):
    """以 csv.reader 解析驗證，回傳列數；不合格則 raise（防呆，非唯一真相）。

    用 io.StringIO 讓 csv.reader 正確處理引號內換行（不可用 splitlines）。
    """
    rows = list(csv.reader(io.StringIO(text), delimiter="\t"))
    if not rows:
        raise RuntimeError("匯出內容為空。")

    prev_id = None
    for line_no, row in enumerate(rows, start=1):
        if len(row) != EXPECTED_COLUMNS:
            raise RuntimeError(
                f"第 {line_no} 列欄數為 {len(row)}，預期 {EXPECTED_COLUMNS}（可能格式漂移或含表頭）。"
            )
        # 第 0 欄為 c_office_id：須為整數且整檔嚴格遞增（對齊伺服端 orderBy('c_office_id')）。
        # 此檢查同時排除表頭（'c_office_id' 無法 int()）與內容漂移。
        try:
            office_id = int(row[0])
        except ValueError:
            raise RuntimeError(
                f"第 {line_no} 列第 1 欄 '{row[0]}' 非整數（疑似誤含表頭或內容漂移）。"
            )
        if prev_id is not None and office_id <= prev_id:
            raise RuntimeError(
                f"第 {line_no} 列 c_office_id={office_id} 未嚴格遞增（前一列={prev_id}）。"
            )
        prev_id = office_id

    return len(rows)


def count_existing(path):
    """回傳本地檔的 (列數, 欄數)；不存在回 (None, None)。"""
    if not os.path.exists(path):
        return None, None
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f, delimiter="\t"))
    except (OSError, UnicodeDecodeError):
        # 本地檔損壞/不可讀時僅影響「舊列數」報告，不應中斷更新流程。
        return None, None
    cols = len(rows[0]) if rows else 0
    return len(rows), cols


def write_atomic(path, text):
    """以同目錄暫存檔 + os.replace 原子覆寫，避免部分寫入。寫出 UTF-8、強制 LF、無 BOM。"""
    # 強制 LF：即使上游/proxy 偶發吐出 CRLF，本地檔仍維持契約要求的 LF（與 fetch 的 BOM 防禦一致）。
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    dir_name = os.path.dirname(path) or "."
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, prefix=".OFFICE_CODES.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="從 CBDB main server 更新本地 OFFICE_CODES.txt。"
    )
    parser.add_argument(
        "--url",
        default=os.environ.get("CBDB_OFFICE_EXPORT_URL", DEFAULT_URL),
        help="來源 endpoint URL（預設正式站；可用環境變數 CBDB_OFFICE_EXPORT_URL 覆寫）。",
    )
    parser.add_argument("--dry-run", action="store_true", help="只報告差異，不覆寫檔案。")
    args = parser.parse_args(argv)

    target_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), TARGET_FILE)

    try:
        text = fetch(args.url)
        new_count = validate(text)
    except Exception as e:  # noqa: BLE001 — 任何失敗都保留本地檔、非零退出
        print(f"[失敗] {e}", file=sys.stderr)
        print("本地 OFFICE_CODES.txt 未變更。", file=sys.stderr)
        return 1

    old_count, old_cols = count_existing(target_path)

    if args.dry_run:
        print(
            f"[dry-run] 來源 {new_count} 列 / {EXPECTED_COLUMNS} 欄；"
            f"本地 {old_count} 列 / {old_cols} 欄。未覆寫。"
        )
        return 0

    try:
        write_atomic(target_path, text)
    except Exception as e:  # noqa: BLE001
        print(f"[失敗] 寫入/替換時發生錯誤：{e}", file=sys.stderr)
        print(
            "（若目標在 OneDrive 等同步目錄，可能遇同步鎖/檔案佔用，請關閉佔用程式後重試。）",
            file=sys.stderr,
        )
        return 1

    print(f"[完成] OFFICE_CODES.txt 已更新：{old_count} → {new_count} 列。")
    if old_cols is not None and old_cols != EXPECTED_COLUMNS:
        print(
            f"  注意：欄數由 {old_cols} → {EXPECTED_COLUMNS}"
            "（屬預期改版：移除已於 main server 刪除的 c_category_1~4 與 c_office_id_old）。"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
