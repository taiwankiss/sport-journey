# 山徑運動誌 (Wei's Sport Journey)

Wei 的登山/路跑紀錄網站，同時發佈到三個地方：

- **Artifact**: https://claude.ai/code/artifact/13655f94-217a-4c6f-88b0-7f622742c39e
- **GitHub Pages**: https://taiwankiss.github.io/sport-journey/
- **Cloudflare Pages**: https://sport-journey.pages.dev （比 GitHub Pages 快，台灣有節點；已透過 GitHub 整合自動部署，push 到 main 就會自動重建，不需要額外操作）

GitHub repo: https://github.com/taiwankiss/sport-journey (`origin`/`main`)

## 檔案結構

- `index.html` — **唯一的原始檔**，單一 HTML 檔案（inline CSS/JS），是 Artifact 版本的來源
- `build.py` — 讀 `raw-sheet-export/*.csv` 產生 `data.json`（Artifact 用，圖片走 `/_blob/{id}`）；`BUILD_TARGET=pages python3 build.py` 產生 `docs/data.json`（GitHub Pages 用，圖片走本地相對路徑）
- `make_docs_html.py` — 從 `index.html` 產生 `docs/index.html`（套用完整 HTML5 shell + favicon/manifest，因為 GitHub Pages 沒有 Artifact 平台的外殼）
- `docs/` — GitHub Pages 實際服務的目錄（也是 Cloudflare Pages 的 build output directory）
- `race_media.json` / `docs/race_media.local.json` — 路跑賽事的照片/成績證明對照表（日期 → blob id 或本地路徑），日期字串必須跟 `data.json` 裡 `races[].date` 完全一致（注意原始 Google Sheet 日期補零不一致：2024/2025 是 `4/28` 不補零，2026 是 `04/18` 有補零）

## 發佈流程（每次改完 index.html 後）

1. 檢查語法：`<style>` 大括號數量要相等；把 `<script>` 內容存成 `.js` 檔跑 `node --check`
2. `python3 build.py` （產生 artifact 用的 `data.json`）
3. `BUILD_TARGET=pages python3 build.py` （產生 `docs/data.json`）
4. `python3 make_docs_html.py` （產生 `docs/index.html`）
5. 本地起 `python3 -m http.server` 測試 `docs/`，用 Browser 工具實際點過一輪再上線
6. Publish 到 Artifact：`data.json` 需要先複製到目前工作目錄底下（Artifact 工具的 `files` 只能讀工作目錄內的檔案），複製成 `_data_for_publish.json` 再傳，傳完刪除
7. `git add` + commit + push（這步會自動觸發 GitHub Pages 跟 Cloudflare Pages 重新部署）
8. `gh api repos/taiwankiss/sport-journey/pages/builds/latest --jq '{status, error}'` 輪詢直到 `status:built` 再跟使用者回報完成

## 環境測試注意事項

Browser 工具的分頁如果是隱藏狀態（`document.hidden === true`），`requestAnimationFrame`、`ResizeObserver`、`IntersectionObserver` 的 callback 都可能不會準時觸發（甚至完全不觸發）。遇到量測/驗證卡住時：
- 優先用**同步**的 `getBoundingClientRect()` 等 API 直接讀取即時 layout，而不是依賴這些非同步 callback
- 捲動觸發類的效果（如 scroll-reveal、parallax）沒辦法在隱藏分頁裡可靠測試，用公式手算 + code review 確認邏輯正確即可，不用死磕螢幕截圖

## 使用者偏好

- 溝通語言：繁體中文
- 每個小改動都直接做完、驗證、發佈到三個平台，不用每次都先問過
- CSS 共用 class（例如 `.progress-track`、`.climbed-summary`）常常被兩三個不同分頁共用，改動前要注意是否會波及不想改的地方，必要時用複合選擇器或額外 class 精準 scope
