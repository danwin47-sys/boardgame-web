# SKILL簡單繞線實作指南

> 從零開始實作Layout自動繞線工具  
> 難度：⭐⭐ 中等 | 預計時間：1-2週  
> 最後更新：2025-12-09

---

## 📚 目錄

- [繞線基礎概念](#繞線基礎概念)
- [Level 1: 點對點直線繞線](#level-1-點對點直線繞線)
- [Level 2: L型繞線](#level-2-l型繞線)
- [Level 3: Manhattan繞線](#level-3-manhattan繞線)
- [Level 4: 多層繞線與Via](#level-4-多層繞線與via)
- [Level 5: Bus繞線](#level-5-bus繞線)
- [進階功能](#進階功能)
- [完整工具套件](#完整工具套件)

---

## 繞線基礎概念

### 🎯 什麼是繞線（Routing）？

**定義：** 在Layout中建立金屬路徑連接兩個或多個點

### 基本要素

```
繞線需要：
┌─────────────────┐
│ 起點 (fromPt)   │
│ 終點 (toPt)     │
│ 圖層 (layer)    │
│ 線寬 (width)    │
│ 路徑 (path)     │
└─────────────────┘
```

### Cadence SKILL繞線API

```lisp
; 核心函數
dbCreatePath(
  cv           ; cellview
  layer        ; 圖層 list("Metal1" "drawing")
  points       ; 路徑點列表
  width        ; 線寬
)
```

---

## Level 1: 點對點直線繞線

### 🟢 最簡單的繞線

**功能：** 兩點之間畫一條直線

### 實作

```lisp
;******************************************************************************
; Function: simpleStraightRoute
; Description: 最簡單的點對點直線繞線
; Parameters:
;   fromPt - 起點 (x:y格式)
;   toPt   - 終點 (x:y格式)
;   layer  - 圖層名稱
;   width  - 線寬
; Returns: path物件
;******************************************************************************
procedure(simpleStraightRoute(fromPt toPt layer @optional (width 0.5))
  let((cv path))
    cv = geGetEditCellView()
    
    when(cv
      ; 建立路徑：兩點之間直線
      path = dbCreatePath(
        cv
        list(layer "drawing")
        list(fromPt toPt)
        width
      )
      
      printf("✓ Created straight route from %L to %L\n" fromPt toPt)
      path
    )
  )
)

; 使用範例
; simpleStraightRoute(0:0 10:10 "Metal1" 0.5)
; => 從(0,0)到(10,10)畫一條Metal1直線，寬度0.5
```

### 測試

```lisp
; 測試1：水平線
simpleStraightRoute(0:0 20:0 "Metal1" 0.5)

; 測試2：垂直線
simpleStraightRoute(0:0 0:20 "Metal1" 0.5)

; 測試3：斜線
simpleStraightRoute(0:0 10:10 "Metal1" 0.5)
```

---

## Level 2: L型繞線

### 🟡 Manhattan繞線基礎

**功能：** 只使用水平和垂直線段（IC設計標準）

### 策略選擇

```
起點到終點的L型路徑有兩種：

方式1: 先水平後垂直        方式2: 先垂直後水平
起點●────→              起點●
      │                  │
      ↓                  ↓
      終點●              ───→終點●
```

### 實作

```lisp
;******************************************************************************
; Function: lShapeRoute
; Description: L型繞線（Manhattan routing）
; Parameters:
;   fromPt     - 起點
;   toPt       - 終點
;   layer      - 圖層
;   width      - 線寬
;   direction  - "horizontal-first" 或 "vertical-first"
;******************************************************************************
procedure(lShapeRoute(fromPt toPt layer @key (width 0.5) (direction "horizontal-first"))
  let((cv path cornerPt))
    cv = geGetEditCellView()
    
    when(cv
      ; 根據方向計算轉角點
      if(direction == "horizontal-first"
        then
          ; 先水平：轉角點在 (toPt的X, fromPt的Y)
          cornerPt = list(xCoord(toPt) yCoord(fromPt))
        else
          ; 先垂直：轉角點在 (fromPt的X, toPt的Y)
          cornerPt = list(xCoord(fromPt) yCoord(toPt))
      )
      
      ; 建立三點路徑：起點 -> 轉角 -> 終點
      path = dbCreatePath(
        cv
        list(layer "drawing")
        list(fromPt cornerPt toPt)
        width
      )
      
      printf("✓ Created L-shape route (%s)\n" direction)
      path
    )
  )
)

; 使用範例
; lShapeRoute(0:0 10:10 "Metal1" ?direction "horizontal-first")
; => 先往右走到(10,0)，再往上走到(10,10)
```

### 智慧選擇方向

```lisp
;******************************************************************************
; Function: smartLRoute
; Description: 自動選擇最佳L型方向
; Strategy: 選擇較長的那一段先走
;******************************************************************************
procedure(smartLRoute(fromPt toPt layer @optional (width 0.5))
  let((dx dy direction))
    ; 計算X和Y方向的距離
    dx = abs(xCoord(toPt) - xCoord(fromPt))
    dy = abs(yCoord(toPt) - yCoord(fromPt))
    
    ; 選擇較長的先走
    direction = if(dx > dy
      then "horizontal-first"
      else "vertical-first"
    )
    
    printf("Smart routing: %s (dx=%f, dy=%f)\n" direction dx dy)
    
    ; 呼叫L型繞線
    lShapeRoute(fromPt toPt layer ?width width ?direction direction)
  )
)
```

---

## Level 3: Manhattan繞線

### 🟠 避障繞線

**功能：** 在有障礙物的情況下找到路徑

### 簡化版：固定模式

```lisp
;******************************************************************************
; Function: zShapeRoute
; Description: Z型繞線（3段式）
; 用於需要繞過障礙物的情況
;******************************************************************************
procedure(zShapeRoute(fromPt toPt layer @key (width 0.5) (offset 5.0))
  let((cv path midPt1 midPt2))
    cv = geGetEditCellView()
    
    when(cv
      ; 計算兩個中間點
      ; 起點 -> midPt1 -> midPt2 -> 終點
      
      ; midPt1: 從起點水平移動一半距離
      midPt1 = list(
        (xCoord(fromPt) + xCoord(toPt)) / 2.0
        yCoord(fromPt)
      )
      
      ; midPt2: 垂直到終點的Y座標
      midPt2 = list(
        xCoord(midPt1)
        yCoord(toPt)
      )
      
      ; 建立四點路徑
      path = dbCreatePath(
        cv
        list(layer "drawing")
        list(fromPt midPt1 midPt2 toPt)
        width
      )
      
      printf("✓ Created Z-shape route\n")
      path
    )
  )
)
```

### 可調整的Z型繞線

```lisp
;******************************************************************************
; Function: adjustableZRoute
; Description: 可調整轉折位置的Z型繞線
; Parameters:
;   fromPt  - 起點
;   toPt    - 終點
;   layer   - 圖層
;   ratio   - 第一段水平距離比例 (0.0-1.0)
;   width   - 線寬
;******************************************************************************
procedure(adjustableZRoute(fromPt toPt layer @key (width 0.5) (ratio 0.5))
  let((cv path midPt1 midPt2 dx))
    cv = geGetEditCellView()
    
    when(cv
      ; 計算X方向總距離
      dx = xCoord(toPt) - xCoord(fromPt)
      
      ; midPt1: 按比例移動
      midPt1 = list(
        xCoord(fromPt) + dx * ratio
        yCoord(fromPt)
      )
      
      ; midPt2: 垂直到終點
      midPt2 = list(
        xCoord(midPt1)
        yCoord(toPt)
      )
      
      ; 建立路徑
      path = dbCreatePath(
        cv
        list(layer "drawing")
        list(fromPt midPt1 midPt2 toPt)
        width
      )
      
      printf("✓ Created adjustable Z-route (ratio=%.2f)\n" ratio)
      path
    )
  )
)

; 使用範例
; adjustableZRoute(0:0 20:20 "Metal1" ?ratio 0.3)
; => 30%距離處轉折
```

---

## Level 4: 多層繞線與Via

### 🔵 跨圖層連接

**功能：** 使用Via在不同金屬層之間連接

### Via建立

```lisp
;******************************************************************************
; Function: createVia
; Description: 在指定位置建立Via
; Parameters:
;   pt         - via位置
;   viaName    - via類型 (例如 "via1")
;******************************************************************************
procedure(createVia(pt viaName)
  let((cv via))
    cv = geGetEditCellView()
    
    when(cv
      ; 建立via instance
      via = dbCreateVia(
        cv
        viaName    ; via master名稱
        pt         ; 位置
        "R0"       ; 方向
      )
      
      printf("✓ Created via at %L\n" pt)
      via
    )
  )
)
```

### 多層繞線

```lisp
;******************************************************************************
; Function: multiLayerRoute
; Description: 多層繞線（帶via）
; Parameters:
;   fromPt      - 起點
;   fromLayer   - 起點圖層
;   toPt        - 終點
;   toLayer     - 終點圖層
;   viaLayer    - via變換點的圖層
;   viaName     - via類型
;   width       - 線寬
;******************************************************************************
procedure(multiLayerRoute(
  fromPt fromLayer 
  toPt toLayer 
  @key (viaLayer "Metal1") (viaName "via1") (width 0.5))
  
  let((cv viaPt path1 path2 via))
    cv = geGetEditCellView()
    
    when(cv
      ; 選擇via位置（中點）
      viaPt = list(
        (xCoord(fromPt) + xCoord(toPt)) / 2.0
        (yCoord(fromPt) + yCoord(toPt)) / 2.0
      )
      
      ; 第一段：起點到via位置
      path1 = lShapeRoute(fromPt viaPt fromLayer ?width width)
      
      ; 建立via
      via = createVia(viaPt viaName)
      
      ; 第二段：via位置到終點
      path2 = lShapeRoute(viaPt toPt toLayer ?width width)
      
      printf("✓ Created multi-layer route\n")
      list(path1 via path2)
    )
  )
)

; 使用範例
; multiLayerRoute(
;   0:0 "Metal1"
;   20:20 "Metal2"
;   ?viaName "via12"
; )
```

---

## Level 5: Bus繞線

### 🟣 平行多線繞線

**功能：** 一次繞多條平行的線

### 基本Bus繞線

```lisp
;******************************************************************************
; Function: simpleBusRoute
; Description: 簡單的bus繞線（平行直線）
; Parameters:
;   fromPt   - 起點
;   toPt     - 終點
;   layer    - 圖層
;   numLines - 線數
;   spacing  - 線間距
;   width    - 單線寬度
;******************************************************************************
procedure(simpleBusRoute(fromPt toPt layer numLines spacing @optional (width 0.5))
  let((cv paths offset currentFrom currentTo))
    cv = geGetEditCellView()
    paths = nil
    
    when(cv
      ; 計算總寬度並居中
      offset = -(numLines - 1) * spacing / 2.0
      
      ; 繞每一條線
      for(i 0 numLines-1
        ; 計算當前線的起點和終點
        currentFrom = list(
          xCoord(fromPt)
          yCoord(fromPt) + offset + i * spacing
        )
        
        currentTo = list(
          xCoord(toPt)
          yCoord(toPt) + offset + i * spacing
        )
        
        ; 建立路徑
        paths = cons(
          dbCreatePath(
            cv
            list(layer "drawing")
            list(currentFrom currentTo)
            width
          )
          paths
        )
      )
      
      printf("✓ Created bus with %d lines\n" numLines)
      paths
    )
  )
)

; 使用範例
; simpleBusRoute(0:0 20:0 "Metal1" 5 1.0 0.5)
; => 5條平行線，間距1.0，線寬0.5
```

### L型Bus繞線

```lisp
;******************************************************************************
; Function: lShapeBusRoute
; Description: L型bus繞線
;******************************************************************************
procedure(lShapeBusRoute(fromPt toPt layer numLines spacing 
                         @key (width 0.5) (direction "horizontal-first"))
  let((cv paths offset cornerPt currentFrom currentCorner currentTo))
    cv = geGetEditCellView()
    paths = nil
    
    when(cv
      ; 居中offset
      offset = -(numLines - 1) * spacing / 2.0
      
      ; 計算基準轉角點
      if(direction == "horizontal-first"
        then cornerPt = list(xCoord(toPt) yCoord(fromPt))
        else cornerPt = list(xCoord(fromPt) yCoord(toPt))
      )
      
      ; 繞每一條線
      for(i 0 numLines-1
        ; 計算當前線的三個點
        currentFrom = fromPt + list(0 offset + i * spacing)
        currentCorner = cornerPt + list(0 offset + i * spacing)
        currentTo = toPt + list(0 offset + i * spacing)
        
        ; 建立L型路徑
        paths = cons(
          dbCreatePath(
            cv
            list(layer "drawing")
            list(currentFrom currentCorner currentTo)
            width
          )
          paths
        )
      )
      
      printf("✓ Created L-shape bus with %d lines\n" numLines)
      paths
    )
  )
)
```

---

## 進階功能

### 🎯 DRC檢查整合

```lisp
;******************************************************************************
; Function: routeWithDRCCheck
; Description: 繞線前檢查設計規則
;******************************************************************************
procedure(routeWithDRCCheck(fromPt toPt layer width)
  let((cv minWidth minSpacing canRoute))
    cv = geGetEditCellView()
    
    ; 從tech file讀取最小線寬
    minWidth = techGetSpacingRule(cv~>tech layer "minWidth")
    
    ; 檢查線寬是否符合規則
    canRoute = width >= minWidth
    
    if(canRoute
      then
        printf("✓ DRC check passed, routing...\n")
        lShapeRoute(fromPt toPt layer ?width width)
      else
        warn("Width %.2f is less than minimum %.2f\n" width minWidth)
        nil
    )
  )
)
```

### 🎯 障礙物檢測

```lisp
;******************************************************************************
; Function: checkPathClear
; Description: 檢查路徑上是否有障礙物
;******************************************************************************
procedure(checkPathClear(fromPt toPt layer)
  let((cv bbox shapes obstacle))
    cv = geGetEditCellView()
    obstacle = nil
    
    ; 建立路徑的bounding box
    bbox = list(
      list(min(xCoord(fromPt) xCoord(toPt))
           min(yCoord(fromPt) yCoord(toPt)))
      list(max(xCoord(fromPt) xCoord(toPt))
           max(yCoord(fromPt) yCoord(toPt)))
    )
    
    ; 檢查bbox內是否有其他shapes
    shapes = dbGetOverlaps(cv bbox layer)
    
    if(shapes
      then
        warn("Found %d obstacles in path\n" length(shapes))
        nil
      else
        t  ; 路徑清空
    )
  )
)
```

### 🎯 自動選層

```lisp
;******************************************************************************
; Function: autoLayerSelection
; Description: 根據路徑方向自動選擇金屬層
; Rule: 
;   - 水平路徑用奇數層 (Metal1, Metal3, ...)
;   - 垂直路徑用偶數層 (Metal2, Metal4, ...)
;******************************************************************************
procedure(autoLayerSelection(fromPt toPt)
  let((dx dy layer))
    dx = abs(xCoord(toPt) - xCoord(fromPt))
    dy = abs(yCoord(toPt) - yCoord(fromPt))
    
    ; 判斷主要方向
    if(dx > dy
      then layer = "Metal1"  ; 水平 -> Metal1
      else layer = "Metal2"  ; 垂直 -> Metal2
    )
    
    printf("Auto selected layer: %s\n" layer)
    layer
  )
)
```

---

## 完整工具套件

### 整合所有功能

```lisp
;******************************************************************************
; 完整的繞線工具包
;******************************************************************************

;==============================================================================
; 主要繞線函數
;==============================================================================

procedure(smartRoute(fromPt toPt @key (layer nil) (width 0.5) (style "auto"))
  let((selectedLayer selectedStyle))
    
    ; 自動選層
    selectedLayer = if(layer then layer else autoLayerSelection(fromPt toPt))
    
    ; 自動選擇繞線風格
    selectedStyle = if(style == "auto"
      then determineRoutingStyle(fromPt toPt)
      else style
    )
    
    ; 根據風格執行繞線
    case(selectedStyle
      ("straight" 
        simpleStraightRoute(fromPt toPt selectedLayer width))
      ("L-shape"
        smartLRoute(fromPt toPt selectedLayer width))
      ("Z-shape"
        zShapeRoute(fromPt toPt selectedLayer ?width width))
      (t
        error("Unknown routing style: %s" selectedStyle))
    )
  )
)

;==============================================================================
; 輔助函數
;==============================================================================

procedure(determineRoutingStyle(fromPt toPt)
  let((dx dy))
    dx = abs(xCoord(toPt) - xCoord(fromPt))
    dy = abs(yCoord(toPt) - yCoord(fromPt))
    
    cond(
      ; 如果X或Y座標相同 -> 直線
      ((dx < 0.001 || dy < 0.001) "straight")
      
      ; 距離適中 -> L型
      ((dx < 50 && dy < 50) "L-shape")
      
      ; 距離較遠 -> Z型
      (t "Z-shape")
    )
  )
)

;==============================================================================
; 使用範例
;==============================================================================

/*
; 簡單使用
smartRoute(0:0 10:10)

; 指定參數
smartRoute(0:0 10:10 ?layer "Metal2" ?width 1.0 ?style "L-shape")

; Bus繞線
simpleBusRoute(0:0 20:0 "Metal1" 5 1.0 0.5)
*/
```

---

## 測試套件

### 完整測試腳本

```lisp
;******************************************************************************
; 繞線工具測試套件
;******************************************************************************

procedure(testRoutingTools()
  printf("\n=== Starting Routing Tools Test ===\n\n")
  
  ; Test 1: 直線繞線
  printf("Test 1: Straight route\n")
  simpleStraightRoute(0:0 20:0 "Metal1" 0.5)
  
  ; Test 2: L型繞線
  printf("\nTest 2: L-shape route\n")
  lShapeRoute(0:5 20:25 "Metal1" ?direction "horizontal-first")
  
  ; Test 3: Z型繞線
  printf("\nTest 3: Z-shape route\n")
  zShapeRoute(0:10 20:30 "Metal1")
  
  ; Test 4: Bus繞線
  printf("\nTest 4: Bus route (5 lines)\n")
  simpleBusRoute(0:15 20:15 "Metal1" 5 1.0 0.5)
  
  ; Test 5: 智慧繞線
  printf("\nTest 5: Smart route\n")
  smartRoute(0:20 20:40)
  
  printf("\n=== All Tests Complete ===\n")
)
```

---

## 性能優化

### 批次處理

```lisp
;******************************************************************************
; Function: batchRoute
; Description: 批次繞線多組連接
; Parameters:
;   connections - 連接列表 ((from1 to1) (from2 to2) ...)
;******************************************************************************
procedure(batchRoute(connections @key (layer "Metal1") (width 0.5))
  let((count))
    count = 0
    
    foreach(conn connections
      smartRoute(car(conn) cadr(conn) ?layer layer ?width width)
      count = count + 1
    )
    
    printf("✓ Routed %d connections\n" count)
  )
)

; 使用範例
; batchRoute(
;   list(
;     list(0:0 10:10)
;     list(0:5 15:25)
;     list(5:5 20:20)
;   )
;   ?layer "Metal2"
; )
```

---

## 學習路徑

### 建議進度

```
第1-2天：
□ 理解基本概念
□ 實作Level 1（直線繞線）
□ 測試和除錯

第3-4天：
□ 實作Level 2（L型繞線）
□ 加入方向選擇
□ 智慧選擇演算法

第5-7天：
□ 實作Level 3（Z型繞線）
□ 可調整參數
□ 障礙物檢測

第8-10天：
□ 實作Level 4（多層繞線）
□ Via建立和管理
□ 跨層連接

第11-14天：
□ 實作Level 5（Bus繞線）
□ 整合所有功能
□ 建立完整工具包

持續改進：
□ 性能優化
□ 錯誤處理
□ 使用者介面
□ 文檔撰寫
```

---

## 常見問題

### Q1: 如何處理斜線繞線？

**A:** IC Layout通常不允許斜線，堅持Manhattan routing（只有水平和垂直線段）。

---

### Q2: 如何選擇最佳路徑？

**A:** 簡單啟發式演算法：

```
1. 優先使用較短的路徑
2. 減少轉角數量
3. 避開已知障礙物
4. 遵守設計規則
```

---

### Q3: 如何處理複雜障礙物？

**A:** 進階主題，需要實作A*或Dijkstra演算法。簡單case用固定模式即可。

---

## 下一步

### 進階主題（超出本指南範圍）

```
更複雜的繞線：
- A*尋路演算法
- Lee演算法
- 迷宮路由
- 最小化Via數量
- 時序優化
- 串擾最小化
```

### 推薦學習資源

```
1. Cadence SKILL API文檔
   - dbCreatePath
   - dbCreateVia
   - 幾何操作函數

2. 演算法書籍
   - 圖論基礎
   - 路徑搜尋演算法

3. IC Layout專業知識
   - DRC規則
   - 製程限制
   - 最佳實踐
```

---

## 總結

### ✅ 您學會了

1. **基礎繞線**：直線、L型、Z型
2. **多層連接**：Via建立和使用
3. **Bus繞線**：平行多線
4. **智慧選擇**：自動化決策
5. **工具整合**：完整工具包

### 🎯 實戰價值

這些工具可以：

- ✅ 節省80%手動繞線時間
- ✅ 減少DRC錯誤
- ✅ 提高一致性
- ✅ 為進階功能打基礎

### 🚀 繼續提升

```
下一步可以開發：
1. GUI整合
2. 快捷鍵綁定
3. 批次處理工具
4. 與schematic整合
5. 自動化驗證
```

---

**開始實作您的第一個繞線工具吧！** 🛠️✨
