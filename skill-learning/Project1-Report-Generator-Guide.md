# 自動化報表生成器 - 詳細說明

> 專案1的深度解析：為什麼它是最佳入門專案？

---

## 🎯 核心作用

### 一句話總結

**自動統計和記錄當前IC設計中所有元件的詳細資訊，生成易讀的報表檔案。**

---

## 💡 實際應用場景

### 場景 1：設計審查會議前的準備

**問題：**
主管問：「這個設計用了多少個電晶體？有幾個電阻？」
你需要手動數嗎？❌

**解決方案：**
執行報表生成器 → 1秒鐘生成完整統計 ✅

**報表範例輸出：**

```
=== Design Report ===
Cell: amplifier_core
Library: analog_lib
Generated: 2025-12-09 15:11:32

Instance Statistics:
-------------------
nfet3: 28
pfet3: 24
rpoly: 12
cmom: 8
mimcap: 4
via1: 156
via2: 98

Total Instances: 330
Total Nets: 156
```

**價值：**

- ⏱️ 節省時間：從手動數20分鐘 → 自動1秒
- 📊 準確度：100%正確，無人為疏漏
- 📝 專業性：報表格式統一、易讀

---

### 場景 2：追蹤設計演進

**問題：**
經過一週的優化，設計有什麼變化？元件數量增減？

**解決方案：**
每天自動生成報表 → 對比歷史記錄

**對比範例：**

```
Version 1.0 (2025-12-01):
  nfet3: 28, pfet3: 24, Total: 330

Version 1.1 (2025-12-09):
  nfet3: 32, pfet3: 28, Total: 358

Changes:
  + nfet3: +4 (14% increase)
  + pfet3: +4 (17% increase)
  + Total: +28 (8% increase)
```

**價值：**

- 📈 趨勢分析：設計複雜度變化
- 🎯 優化追蹤：是否達到減少元件的目標
- 📅 版本管理：清楚的歷史記錄

---

### 場景 3：多個設計的快速比較

**問題：**
有3個不同的設計方案，哪個用的元件最少？

**解決方案：**
對每個方案執行報表生成器 → 並排比較

**比較表格：**

```
| 元件類型  | 方案A | 方案B | 方案C | 最佳 |
|----------|-------|-------|-------|------|
| nfet3    | 28    | 32    | 24    | C ✓  |
| pfet3    | 24    | 28    | 20    | C ✓  |
| Total    | 330   | 358   | 298   | C ✓  |
```

**價值：**

- ⚖️ 客觀比較：數據說話
- 💰 成本評估：元件少 = 面積小 = 成本低
- 🚀 決策支援：快速選擇最佳方案

---

### 場景 4：BOM（Bill of Materials）生成

**問題：**
需要提供給製造部門元件清單

**解決方案：**
報表生成器 → 直接輸出BOM格式

**BOM範例：**

```
Bill of Materials - amplifier_core
===================================
Part Number | Type  | Quantity | Unit Cost | Total
------------|-------|----------|-----------|-------
NFET_STD    | nfet3 | 28       | $0.002    | $0.056
PFET_STD    | pfet3 | 24       | $0.002    | $0.048
RPOLY_1K    | rpoly | 12       | $0.001    | $0.012
...
                                   TOTAL:    $0.342
```

**價值：**

- 💵 成本估算：精確計算設計成本
- 📋 文件完整：製造所需資訊齊全
- ✅ 驗證：確保沒有遺漏元件

---

### 場景 5：設計規則檢查前置作業

**問題：**
某些設計規則與元件數量有關（例如：總電容數不可超過X）

**解決方案：**
報表生成器 → 預檢查是否符合限制

**檢查範例：**

```
Design Rule Pre-Check:
----------------------
✓ Total transistors: 52 (limit: 100)
✓ Total capacitors: 12 (limit: 20)
✗ Total vias: 254 (limit: 200) ← WARNING!
✓ Total instances: 330 (limit: 500)

Action Required:
- Reduce via count by at least 54
```

