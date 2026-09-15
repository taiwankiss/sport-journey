# 山徑運動誌

Wei 的登山 / 路跑紀錄網頁，資料來源是一份私人 Google 試算表，經過整理、去識別化後產生 `data.json` 供網頁讀取。

發布網址：https://claude.ai/code/artifact/13655f94-217a-4c6f-88b0-7f622742c39e

## 檔案說明
- `index.html` — 網頁本體（發布到 Artifact 的檔案）
- `data.json` — 網頁讀取的資料（由 `build.py` 從私人試算表匯出的 CSV 產生，CSV 原始檔不進版控）
- `build.py` — 把試算表匯出的 CSV 轉成 `data.json` 的腳本，同時把每座山對應到照片（`photo_assets.json`）與氣象署天氣連結（`cwa_pids.py`）
- `KV/Banner.jpg` — 首頁頂部橫幅（主視覺）
- `photo_assets.json` — 山名 → Artifact 圖片資產 id 對照表（已上傳到 Artifact 的 `/_blob/...`）
- `cwa_pids.py` — 中央氣象署「登山天氣」山頭名稱 → PID 對照表，及我們資料裡山名的別名對照
- `fetch_photos.py` / `download_photos.py` / `photo_urls.json` / `photo_manifest.json` / `photos/` — 從維基百科／維基共享資源抓山岳照片用的工具腳本與快取
- `photos_google/` — 維基百科找不到的冷門郊山，改用 Google 圖片搜尋找到的照片（人工挑過濾掉明顯有人的圖）

目前爬過的山（56）與想爬的山（17）皆已 100% 配對到真實照片。

## 之後要同步試算表最新內容時
來源試算表的連結與各分頁 gid 記在本機的 `SYNC_NOTES.md`（未進版控，僅存在你的電腦上）。同步步驟：
1. 用 curl 依 `SYNC_NOTES.md` 裡的連結重新下載各分頁 CSV 到本機的 `raw-sheet-export/`（此資料夾不進版控，因為其中一個分頁含有他人的個人成績資料）
2. 若有新山頭，跑 `python3 fetch_photos.py` + `python3 download_photos.py`（先在 `CANDIDATES` 裡補上維基百科條目候選標題），肉眼檢查 `photos/` 底下有沒有出現真人再決定要不要用，接著用 Artifact 工具的 `upload_asset` 上傳、把回傳的 id 記進 `photo_assets.json`。若在 `cwa_pids.py` 的 `CWA_ALL` 找得到對應山名，順手也在 `ALIASES` 補上。
3. 執行 `python3 build.py` 重新產生 `data.json`
4. 用 Artifact 工具以 `url` 參數重新發布同一個網址（`files` 帶上新的 `data.json`）

## 技術限制小提醒
Claude Artifact 的頁面基於安全考量，瀏覽器端無法直接連線 Google 試算表，所以「同步」是請 Claude 重新讀表、更新 `data.json` 再重新發布；頁面上的重新整理按鈕負責把最新同步好的資料載入畫面。

## 隱私聲明
本 repo 不包含試算表原始 CSV，因為其中一個分頁同時記錄了另一位使用者（非 Wei 本人）的個人路跑成績；`data.json` 與網頁內容僅包含 Wei 本人已同意公開的資料。
