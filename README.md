# 山徑運動誌

Wei 的登山 / 路跑紀錄網頁，資料來源是一份私人 Google 試算表，經過整理、去識別化後產生 `data.json` 供網頁讀取。

Claude Artifact 版（功能完整，含清單存檔/照片皆正常，但需要登入 Claude 帳號才能瀏覽）：
https://claude.ai/code/artifact/13655f94-217a-4c6f-88b0-7f622742c39e

GitHub Pages 版（任何人不用登入就能看，但登山清單只存在瀏覽器本機，換裝置/清瀏覽器資料會消失）：
https://taiwankiss.github.io/sport-journey/

兩份網頁內容一致，差別只在圖片來源與清單儲存方式，見下方「兩個版本」說明。

## 檔案說明
- `index.html` — Artifact 版網頁本體（發布到 Artifact 的檔案，圖片用 `/_blob/...` 指到 Claude 的圖床）
- `data.json` — Artifact 版讀取的資料（`BUILD_TARGET=artifact python3 build.py`，即預設模式，產生）
- `docs/` — **GitHub Pages 版**，由 `BUILD_TARGET=pages python3 build.py` 產生：
  - `docs/index.html` — 跟根目錄的 `index.html` 幾乎一樣，唯一差異是首圖背景改指到 `images/banner.jpg`（本機相對路徑，不是 `/_blob/...`）
  - `docs/data.json` — 每座山的 `photoUrl` 改成 `images/mountains/xxx.jpg` 這種本機相對路徑
  - `docs/images/` — 實際圖檔（banner + 每座山的照片），是從 `photos/`／`photos_google/`／`KV/` 複製過來的
  - `docs/photo_map.local.json` — 山名 → `docs/images/mountains/...` 檔名的對照表，`build.py` 在 `BUILD_TARGET=pages` 時會讀這份
- `build.py` — 把試算表匯出的 CSV 轉成 `data.json`／`docs/data.json` 的腳本，同時把每座山對應到照片與氣象署天氣連結（`cwa_pids.py`）
- `KV/Banner.jpg` / `Banner2.jpg` / `Banner3.jpg` — 首頁頂部橫幅候選（目前用 Banner3）
- `photo_assets.json` — 山名 → Artifact 圖片資產 id 對照表（Artifact 版用，已上傳到 Artifact 的 `/_blob/...`）
- `cwa_pids.py` — 中央氣象署「登山天氣」山頭名稱 → PID 對照表，及我們資料裡山名的別名對照
- `fetch_photos.py` / `download_photos.py` / `photo_urls.json` / `photo_manifest.json` / `photos/` — 從維基百科／維基共享資源抓山岳照片用的工具腳本與快取
- `photos_google/` — 維基百科找不到的冷門郊山，改用 Google 圖片搜尋找到的照片（人工挑過濾掉明顯有人的圖）

目前爬過的山（56）與想爬的山（17）皆已 100% 配對到真實照片。

## 兩個版本的差異
| | Artifact 版 | GitHub Pages 版 |
|---|---|---|
| 網址 | claude.ai/code/artifact/... | taiwankiss.github.io/sport-journey |
| 需要登入才能看 | 要（免費帳號即可） | 不用，任何人都能看 |
| 照片來源 | Claude Artifact 圖床 | repo 裡的 `docs/images/` 實體檔案 |
| 登山物品檢查清單 | 雲端存檔，跨裝置同步 | 只存在瀏覽器 localStorage，換裝置或清資料就消失 |
| 自訂網域 | 不行 | 可以（GitHub Pages 設定） |

日常內容更新（改文字、樣式、資料）都以 **Artifact 版為主**去改，改完後兩個 target 都要各跑一次 build 再各自發布/推送，才會同步。

## 之後要同步試算表最新內容時
來源試算表的連結與各分頁 gid 記在本機的 `SYNC_NOTES.md`（未進版控，僅存在你的電腦上）。同步步驟：
1. 用 curl 依 `SYNC_NOTES.md` 裡的連結重新下載各分頁 CSV 到本機的 `raw-sheet-export/`（此資料夾不進版控，因為其中一個分頁含有他人的個人成績資料）
2. 若有新山頭，跑 `python3 fetch_photos.py` + `python3 download_photos.py`（先在 `CANDIDATES` 裡補上維基百科條目候選標題），肉眼檢查 `photos/` 底下有沒有出現真人再決定要不要用：
   - Artifact 版：用 Artifact 工具的 `upload_asset` 上傳、把回傳的 id 記進 `photo_assets.json`
   - Pages 版：把照片複製進 `docs/images/mountains/`、在 `docs/photo_map.local.json` 補上山名對應
   - 若在 `cwa_pids.py` 的 `CWA_ALL` 找得到對應山名，順手也在 `ALIASES` 補上
3. 執行 `python3 build.py` 重新產生 `data.json`（Artifact 版），再執行 `BUILD_TARGET=pages python3 build.py` 重新產生 `docs/data.json`（Pages 版）
4. Artifact 版：用 Artifact 工具以 `url` 參數重新發布同一個網址（`files` 帶上新的 `data.json`）
   Pages 版：`git add -A && git commit && git push`，GitHub Pages 會自動重新部署

## 技術限制小提醒
Claude Artifact 的頁面基於安全考量，瀏覽器端無法直接連線 Google 試算表，所以「同步」是請 Claude 重新讀表、更新 `data.json` 再重新發布；頁面上的重新整理按鈕負責把最新同步好的資料載入畫面。

## 隱私聲明
本 repo 不包含試算表原始 CSV，因為其中一個分頁同時記錄了另一位使用者（非 Wei 本人）的個人路跑成績；`data.json` 與網頁內容僅包含 Wei 本人已同意公開的資料。