**價值：**

- 🛡️ 提早發現問題：避免後期大改
- ⚡ 快速驗證：不用等DRC跑完
- 🎯 精準優化：知道要改哪裡

---

### 場景 6：團隊協作與知識傳遞

**問題：**
新同事接手設計，需要快速了解設計規模

**解決方案：**
附上自動報表 → 一目了然

**團隊報表：**

```
Project: Low-Power ADC
Team: Analog Design Group
Designer: John Doe

Design Summary:
  Blocks: 5 (comparator, sar_logic, dac, buffer, bias)
  Total Instances: 1,247
  Estimated Area: 0.085 mm²
  Power Domains: 2 (AVDD, DVDD)

Detailed per Block:
  comparator: 156 instances
  sar_logic: 423 instances
  dac: 298 instances
  ...
```

**價值：**

- 👥 降低學習曲線：快速掌握設計架構
- 📚 文件化：自動生成設計文件
- 🔄 交接順暢：減少溝通成本

---

## 🔍 深入理解：為什麼是最佳入門專案？

### 技術學習層面

#### 1. 涵蓋SKILL核心概念

```lisp
; ✅ 學習點1: 變數和資料結構
let((cv instList typeCount))

; ✅ 學習點2: 物件存取
cv = geGetEditCellView()
cv~>cellName
cv~>instances

; ✅ 學習點3: 迴圈
foreach(inst cv~>instances
  ; 處理每個instance
)

; ✅ 學習點4: 條件判斷
if(cv 
  then ; 有效
  else ; 無效
)

; ✅ 學習點5: 檔案I/O
port = outfile("report.txt" "w")
fprintf(port "內容\n")
close(port)

; ✅ 學習點6: 錯誤處理
error("No cell view is open!")
```

**一個專案掌握6大核心技能！**

---

#### 2. 立即可見的成果

**傳統學習：**

```
學語法 → 寫程式 → 看不到效果 → 😴 沒動力
```

**這個專案：**

```
寫程式 → 執行 → 看到報表檔案 → 😃 有成就感！
```

**心理學優勢：**

- 🎉 即時回饋：馬上看到結果
- 💪 建立信心：「我做到了！」
- 🚀 持續動力：想加更多功能

---

#### 3. 實用性高，工作即練習

**不是玩具專案，是真正的生產力工具！**

- 每天都會用到 → 重複強化學習
- 同事會借用 → 獲得正面反饋
- 持續改進 → 自然進步

---

### 實際工作價值

#### 時間效益計算

**假設情境：**

- 每週需要檢查設計3次
- 手動統計每次15分鐘
- 一年工作50週

**手動方式：**

```
3次/週 × 15分鐘 × 50週 = 2,250分鐘/年 = 37.5小時/年
```

**自動化後：**

```
3次/週 × 5秒 × 50週 = 750秒/年 = 12.5分鐘/年
```

**節省時間：37.4小時/年** ⏰

**以時薪$30計算：節省 $1,122/年**

---

#### 錯誤減少

**手動統計常見問題：**

- ❌ 數錯（漏數、重複數）
- ❌ 分類錯（把pfet當nfet）
- ❌ 版本混淆（不知道是哪個版本的統計）

**自動化優勢：**

- ✅ 100%準確
- ✅ 永不疲勞
- ✅ 可追溯（時間戳記、版本資訊）

---

## 🎨 擴展可能性

### 初級擴展（1-2天）

1. **加入時間戳記**

```lisp
fprintf(port "Generated: %s\n" getCurrentTime())
```

2. **統計Net數量**

```lisp
fprintf(port "Total Nets: %d\n" length(cv~>nets))
```

3. **計算總面積**

```lisp
fprintf(port "Total Area: %f um²\n" calculateArea(cv))
```

---

### 中級擴展（3-7天）

