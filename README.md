# code-office

給朝代的官職加上 CBDB 官職 id：依 `input.txt` 比對 `OFFICE_CODES.txt`，輸出 `output.txt`。

## 平時用法

```bash
pip install pandas char-converter   # 首次安裝相依套件
python code_office.py
```

## 需要最新官職代碼時

若同事剛在 CBDB 後台新增/修改了 office code、你需要**立刻**拿到最新資料（平時不必跑）：

```bash
python update.py        # 從 CBDB 拉取最新 OFFICE_CODES.txt（僅用 Python 標準庫）
python code_office.py
```

- `python update.py --dry-run`：只報告差異、不覆寫。
- `--url <URL>` 或環境變數 `CBDB_OFFICE_EXPORT_URL`：指定來源（測試/自架用）。
- 拉取失敗時（例如來源暫時無法連線）會保留本地檔、不做任何更動。

> 首次跑 `update.py` 後，`OFFICE_CODES.txt` 會由 16 欄變成 **11 欄**，這是正常的——CBDB 已移除不再使用的 5 個欄位（`c_category_1`~`c_category_4`、`c_office_id_old`），不影響 `code_office.py`。
