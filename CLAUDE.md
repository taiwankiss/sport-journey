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
5. 驗證改動（見下方「驗證要花多重」的判斷原則，不是每次都要開瀏覽器截圖點一輪）
6. Publish 到 Artifact：`data.json` 需要先複製到目前工作目錄底下（Artifact 工具的 `files` 只能讀工作目錄內的檔案），複製成 `_data_for_publish.json` 再傳，傳完刪除
7. `git add` + commit + push（這步會自動觸發 GitHub Pages 跟 Cloudflare Pages 重新部署）
8. `gh api repos/taiwankiss/sport-journey/pages/builds/latest --jq '{status, error}'` 輪詢直到 `status:built` 再跟使用者回報完成

### 驗證要花多重

截圖跟開瀏覽器點過一輪很花 token，不是每個改動都值得。判斷原則：

- **純 CSS 視覺微調 / 文字內容修改**（顏色、間距、字級、漸層、動畫參數、文案這類）：**不用**截圖或開瀏覽器點過一輪。用 `node --check` + 大括號計數確認語法沒壞，需要的話用 `javascript_exec` 讀 `getComputedStyle` 或 log 一下邏輯值（例如漸層色、排序方向、data-active 狀態）確認數字對了就好。
- **牽涉互動邏輯、layout 結構、跨分頁共用 class 的改動**（可能波及其他地方、新加的功能、排序/篩選邏輯）：才需要實際開瀏覽器點過、視覺確認沒有壞掉其他分頁。
- 使用者想「眼見為憑」的時候會直接說，不用預先幫他截。

### 發佈頻率：小改動要攢著一起發

不要每講一句小修改就整套（build ×2 + Artifact publish + git push + 輪詢建置）跑一次——這一套很貴，跑好幾次等於貴好幾倍。原則：
- 同一波對話裡如果使用者連續丟出好幾個小調整，**先都改完、在本機/Artifact 草稿層級確認邏輯對了**，等使用者說「可以發了」、告一段落、或明顯是最後一個小修改時，才一次跑完整發佈流程（Artifact + git push + 輪詢）。
- 如果不確定是不是還有下一個小改動要來，可以直接問一句「還有其他要改的嗎，還是現在發布？」而不是預設每次都發。

## 環境測試注意事項

Browser 工具的分頁如果是隱藏狀態（`document.hidden === true`），`requestAnimationFrame`、`ResizeObserver`、`IntersectionObserver` 的 callback 都可能不會準時觸發（甚至完全不觸發）。遇到量測/驗證卡住時：
- 優先用**同步**的 `getBoundingClientRect()` 等 API 直接讀取即時 layout，而不是依賴這些非同步 callback
- 捲動觸發類的效果（如 scroll-reveal、parallax）沒辦法在隱藏分頁裡可靠測試，用公式手算 + code review 確認邏輯正確即可，不用死磕螢幕截圖

## 使用者偏好

- 溝通語言：繁體中文
- 小改動直接做完、改完就地確認邏輯對了，不用每次都先問過；但**發佈到三平台這件事要攢著幾個小改動一起做**，不要每個小改動各跑一次完整發佈流程（見上方「發佈頻率」）。原因：2026-09-22 發現連續幾個小調整各自跑一次完整流程（build + 截圖驗證 + Artifact publish + git push + 輪詢建置）非常花 token 跟時間
- 純 CSS/文案微調不用開瀏覽器截圖確認，看 code 邏輯 + `getComputedStyle` 檢查就好；牽涉 layout/互動邏輯或跨分頁影響的改動才需要實際截圖點過一輪（見上方「驗證要花多重」）
- CSS 共用 class（例如 `.progress-track`、`.climbed-summary`）常常被兩三個不同分頁共用，改動前要注意是否會波及不想改的地方，必要時用複合選擇器或額外 class 精準 scope