4. **生成HTML報表**

```lisp
fprintf(port "<html><body>")
fprintf(port "<h1>%s</h1>" cv~>cellName)
fprintf(port "<table border='1'>")
; ... 表格內容
fprintf(port "</table></body></html>")
```

5. **圖表視覺化**

- 使用條形圖顯示元件分佈
- 圓餅圖顯示比例

6. **Email自動發送**

```lisp
system("sendmail manager@company.com < report.txt")
```

---

### 高級擴展（1-2週）

7. **趨勢分析儀表板**

- 儲存歷史數據到資料庫
- 生成趨勢圖表
- 異常檢測（元件數突增？）

8. **多設計批次報表**

```lisp
foreach(design designList
  generateReport(design)
)
; 生成總覽報表
```

9. **與CI/CD整合**

- Git commit後自動生成報表
- 差異過大自動警告

---

## 📖 完整實作教學

### 步驟1：最簡版本（10分鐘）

**目標：** 只輸出cell名稱和instance總數

```lisp
procedure(generateSimpleReport()
  let((cv))
    cv = geGetEditCellView()
    
    if(cv then
      printf("Cell: %s\n" cv~>cellName)
      printf("Total instances: %d\n" length(cv~>instances))
    else
      printf("Error: No cell view is open!\n")
    )
  )
)
```

**測試：**

1. 在Cadence開啟任一Layout
2. 在CIW輸入：`generateSimpleReport()`
3. 看到輸出 → 成功！✅

---

### 步驟2：加入檔案輸出（+20分鐘）

**目標：** 將結果寫入txt檔案

```lisp
procedure(generateReportToFile()
  let((cv port))
    cv = geGetEditCellView()
    
    if(cv then
      ; 開啟檔案
      port = outfile("design_report.txt" "w")
      
      ; 寫入內容
      fprintf(port "=== Design Report ===\n")
      fprintf(port "Cell: %s\n" cv~>cellName)
      fprintf(port "Library: %s\n" cv~>libName)
      fprintf(port "Total instances: %d\n" length(cv~>instances))
      
      ; 關閉檔案
      close(port)
      
      printf("✓ Report saved to: design_report.txt\n")
    else
      error("No cell view is open!")
    )
  )
)
```

**測試：**

1. 執行函數
2. 檢查目錄下是否有 `design_report.txt`
3. 開啟檔案查看內容

---

### 步驟3：統計各類型元件（+30分鐘）

**目標：** 分類統計不同類型的instance

```lisp
procedure(generateDetailedReport()
  let((cv typeCount port))
    cv = geGetEditCellView()
    
    if(cv then
      ; 建立統計表（使用list代替table）
      typeCount = nil
      
      ; 遍歷所有instances
      foreach(inst cv~>instances
        let((cellName found entry))
          cellName = inst~>cellName
          found = nil
          
          ; 查找是否已存在
          foreach(item typeCount
            when(car(item) == cellName
              ; 增加計數
              rplacd(item cadr(item) + 1)
              found = t
            )
          )
          
          ; 如果不存在，新增
          unless(found
            typeCount = cons(list(cellName 1) typeCount)
          )
        )
      )
      
      ; 寫入報表
      port = outfile("design_report.txt" "w")
      fprintf(port "=== Detailed Design Report ===\n")
      fprintf(port "Cell: %s\n" cv~>cellName)
      fprintf(port "Library: %s\n\n" cv~>libName)
      fprintf(port "Instance Statistics:\n")
      fprintf(port "-------------------\n")
      
      ; 輸出統計（已排序）
      typeCount = sortcar(typeCount 'alphalessp)
      foreach(item typeCount
        fprintf(port "%-20s: %4d\n" car(item) cadr(item))
      )
      
      fprintf(port "\nTotal Types: %d\n" length(typeCount))
      fprintf(port "Total Instances: %d\n" length(cv~>instances))
      
      close(port)
      printf("✓ Detailed report generated!\n")
    else
      error("No cell view is open!")
    )
  )
)
```

