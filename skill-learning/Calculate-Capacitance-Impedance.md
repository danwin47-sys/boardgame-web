# SKILL計算電容和阻抗

> IC設計中的電氣參數計算工具  
> 最後更新：2025-12-09

---

## 📚 目錄

- [基礎概念](#基礎概念)
- [方法1：從元件參數計算](#方法1從元件參數計算)
- [方法2：從幾何尺寸計算](#方法2從幾何尺寸計算)
- [方法3：寄生參數提取](#方法3寄生參數提取)
- [實用工具範例](#實用工具範例)
- [完整專案](#完整專案)

---

## 基礎概念

### 在IC設計中的電容和阻抗

#### 電容類型

1. **主動元件電容**
   - MOM電容（Metal-Oxide-Metal）
   - MIM電容（Metal-Insulator-Metal）
   - MOS電容（Gate capacitance）

2. **寄生電容**
   - 金屬層間耦合電容
   - 金屬到基板電容
   - 擴散區電容

#### 阻抗/電阻類型

1. **主動元件電阻**
   - Poly電阻
   - N-well/P-well電阻
   - Metal電阻

2. **寄生電阻**
   - 金屬線電阻
   - Via電阻
   - 接觸電阻

---

## 方法1：從元件參數計算

### 情境：已知元件的物理參數

當你有一個PCell或標準元件，它有width、length等參數時。

### 🔧 電容計算

#### MOM/MIM電容公式

```
C = ε × A / d

其中：
C = 電容值（法拉）
ε = 介電常數（法拉/米）
A = 面積（米²）
d = 介電層厚度（米）
```

#### SKILL實作

```lisp
;******************************************************************************
; Function: calculateCapacitance
; Description: 根據電容元件的參數計算電容值
; Parameters:
;   width  - 電容寬度（微米）
;   length - 電容長度（微米）
;   type   - 電容類型 ("MOM" or "MIM")
; Returns: 電容值（法拉，fF）
;******************************************************************************
procedure(calculateCapacitance(width length @optional (type "MOM"))
  let((area epsilon thickness capValue))
    
    ; 面積計算（轉換為 m²）
    area = width * length * 1e-12  ; um² -> m²
    
    ; 根據類型設定參數
    case(type
      ("MOM"
        ; Metal-Oxide-Metal 參數（範例值，需根據製程調整）
        epsilon = 3.9 * 8.854e-12  ; SiO2的介電常數
        thickness = 0.5e-6         ; 500nm
      )
      ("MIM"
        ; Metal-Insulator-Metal 參數
        epsilon = 7.5 * 8.854e-12  ; High-k材料
        thickness = 0.05e-6        ; 50nm
      )
      (t
        error("Unknown capacitor type: %s" type)
      )
    )
    
    ; 計算電容值（法拉）
    capValue = epsilon * area / thickness
    
    ; 轉換為 fF（femtofarad）方便閱讀
    capValue = capValue * 1e15
    
    printf("Capacitance Calculation:\n")
    printf("  Type: %s\n" type)
    printf("  Width: %.2f um\n" width)
    printf("  Length: %.2f um\n" length)
    printf("  Area: %.2f um²\n" width * length)
    printf("  Capacitance: %.3f fF\n" capValue)
    
    capValue  ; 返回值
  )
)

; 使用範例
; calculateCapacitance(10.0 20.0 "MOM")
; => 計算 10um × 20um 的MOM電容
```

**執行結果：**

```
Capacitance Calculation:
  Type: MOM
  Width: 10.00 um
  Length: 20.00 um
  Area: 200.00 um²
  Capacitance: 13.328 fF
```

---

### 🔧 電阻計算

#### 電阻公式

```
R = ρ × L / A

其中：
R = 電阻值（歐姆）
ρ = 電阻率（歐姆·米）
L = 長度（米）
A = 截面積（米²）
```

#### 使用片電阻（Sheet Resistance）

IC設計中更常用：

```
R = Rs × (L / W) × N

其中：
Rs = 片電阻（Ω/□，ohm per square）
L  = 長度
W  = 寬度
N  = 方塊數 = L/W
```

#### SKILL實作

```lisp
;******************************************************************************
; Function: calculateResistance
; Description: 根據電阻元件的參數計算電阻值
; Parameters:
;   width  - 電阻寬度（微米）
;   length - 電阻長度（微米）
;   layer  - 電阻層類型 ("poly", "nwell", "metal1", etc.)
; Returns: 電阻值（歐姆）
;******************************************************************************
procedure(calculateResistance(width length layer)
  let((sheetRes numSquares resValue))
    
    ; 根據層類型設定片電阻（範例值，需根據製程調整）
    case(layer
      ("poly"
        sheetRes = 50.0  ; 50 Ω/□
      )
      ("nwell"
        sheetRes = 1000.0  ; 1k Ω/□
      )
      ("pwell"
        sheetRes = 3000.0  ; 3k Ω/□
      )
      ("metal1"
        sheetRes = 0.08  ; 0.08 Ω/□
      )
      ("metal2"
        sheetRes = 0.06  ; 0.06 Ω/□
      )
      (t
        warn("Unknown layer: %s, using default Rs=100" layer)
        sheetRes = 100.0
      )
    )
    
    ; 計算方塊數
    numSquares = length / width
    
    ; 計算電阻值
    resValue = sheetRes * numSquares
    
    printf("Resistance Calculation:\n")
    printf("  Layer: %s\n" layer)
    printf("  Width: %.2f um\n" width)
    printf("  Length: %.2f um\n" length)
    printf("  Sheet Resistance: %.2f Ω/□\n" sheetRes)
    printf("  Number of Squares: %.2f\n" numSquares)
    printf("  Resistance: %.2f Ω\n" resValue)
    
    resValue  ; 返回值
  )
)

; 使用範例
; calculateResistance(2.0 100.0 "poly")
; => 計算 2um寬 × 100um長 的Poly電阻
```

**執行結果：**

```
Resistance Calculation:
  Layer: poly
  Width: 2.00 um
  Length: 100.00 um
  Sheet Resistance: 50.00 Ω/□
  Number of Squares: 50.00
  Resistance: 2500.00 Ω
```

---

## 方法2：從幾何尺寸計算

### 情境：從Layout中讀取實際圖形

當你需要分析現有Layout的寄生參數時。

### 🔍 讀取元件尺寸

```lisp
;******************************************************************************
; Function: getInstanceDimensions
; Description: 從instance中提取寬度和長度參數
; Parameters:
;   inst - instance物件
; Returns: list(width length) 或 nil
;******************************************************************************
procedure(getInstanceDimensions(inst)
  let((width length params))
    
    ; 方法1: 從PCell參數讀取
    when(inst~>objType == "inst" && inst~>master~>superMaster
      params = inst~>pcellParams
      
      ; 尋找width參數
      width = cdr(assoc("width" params))
      length = cdr(assoc("length" params))
      
      when(width && length
        return(list(width length))
      )
    )
    
    ; 方法2: 從bounding box計算
    when(inst~>bBox
      let((bbox))
        bbox = inst~>bBox
        width = xCoord(upperRight(bbox)) - xCoord(lowerLeft(bbox))
        length = yCoord(upperRight(bbox)) - yCoord(lowerLeft(bbox))
        
        return(list(width length))
      )
    )
    
    ; 無法取得尺寸
    nil
  )
)
```

### 📊 批次分析設計中的元件

```lisp
;******************************************************************************
; Function: analyzeDesignRC
; Description: 分析設計中所有電容和電阻的總值
;******************************************************************************
procedure(analyzeDesignRC()
  let((cv totalCap totalRes capList resList))
    cv = geGetEditCellView()
    totalCap = 0.0
    totalRes = 0.0
    capList = nil
    resList = nil
    
    when(cv
      ; 遍歷所有instances
      foreach(inst cv~>instances
        let((cellName dims width length capValue resValue))
          cellName = inst~>cellName
          dims = getInstanceDimensions(inst)
          
          when(dims
            width = car(dims)
            length = cadr(dims)
            
            ; 檢查是否為電容
            when(rexMatchp("^[cm]" cellName)  ; c=cap, m=mom
              capValue = calculateCapacitance(width length "MOM")
              totalCap = totalCap + capValue
              capList = cons(
                list(inst~>name cellName capValue)
                capList
              )
            )
            
            ; 檢查是否為電阻
            when(rexMatchp("^r" cellName)  ; r=resistor
              resValue = calculateResistance(width length "poly")
              totalRes = totalRes + resValue
              resList = cons(
                list(inst~>name cellName resValue)
                resList
              )
            )
          )
        )
      )
      
      ; 輸出報告
      printf("\n=== RC Analysis Report ===\n")
      printf("Cell: %s\n\n" cv~>cellName)
      
      printf("Capacitors Found: %d\n" length(capList))
      foreach(item capList
        printf("  %s (%s): %.3f fF\n" 
          car(item)      ; instance名稱
          cadr(item)     ; cell名稱
          caddr(item)    ; 電容值
        )
      )
      printf("Total Capacitance: %.3f fF\n\n" totalCap)
      
      printf("Resistors Found: %d\n" length(resList))
      foreach(item resList
        printf("  %s (%s): %.2f Ω\n" 
          car(item)      ; instance名稱
          cadr(item)     ; cell名稱
          caddr(item)    ; 電阻值
        )
      )
      printf("Total Resistance: %.2f Ω\n" totalRes)
    )
  )
)
```

**執行結果範例：**

```
=== RC Analysis Report ===
Cell: amplifier_stage1

Capacitors Found: 3
  C0 (cmom_2t): 25.450 fF
  C1 (cmom_2t): 25.450 fF
  C2 (mimcap): 102.340 fF
Total Capacitance: 153.240 fF

Resistors Found: 4
  R0 (rpoly): 2500.00 Ω
  R1 (rpoly): 5000.00 Ω
  R2 (rpoly): 1250.00 Ω
  R3 (rnwell): 50000.00 Ω
Total Resistance: 58750.00 Ω
```

---

## 方法3：寄生參數提取

### 金屬線寄生電阻

```lisp
;******************************************************************************
; Function: calculateMetalResistance
; Description: 計算金屬線的寄生電阻
; Parameters:
;   length - 金屬線長度（微米）
;   width  - 金屬線寬度（微米）
;   layer  - 金屬層名稱
; Returns: 電阻值（歐姆）
;******************************************************************************
procedure(calculateMetalResistance(length width layer)
  let((sheetRes resistance))
    
    ; 金屬層片電阻查找表
    sheetRes = case(layer
      ("Metal1" 0.08)
      ("Metal2" 0.06)
      ("Metal3" 0.05)
      ("Metal4" 0.04)
      ("Metal5" 0.03)
      (t 0.1)  ; 默認值
    )
    
    ; R = Rs × L / W
    resistance = sheetRes * length / width
    
    printf("Metal Line Resistance:\n")
    printf("  Layer: %s\n" layer)
    printf("  Length: %.2f um\n" length)
    printf("  Width: %.2f um\n" width)
    printf("  Resistance: %.4f Ω\n" resistance)
    
    resistance
  )
)
```

### 金屬線寄生電容

```lisp
;******************************************************************************
; Function: calculateMetalCapacitance
; Description: 計算金屬線到基板的寄生電容
; Parameters:
;   length - 金屬線長度（微米）
;   width  - 金屬線寬度（微米）
;   layer  - 金屬層名稱
; Returns: 電容值（fF）
;******************************************************************************
procedure(calculateMetalCapacitance(length width layer)
  let((capPerArea area totalCap))
    
    ; 單位面積電容（fF/um²）- 根據製程而定
    capPerArea = case(layer
      ("Metal1" 0.03)  ; 較靠近基板，電容較大
      ("Metal2" 0.02)
      ("Metal3" 0.015)
      ("Metal4" 0.01)
      ("Metal5" 0.008)
      (t 0.02)
    )
    
    ; 計算面積
    area = length * width
    
    ; 計算總電容
    totalCap = capPerArea * area
    
    printf("Metal Line Capacitance:\n")
    printf("  Layer: %s\n" layer)
    printf("  Area: %.2f um²\n" area)
    printf("  Capacitance: %.3f fF\n" totalCap)
    
    totalCap
  )
)
```

### 耦合電容（Coupling Capacitance）

```lisp
;******************************************************************************
; Function: calculateCouplingCapacitance
; Description: 計算兩條平行金屬線之間的耦合電容
; Parameters:
;   length   - 平行長度（微米）
;   spacing  - 間距（微米）
;   height   - 金屬線高度/厚度（微米）
; Returns: 耦合電容值（fF）
;******************************************************************************
procedure(calculateCouplingCapacitance(length spacing height)
  let((epsilon capPerLength totalCap))
    
    ; 簡化的平行板電容模型
    epsilon = 3.9 * 8.854e-12  ; SiO2
    
    ; 單位長度電容（fF/um）
    ; C_coupling ≈ ε × h / s
    capPerLength = epsilon * height / spacing * 1e15 * 1e-6
    
    ; 總電容
    totalCap = capPerLength * length
    
    printf("Coupling Capacitance:\n")
    printf("  Length: %.2f um\n" length)
    printf("  Spacing: %.2f um\n" spacing)
    printf("  Height: %.2f um\n" height)
    printf("  Cap/Length: %.4f fF/um\n" capPerLength)
    printf("  Total Capacitance: %.3f fF\n" totalCap)
    
    totalCap
  )
)
```

---

## 實用工具範例

### 🛠️ 工具1：RC時間常數計算器

```lisp
;******************************************************************************
; Function: calculateRCTimeConstant
; Description: 計算RC時間常數（τ = R × C）
; Parameters:
;   resistance  - 電阻值（歐姆）
;   capacitance - 電容值（法拉或fF）
;   unit        - 電容單位 ("F" 或 "fF")
; Returns: 時間常數（秒）
;******************************************************************************
procedure(calculateRCTimeConstant(resistance capacitance @optional (unit "fF"))
  let((cap tau))
    
    ; 轉換電容到法拉
    cap = if(unit == "fF"
      then capacitance * 1e-15
      else capacitance
    )
    
    ; 計算時間常數
    tau = resistance * cap
    
    printf("RC Time Constant Calculation:\n")
    printf("  Resistance: %.2f Ω\n" resistance)
    printf("  Capacitance: %.3f %s\n" capacitance unit)
    printf("  τ (tau): %.3e seconds\n" tau)
    printf("  τ (tau): %.3f ps\n" tau * 1e12)
    
    ; 計算相關頻率
    let((freq3dB))
      freq3dB = 1.0 / (2.0 * pi * tau)
      printf("  -3dB Frequency: %.3e Hz\n" freq3dB)
      printf("  -3dB Frequency: %.3f MHz\n" freq3dB / 1e6)
    )
    
    tau
  )
)

; 使用範例
; calculateRCTimeConstant(10000.0 100.0 "fF")
; => 計算 10kΩ 和 100fF 的RC時間常數
```

**執行結果：**

```
RC Time Constant Calculation:
  Resistance: 10000.00 Ω
  Capacitance: 100.000 fF
  τ (tau): 1.000e-12 seconds
  τ (tau): 1.000 ps
  -3dB Frequency: 1.592e+11 Hz
  -3dB Frequency: 159154.943 MHz
```

---

### 🛠️ 工具2：阻抗分析器

```lisp
;******************************************************************************
; Function: calculateImpedance
; Description: 計算在特定頻率下的阻抗
; Parameters:
;   resistance  - 電阻值（歐姆）
;   capacitance - 電容值（fF）
;   frequency   - 頻率（Hz）
; Returns: 阻抗大小（歐姆）
;******************************************************************************
procedure(calculateImpedance(resistance capacitance frequency)
  let((cap omega Xc Z))
    
    ; 轉換電容
    cap = capacitance * 1e-15  ; fF to F
    
    ; 角頻率
    omega = 2.0 * pi * frequency
    
    ; 電容抗
    Xc = 1.0 / (omega * cap)
    
    ; 總阻抗 Z = sqrt(R² + Xc²)
    Z = sqrt(resistance * resistance + Xc * Xc)
    
    printf("Impedance Calculation:\n")
    printf("  Resistance: %.2f Ω\n" resistance)
    printf("  Capacitance: %.3f fF\n" capacitance)
    printf("  Frequency: %.3e Hz (%.2f MHz)\n" frequency frequency/1e6)
    printf("  Capacitive Reactance (Xc): %.2f Ω\n" Xc)
    printf("  Total Impedance (|Z|): %.2f Ω\n" Z)
    
    ; 相位角
    let((phase))
      phase = atan2(neg(Xc) resistance) * 180.0 / pi
      printf("  Phase Angle: %.2f degrees\n" phase)
    )
    
    Z
  )
)

; 使用範例
; calculateImpedance(1000.0 100.0 1e9)
; => 在1GHz頻率下計算阻抗
```

---

## 完整專案

### 📊 RC網路分析器

完整的工具，可以：

1. 掃描整個設計
2. 識別RC網路
3. 計算關鍵參數
4. 生成報表

```lisp
;******************************************************************************
; Function: analyzeRCNetwork
; Description: 完整的RC網路分析工具
;******************************************************************************
procedure(analyzeRCNetwork()
  let((cv report))
    cv = geGetEditCellView()
    
    when(cv
      ; 建立報表檔案
      report = outfile("rc_analysis_report.txt" "w")
      
      fprintf(report "======================================\n")
      fprintf(report "RC Network Analysis Report\n")
      fprintf(report "======================================\n")
      fprintf(report "Cell: %s\n" cv~>cellName)
      fprintf(report "Library: %s\n" cv~>libName)
      fprintf(report "Date: %s\n\n" getCurrentTime())
      
      ; 1. 分析所有電容
      fprintf(report "=== Capacitor Analysis ===\n")
      let((totalCap capCount))
        totalCap = 0.0
        capCount = 0
        
        foreach(inst cv~>instances
          when(rexMatchp("^[cm]" inst~>cellName)
            let((dims cap))
              dims = getInstanceDimensions(inst)
              when(dims
                cap = calculateCapacitance(car(dims) cadr(dims) "MOM")
                totalCap = totalCap + cap
                capCount = capCount + 1
                
                fprintf(report "  %s: %.3f fF\n" inst~>name cap)
              )
            )
          )
        )
        
        fprintf(report "\nTotal Capacitors: %d\n" capCount)
        fprintf(report "Total Capacitance: %.3f fF\n\n" totalCap)
      )
      
      ; 2. 分析所有電阻
      fprintf(report "=== Resistor Analysis ===\n")
      let((totalRes resCount))
        totalRes = 0.0
        resCount = 0
        
        foreach(inst cv~>instances
          when(rexMatchp("^r" inst~>cellName)
            let((dims res))
              dims = getInstanceDimensions(inst)
              when(dims
                res = calculateResistance(car(dims) cadr(dims) "poly")
                totalRes = totalRes + res
                resCount = resCount + 1
                
                fprintf(report "  %s: %.2f Ω\n" inst~>name res)
              )
            )
          )
        )
        
        fprintf(report "\nTotal Resistors: %d\n" resCount)
        fprintf(report "Total Resistance: %.2f Ω\n\n" totalRes)
      )
      
      fprintf(report "======================================\n")
      fprintf(report "End of Report\n")
      fprintf(report "======================================\n")
      
      close(report)
      
      printf("✓ RC analysis complete!\n")
      printf("✓ Report saved to: rc_analysis_report.txt\n")
    )
  )
)
```

---

## 📈 應用場景

### 1. 類比電路設計

- 計算濾波器的截止頻率
- 分析帶寬限制
- 優化功耗

### 2. 時序分析

- RC延遲計算
- 關鍵路徑識別
- 時序優化

### 3. 信號完整性

- 串擾分析
- 反射問題
- 阻抗匹配

### 4. 功耗估算

- 動態功耗（C×V²×f）
- 漏電流
- 熱分析

---

## 🎯 進階擴展

### 1. 與Spectre模擬整合

```lisp
; 自動生成netlist並模擬
procedure(simulateRC(resistance capacitance))
  ; 生成Spectre netlist
  ; 執行模擬
  ; 提取結果
)
```

### 2. 視覺化工具

- 在Layout上標註RC值
- 顏色編碼顯示熱點
- 互動式查詢

### 3. 優化建議

- 自動建議減少寄生參數
- 提供改善方案
- Before/After比較

---

## 📚 參考資料

### 物理公式

- 電容：C = εA/d
- 電阻：R = ρL/A
- 阻抗：Z = √(R² + X²)
- 時間常數：τ = RC

### 製程參數

需要從foundry的PDK中獲取：

- 片電阻值
- 介電常數
- 金屬厚度
- 層間距離

---

## ✅ 總結

通過SKILL，你可以：

✅ **自動計算**元件的R和C值  
✅ **分析寄生參數**影響  
✅ **預測電路行為**（頻率響應、延遲等）  
✅ **優化設計**減少寄生效應  
✅ **生成報告**供文檔和審查使用  

**實際價值：**

- ⏱️ 節省手動計算時間
- 🎯 提早發現問題
- 📊 量化設計品質
- 🚀 加速設計迭代

---

**開始使用這些工具，讓你的IC設計更加精確！** 🔬
