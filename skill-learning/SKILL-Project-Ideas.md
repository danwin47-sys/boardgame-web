# SKILL實用專案建議

> 從零到專家的專案實作指南  
> 最後更新：2025-12-09

---

## 📊 專案難度分級

- 🟢 **初級** - 適合SKILL新手，1-3天完成
- 🟡 **中級** - 需要基礎知識，1-2週完成  
- 🔴 **高級** - 需要進階技能，2週以上

---

## 目錄

- [初級專案](#初級專案)
- [中級專案](#中級專案)
- [高級專案](#高級專案)
- [專業級專案](#專業級專案)
- [專案實作指南](#專案實作指南)

---

# 初級專案

## 🟢 專案 1: 自動化報表生成器

### 專案目標

撰寫腳本自動生成設計統計報表，列出當前cell view中所有元件的數量和類型。

### 學習重點

- ✅ 基本SKILL語法
- ✅ 存取cell view物件
- ✅ 檔案寫入操作
- ✅ 使用迴圈和條件判斷

### 功能需求

1. 讀取當前開啟的cell view
2. 統計所有instance的類型和數量
3. 生成文字報表檔案
4. 在CIW顯示摘要資訊

### 實作步驟

```lisp
; Step 1: 取得當前cell view
procedure(generateReport()
  let((cv instList typeCount port)
    cv = geGetEditCellView()
    
    ; Step 2: 檢查cv是否有效
    if(cv then
      ; Step 3: 初始化統計表
      typeCount = makeTable("typeCount" nil)
      
      ; Step 4: 遍歷所有instances
      foreach(inst cv~>instances
        let((cellName count))
          cellName = inst~>cellName
          count = arrayref(typeCount cellName)
          
          ; 累加計數
          if(count
            then arrayref(typeCount cellName count + 1)
            else arrayref(typeCount cellName 1)
          )
        )
      )
      
      ; Step 5: 寫入報表檔案
      port = outfile("design_report.txt" "w")
      fprintf(port "=== Design Report ===\n")
      fprintf(port "Cell: %s\n" cv~>cellName)
      fprintf(port "Library: %s\n\n" cv~>libName)
      fprintf(port "Instance Statistics:\n")
      fprintf(port "-------------------\n")
      
      ; 輸出統計結果
      foreach(mapcar entry typeCount
        fprintf(port "%s: %d\n" car(entry) cadr(entry))
      )
      
      close(port)
      printf("Report generated: design_report.txt\n")
      
    else
      error("No cell view is open!")
    )
  )
)
```

### 預期成果

- 📄 生成完整的設計報表檔案
- 📊 清楚列出各類元件數量
- ✅ 可重複執行、更新報表

### 擴展方向

- 加入net數量統計
- 統計總面積
- 生成HTML格式報表
- 加入時間戳記

---

## 🟢 專案 2: 批次元件重命名工具

### 專案目標

批次修改選定元件的命名規則，例如從 `I0, I1, I2` 改為 `INST_0, INST_1, INST_2`。

### 學習重點

- ✅ 使用者輸入處理
- ✅ 字串操作
- ✅ 物件屬性修改
- ✅ 錯誤處理

### 功能需求

1. 讓使用者輸入前綴字串
2. 選擇特定類型的元件
3. 批次重新命名
4. 提供Undo功能

### 實作步驟

```lisp
procedure(batchRename(@optional (prefix "INST"))
  let((cv counter newName))
    cv = geGetEditCellView()
    counter = 0
    
    when(cv
      foreach(inst cv~>instances
        ; 生成新名稱
        newName = sprintf("%s_%d" prefix counter)
        
        ; 修改instance名稱
        inst~>name = newName
        counter = counter + 1
        
        printf("Renamed to: %s\n" newName)
      )
      
      printf("\nTotal renamed: %d instances\n" counter)
    )
  )
)
```

### 預期成果

- 🔄 快速批次重命名
- 📝 清楚的命名規則
- ✅ 提升設計一致性

---

## 🟢 專案 3: 圖層顏色快速切換器

### 專案目標

建立快捷鍵工具，快速切換常用圖層的顯示/隱藏狀態。

### 學習重點

- ✅ 圖層操作函數
- ✅ 快捷鍵綁定
- ✅ 使用者介面互動

### 功能需求

1. 定義常用圖層組合
2. 一鍵切換顯示模式
3. 儲存使用者偏好設定

### 實作範例

```lisp
procedure(toggleMetalLayers()
  let((cv lsw metalLayers))
    cv = geGetEditCellView()
    metalLayers = list("Metal1" "Metal2" "Metal3")
    
    foreach(layer metalLayers
      ; 切換圖層可見性
      leSetLayerVisible(cv layer 
        !leGetLayerVisible(cv layer))
    )
    
    printf("Metal layers toggled\n")
  )
)

; 綁定到快捷鍵 Ctrl+M
hiSetBindKey("Layout" "<Key>m" "toggleMetalLayers()")
```

---

## 🟢 專案 4: 設計規則檢查輔助工具

### 專案目標

建立簡單的預檢查工具，在執行正式DRC前找出明顯錯誤。

### 學習重點

- ✅ 幾何計算
- ✅ 規則檢查邏輯
- ✅ 錯誤報告生成

### 檢查項目

- 最小線寬檢查
- 最小間距檢查
- 懸空金屬檢測
- 重疊元件檢查

---

# 中級專案

## 🟡 專案 5: 智慧型元件放置助手

### 專案目標

開發工具協助設計師按照規則自動放置元件，保持適當間距和對齊。

### 學習重點

- ✅ 座標計算
- ✅ 幾何對齊
- ✅ GUI表單建立
- ✅ 互動式操作

### 功能需求

1. 讀取元件列表
2. 計算最佳放置位置
3. 自動對齊和間距
4. 支援行/列排列

### 實作架構

```lisp
procedure(autoPlace(
  @key (spacing 10.0) (orientation "R0") (direction "horizontal"))
  
  let((cv insts xPos yPos))
    cv = geGetEditCellView()
    xPos = 0
    yPos = 0
    
    ; 取得選中的instances
    insts = geGetSelSet()
    
    foreach(inst insts
      ; 移動到新位置
      dbMoveFig(inst nil xPos:yPos)
      
      ; 計算下一個位置
      if(direction == "horizontal"
        then xPos = xPos + spacing
        else yPos = yPos + spacing
      )
    )
    
    printf("Placed %d instances\n" length(insts))
  )
)
```

### 預期成果

- 🎯 精確的元件排列
- ⚡ 大幅節省手動擺放時間
- 📐 一致的設計風格

### 擴展方向

- 支援矩陣式排列 (m×n)
- 智慧避障功能
- 根據連接關係優化位置
- 儲存和載入排列模板

---

## 🟡 專案 6: 參數化單元格（PCell）生成器

### 專案目標

建立可重複使用的參數化元件，例如電阻、電容、自訂陣列等。

### 學習重點

- ✅ PCell架構
- ✅ 參數定義和驗證
- ✅ 動態Layout生成
- ✅ DRC友好設計

### 範例：參數化電阻

```lisp
pcDefinePCell(
  list(ddGetObj("myLib") "resistor" "layout")
  
  ; 參數定義
  ((width 1.0)
   (length 5.0)
   (layer "Poly"))
  
  ; 繪製函數
  let((cv box))
    cv = pcCellView
    
    ; 參數驗證
    when(width < 0.5
      error("Width must be >= 0.5um")
    )
    
    ; 繪製電阻本體
    box = list(0:0 width:length)
    dbCreateRect(cv list(layer "drawing") box)
    
    ; 繪製接觸點
    ; ... (詳細實作)
    
    printf("Resistor created: W=%f L=%f\n" width length)
  )
)
```

### 實用PCell建議

1. **電阻陣列** - 可調整數量和間距
2. **電容陣列** - MOM/MIM電容
3. **Guard Ring** - 可調大小的保護環
4. **Via陣列** - 自動計算數量
5. **Dummy Fill** - 金屬填充塊

---

## 🟡 專案 7: 自訂GUI控制面板

### 專案目標

建立圖形化介面，整合常用工具到單一控制面板。

### 學習重點

- ✅ hiCreateAppForm使用
- ✅ 按鈕和輸入欄位
- ✅ 回呼函數
- ✅ 資料驗證

### 面板功能建議

- 快速圖層切換
- 常用腳本執行
- 參數設定介面
- 設計檢查工具

### 實作範例

```lisp
procedure(createControlPanel()
  let((form))
    form = hiCreateAppForm(
      ?name 'myControlPanel
      ?formTitle "Design Control Panel"
      ?buttonLayout 'Close
      
      ?fields list(
        hiCreateButton(
          ?name 'btnAutoPlace
          ?buttonText "Auto Place"
          ?callback "autoPlace()"
        )
        
        hiCreateButton(
          ?name 'btnGenReport
          ?buttonText "Generate Report"
          ?callback "generateReport()"
        )
        
        hiCreateStringField(
          ?name 'txtPrefix
          ?prompt "Instance Prefix:"
          ?value "INST"
        )
        
        hiCreateButton(
          ?name 'btnRename
          ?buttonText "Batch Rename"
          ?callback "batchRename(form->txtPrefix->value)"
        )
      )
    )
    
    hiDisplayForm(form)
  )
)
```

### 預期成果

- 🎨 美觀的使用者介面
- 🚀 一鍵執行常用功能
- 💾 儲存使用偏好

---

## 🟡 專案 8: 佈局比較工具

### 專案目標

比較兩個Layout版本的差異，標示出修改的部分。

### 學習重點

- ✅ 多個cell view操作
- ✅ 幾何比較算法
- ✅ 視覺化差異標記
- ✅ 報表生成

### 功能需求

1. 載入兩個版本的Layout
2. 比較instances、nets、shapes
3. 用顏色標記差異
4. 生成差異報表

---

# 高級專案

## 🔴 專案 9: 自動化佈線工具

### 專案目標

開發智慧型佈線工具，自動連接指定的pins並避開障礙物。

### 學習重點

- ✅ 路徑搜尋算法（A*、Dijkstra）
- ✅ 複雜幾何運算
- ✅ DRC規則整合
- ✅ 效能優化

### 核心算法

```lisp
procedure(autoRoute(fromPin toPin layer)
  let((path obstacles grid))
    ; 建立柵格系統
    grid = createRoutingGrid(cv layer)
    
    ; 收集障礙物
    obstacles = collectObstacles(cv layer)
    
    ; A*尋路
    path = aStarSearch(fromPin toPin grid obstacles)
    
    ; 繪製路徑
    if(path
      then drawPath(cv layer path)
      else warn("No valid route found!")
    )
  )
)
```

### 技術挑戰

- 多層繞線策略
- Via最小化
- 時序考量
- 擁塞避免

---

## 🔴 專案 10: 設計資料版本管理系統

### 專案目標

整合Git版本控制到Cadence環境，追蹤設計變更歷史。

### 學習重點

- ✅ 外部程式呼叫
- ✅ 檔案系統操作
- ✅ 差異比對
- ✅ 使用者權限管理

### 功能架構

1. **Commit功能** - 儲存設計快照
2. **Diff工具** - 視覺化差異
3. **Merge助手** - 協助合併衝突
4. **History瀏覽** - 時間軸檢視

### 參考專案

GitHub上的 **CdsGit** 專案已實作部分功能，可以作為起點。

---

## 🔴 專案 11: 電路網表分析器

### 專案目標

分析複雜電路的網表，找出關鍵路徑、扇出過大等問題。

### 學習重點

- ✅ 圖論算法
- ✅ 網表解析
- ✅ 拓樸分析
- ✅ 效能瓶頸識別

### 分析功能

- 關鍵路徑識別
- 扇出分析
- 未使用接腳檢測
- 浮接網路檢查
- 電源網路分析

---

## 🔴 專案 12: Layout vs Schematic自動修正

### 專案目標

自動檢測並修正Layout和Schematic之間的不一致。

### 學習重點

- ✅ LVS結果解析
- ✅ 自動錯誤定位
- ✅ 智慧修正建議
- ✅ 批次處理

### 工作流程

1. 執行LVS
2. 解析錯誤報告
3. 定位問題元件
4. 提供修正建議或自動修正
5. 重新驗證

---

# 專業級專案

## 🔴🔴 專案 13: 完整PCell庫開發

### 專案目標

建立包含常用元件的完整PCell庫，符合foundry規範。

### 包含元件

- 各種尺寸的電晶體
- 電阻陣列（Poly, N-well, P-well）
- 電容（MOM, MIM, MOS）
- Via/Contact陣列
- Guard Ring
- Dummy Metal Fill
- ESD保護元件

### 品質要求

- ✅ 完整DRC通過
- ✅ 參數驗證
- ✅ 使用文件
- ✅ 單元測試

---

## 🔴🔴 專案 14: 類比Layout自動化框架

### 專案目標

開發自動化框架，從電路圖生成優化的類比Layout。

### 核心功能

1. **元件擺放優化**
   - 對稱性保持
   - 匹配元件配對
   - 熱考量

2. **智慧繞線**
   - 對稱繞線
   - 最小寄生
   - 遮蔽處理

3. **自動Guard Ring生成**

4. **後處理優化**
   - Dummy fill
   - Antenna檢查修正

---

## 🔴🔴 專案 15: 完整DRC/LVS自動化流程

### 專案目標

建立一鍵式驗證流程，自動執行DRC、LVS、Antenna等所有檢查。

### 流程設計

```
開始 → 參數設定 → DRC → 報告解析 → 
自動修正 → LVS → 比對 → Antenna → 
最終報告 → 郵件通知
```

### 進階功能

- 錯誤自動分類
- 建議修正方案
- 趨勢分析（錯誤數量變化）
- 與CI/CD整合

---

# 專案實作指南

## 🎯 如何選擇專案

### 新手建議（第1-2個月）

1. 從**專案1-4**選一個開始
2. 完成後嘗試擴展功能
3. 分享程式碼獲得反饋

### 進階學習（第3-6個月）

1. 挑戰**專案5-8**
2. 結合實際工作需求
3. 注重程式品質和可維護性

### 專家目標（6個月以上）

1. 投入**專案9-15**
2. 考慮開源貢獻
3. 建立個人工具庫

---

## 📝 開發最佳實踐

### 1. 程式碼組織

```
myProject/
├── main.il              # 主程式
├── utils.il             # 工具函數
├── gui.il               # GUI相關
├── config.il            # 配置參數
├── tests/               # 測試腳本
│   └── test_main.il
└── docs/                # 說明文件
    └── README.md
```

### 2. 註解規範

```lisp
/*******************************************************************************
 * Function: autoPlace
 * Description: 自動排列選中的instances
 * Parameters:
 *   @spacing - 元件間距 (默認: 10.0)
 *   @orientation - 方向 (默認: "R0")
 *   @direction - 排列方向 (默認: "horizontal")
 * Returns: t if successful, nil otherwise
 * Author: Your Name
 * Date: 2025-12-09
 ******************************************************************************/
procedure(autoPlace( ... )
  ; 實作內容
)
```

### 3. 錯誤處理

```lisp
procedure(safeExecute()
  errset(
    let((result))
      ; 可能出錯的程式碼
      result = riskyOperation()
      result
    )
    t  ; 顯示錯誤訊息
  )
)
```

### 4. 測試驅動開發

```lisp
; test_main.il
procedure(testAutoPlace()
  let((result))
    ; 設定測試環境
    setupTestEnv()
    
    ; 執行測試
    result = autoPlace(?spacing 5.0)
    
    ; 驗證結果
    if(result
      then printf("✓ Test passed\n")
      else error("✗ Test failed")
    )
    
    ; 清理
    cleanupTestEnv()
  )
)
```

---

## 📊 專案進度追蹤

### 專案檢查清單

#### 初級專案完成標準

- [ ] 程式碼可正常執行
- [ ] 有基本註解
- [ ] 處理常見錯誤
- [ ] 有簡單的使用說明

#### 中級專案完成標準

- [ ] 結構化程式碼
- [ ] 完整的錯誤處理
- [ ] 使用者友好的介面
- [ ] 詳細的文件說明
- [ ] 基本的測試覆蓋

#### 高級專案完成標準

- [ ] 模組化設計
- [ ] 全面的錯誤處理和恢復
- [ ] 效能優化
- [ ] 完整的測試套件
- [ ] 使用手冊和API文件
- [ ] 版本控制

---

## 🏆 專案展示建議

### GitHub開源分享

1. 建立清晰的README
2. 提供安裝說明
3. 包含使用範例
4. 加入螢幕截圖/影片
5. 標註License

### 公司內部分享

1. 準備簡報說明功能
2. 提供使用培訓
3. 收集使用者反饋
4. 持續改進

---

## 💡 創意專案激發

### 從工作痛點出發

- 哪個任務最重複、最耗時？
- 哪個檢查最容易出錯？
- 哪個流程可以自動化？

### 觀察他人需求

- 同事常遇到什麼問題？
- 新人最常問什麼？
- 有哪些手動操作頻繁發生？

### 學習先進工具

- 研究商業EDA工具的功能
- 思考如何用SKILL實現類似功能
- 加入自己的創新想法

---

## 🎓 學習資源整合

每個專案都可以參考：

- 📘 [SKILL函數參考手冊](./SKILL-Function-Reference.md)
- 🌐 [社群資源清單](./Community-SKILL-Resources.md)
- 🔍 Cadence官方文件（cdsdoc）
- 💻 GitHub開源專案

---

## ✅ 成功案例分享

### 實際節省時間統計

- 自動報表生成：**每週節省2小時**
- 批次重命名工具：**每次節省30分鐘**
- PCell庫：**新設計速度提升50%**
- 自動驗證流程：**減少90%的人為錯誤**

---

## 🚀 開始你的第一個專案

**推薦起手式：**

1. 選擇**專案1: 自動化報表生成器**
2. 花1天時間完成基本版本
3. 每天加入一個新功能
4. 一週後你會有個實用工具！

**記住：**
> "最好的學習方式就是動手實作。不要追求完美，重要的是開始！"

---

**祝專案開發順利！** 🎉

*有問題隨時參考社群資源或查閱官方文件*