**測試報表範例輸出：**

```
=== Detailed Design Report ===
Cell: amplifier_core
Library: analog_lib

Instance Statistics:
-------------------
cmom                :    8
mimcap              :    4
nfet3               :   28
pfet3               :   24
rpoly               :   12
via1                :  156
via2                :   98

Total Types: 7
Total Instances: 330
```

---

### 步驟4：加入時間和版本資訊（+15分鐘）

```lisp
; 在報表開頭加入
fprintf(port "Generated: %s\n" getCurrentTime())
fprintf(port "User: %s\n" getShellEnvVar("USER"))
fprintf(port "Hostname: %s\n\n" getShellEnvVar("HOSTNAME"))
```

---

## 🎯 學習目標檢查清單

完成這個專案後，您應該能夠：

### 基礎技能

- [ ] 在CIW中撰寫和執行SKILL程式
- [ ] 使用`let`建立區域變數
- [ ] 使用`if`/`when`/`unless`進行條件判斷
- [ ] 使用`foreach`遍歷列表

### 物件操作

- [ ] 取得當前開啟的cell view
- [ ] 存取cell view的屬性（`~>`運算子）
- [ ] 遍歷instances列表
- [ ] 讀取instance的屬性

### 檔案處理

- [ ] 使用`outfile`開啟檔案
- [ ] 使用`fprintf`格式化寫入
- [ ] 正確關閉檔案

### 資料結構

- [ ] 使用list儲存資料
- [ ] 使用cons新增元素
- [ ] 使用car/cadr存取元素
- [ ] 列表排序（sortcar）

### 除錯技能

- [ ] 使用`printf`輸出除錯訊息
- [ ] 使用`error`產生錯誤
- [ ] 檢查變數是否為nil

---

## 💬 常見問題

### Q1: 報表檔案儲存在哪裡？

**A:** 預設儲存在Cadence的工作目錄，通常是你啟動Cadence的目錄。

**如何指定路徑：**

```lisp
port = outfile("/home/user/reports/design_report.txt" "w")
```

---

### Q2: 如何處理中文名稱？

**A:** SKILL支援UTF-8，但要確保檔案編碼正確：

```lisp
port = outfile("report.txt" "w")
fprintf(port "元件類型: %s\n" "電晶體")
```

---

### Q3: 可以生成Excel格式嗎？

**A:** 可以！生成CSV格式，Excel可直接開啟：

```lisp
port = outfile("report.csv" "w")
fprintf(port "Type,Quantity\n")  ; 標題行
foreach(item typeCount
  fprintf(port "%s,%d\n" car(item) cadr(item))
)
```

---

### Q4: 如何自動化每天生成報表？

**A:** 使用cron job（Linux）或Task Scheduler（Windows）：

**Linux crontab範例：**

```bash
0 18 * * * /tools/cadence/run_report.sh
```

**run_report.sh：**

```bash
#!/bin/bash
virtuoso -nograph -replay report_script.il
```

---

## 🚀 下一步

完成基本版本後，建議：

1. **分享給同事** → 獲得反饋
2. **加入一個擴展功能** → 每週一個小改進
3. **上傳到GitHub** → 建立作品集
4. **開始專案2** → 批次重命名工具

---

## 📊 成功指標

### 1週後

- ✅ 基本報表功能正常
- ✅ 能處理常見錯誤
- ✅ 同事開始使用

### 1個月後

- ✅ 加入3個以上擴展功能
- ✅ 生成HTML/CSV格式
- ✅ 整合到工作流程

### 3個月後

- ✅ 全組都在使用
- ✅ 節省可觀的時間
- ✅ SKILL能力顯著提升

---

**記住：最好的學習方式就是實際動手做！現在就開始你的第一個SKILL專案吧！** 🎉
