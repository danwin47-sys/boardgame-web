# SKILL 語言函數參考手冊

> 個人學習筆記 - 最後更新：2025-12-09

## 目錄

- [基礎語法](#基礎語法)
- [字串操作](#字串操作)
- [列表操作](#列表操作)
- [數學運算](#數學運算)
- [檔案I/O](#檔案io)
- [資料庫操作](#資料庫操作)
- [GUI/表單](#gui表單)
- [PCells](#pcells)
- [除錯工具](#除錯工具)
- [常用技巧](#常用技巧)

---

## 基礎語法

### 變數定義

#### `setq`

**語法：** `(setq variable value)`

**說明：** 設定變數值

**參數：**

- `variable` - 變數名稱
- `value` - 要賦予的值

**返回值：** 設定的值

**範例：**

```lisp
setq x 10
setq name "Cadence"
setq list '(1 2 3)
```

**注意事項：**

- 不需要事先宣告變數型別
- 全域變數，在所有scope都可存取

---

#### `let`

**語法：** `(let ((var1 val1) (var2 val2) ...) body)`

**說明：** 建立區域變數

**參數：**

- 變數綁定列表
- 執行主體

**返回值：** 主體最後一個表達式的值

**範例：**

```lisp
let( ((x 5) (y 10))
  printf("x + y = %d\n" x + y)
  x + y  ; 返回 15
)
```

**注意事項：**

- 變數只在let區塊內有效
- 適合避免全域變數污染

---

### 條件控制

#### `if`

**語法：** `(if condition then-expr else-expr)`

**說明：** 條件判斷

**範例：**

```lisp
if( x > 10
  then println("大於10")
  else println("小於等於10")
)
```

---

#### `case`

**語法：** `(case expr (val1 result1) (val2 result2) ... (t default))`

**說明：** 多重條件選擇

**範例：**

```lisp
case( color
  ("red" setColor("紅色"))
  ("blue" setColor("藍色"))
  (t setColor("其他"))
)
```

---

### 迴圈

#### `for`

**語法：** `(for var start end body)`

**說明：** 數值迴圈

**範例：**

```lisp
for( i 1 10
  printf("%d " i)
)
```

---

#### `foreach`

**語法：** `(foreach var list body)`

**說明：** 遍歷列表

**範例：**

```lisp
foreach( item '(1 2 3 4 5)
  printf("%d " item)
)
```

---

## 字串操作

### `strcat`

**語法：** `(strcat str1 str2 ...)`

**說明：** 連接字串

**範例：**

```lisp
strcat("Hello" " " "World")  ; => "Hello World"
```

---

### `sprintf`

**語法：** `(sprintf format args...)`

**說明：** 格式化字串（不輸出）

**範例：**

```lisp
sprintf("Value: %d, Name: %s" 100 "Test")
```

**格式符號：**

- `%s` - 字串
- `%d` - 整數
- `%f` - 浮點數
- `%L` - SKILL物件

---

### `strlen`

**語法：** `(strlen string)`

**說明：** 取得字串長度

**範例：**

```lisp
strlen("Hello")  ; => 5
```

---

## 列表操作

### `list`

**語法：** `(list item1 item2 ...)`

**說明：** 建立列表

**範例：**

```lisp
list(1 2 3)  ; => (1 2 3)
```

---

### `car`

**語法：** `(car list)`

**說明：** 取得列表第一個元素

**範例：**

```lisp
car('(1 2 3))  ; => 1
```

---

### `cdr`

**語法：** `(cdr list)`

**說明：** 取得列表除了第一個元素之外的部分

**範例：**

```lisp
cdr('(1 2 3))  ; => (2 3)
```

---

### `append`

**語法：** `(append list1 list2 ...)`

**說明：** 連接列表

**範例：**

```lisp
append('(1 2) '(3 4))  ; => (1 2 3 4)
```

---

### `length`

**語法：** `(length list)`

**說明：** 取得列表長度

**範例：**

```lisp
length('(1 2 3 4))  ; => 4
```

---

### `nth`

**語法：** `(nth index list)`

**說明：** 取得列表第n個元素（從0開始）

**範例：**

```lisp
nth(2 '(a b c d))  ; => c
```

---

## 數學運算

### `+`, `-`, `*`, `/`

**說明：** 基本數學運算

**範例：**

```lisp
plus(5 3)     ; => 8
difference(10 4)  ; => 6
times(3 4)    ; => 12
quotient(10 2)    ; => 5
```

---

### `max`, `min`

**語法：** `(max num1 num2 ...)` / `(min num1 num2 ...)`

**範例：**

```lisp
max(1 5 3 9 2)  ; => 9
min(1 5 3 9 2)  ; => 1
```

---

## 檔案I/O

### `infile`

**語法：** `(infile filename)`

**說明：** 開啟檔案供讀取

**範例：**

```lisp
let( (port nil line nil)
  port = infile("data.txt")
  when(port
    while( (line = gets("" port))
      printf("%s\n" line)
    )
    close(port)
  )
)
```

---

### `outfile`

**語法：** `(outfile filename [mode])`

**說明：** 開啟檔案供寫入

**範例：**

```lisp
let( (port nil)
  port = outfile("output.txt" "w")
  fprintf(port "Hello World\n")
  close(port)
)
```

---

## 資料庫操作

### `dbOpenCellViewByType`

**語法：** `(dbOpenCellViewByType lib cell view [tool] [mode])`

**說明：** 開啟CellView

**參數：**

- `lib` - Library名稱
- `cell` - Cell名稱
- `view` - View名稱
- `mode` - "r" (讀取) 或 "a" (寫入/追加)

**範例：**

```lisp
cv = dbOpenCellViewByType("myLib" "myCell" "layout" "" "a")
```

---

### `dbCreateInst`

**語法：** `(dbCreateInst cv masterCellView name point orient)`

**說明：** 建立元件實例

**範例：**

```lisp
dbCreateInst(cv masterCV "I0" 0:0 "R0")
```

---

### `dbCreateRect`

**語法：** `(dbCreateRect cv layer bbox)`

**說明：** 建立矩形

**範例：**

```lisp
dbCreateRect(cv list("Metal1" "drawing") list(0:0 10:10))
```

---

### `dbSave`

**語法：** `(dbSave cv)`

**說明：** 儲存CellView

**範例：**

```lisp
dbSave(cv)
```

---

### `dbClose`

**語法：** `(dbClose cv)`

**說明：** 關閉CellView

**範例：**

```lisp
dbClose(cv)
```

---

## GUI/表單

### `hiCreateAppForm`

**語法：** `(hiCreateAppForm formId symbolName title ...)`

**說明：** 建立應用程式表單

**範例：**

```lisp
hiCreateAppForm(
  'myForm
  'myFormSymbol
  "My Custom Form"
  'buttonLayout 'OKCancel
)
```

**待補充：** 需要更多實際範例

---

### `hiDisplayForm`

**語法：** `(hiDisplayForm formId)`

**說明：** 顯示表單

**範例：**

```lisp
hiDisplayForm('myForm)
```

---

## PCells

### `pcDefinePCell`

**語法：** `(pcDefinePCell ...)`

**說明：** 定義參數化元件

**範例：**

```lisp
; 待補充實際範例
```

---

## 除錯工具

### `printf`

**語法：** `(printf format args...)`

**說明：** 格式化輸出到CIW

**範例：**

```lisp
printf("Debug: x=%d, y=%d\n" x y)
```

---

### `error`

**語法：** `(error message)`

**說明：** 產生錯誤訊息

**範例：**

```lisp
when( x < 0
  error("x must be positive!")
)
```

---

### `warn`

**語法：** `(warn message)`

**說明：** 產生警告訊息

**範例：**

```lisp
warn("This feature is deprecated")
```

---

## 常用技巧

### 檢查變數是否為nil

```lisp
when( variableName
  ; 變數不是nil時執行
)

unless( variableName
  ; 變數是nil時執行
)
```

### 安全的屬性存取

```lisp
; 使用 ->? 而不是 -> 來避免nil錯誤
cellView->?name
```

### 錯誤處理

```lisp
errset(
  ; 可能會出錯的程式碼
  someFunction()
  t  ; t表示顯示錯誤訊息
)
```

---

## 筆記模板

每當學習新函數時，請複製以下模板填寫：

```markdown
### `函數名稱`
**語法：** `(函數名稱 參數...)`

**說明：** 簡短描述函數功能

**參數：**
- `參數1` - 說明
- `參數2` - 說明

**返回值：** 描述返回值

**範例：**
```lisp
; 實際使用範例
```

**注意事項：**

- 重要提醒
- 常見錯誤
- 最佳實踐

**相關函數：** 列出相關的函數

**學習日期：** YYYY-MM-DD

**來源：** 文檔頁碼/網址/專案

```

---

## 學習進度追蹤

- [ ] 基礎語法 (20個函數)
- [ ] 字串操作 (15個函數)
- [ ] 列表操作 (20個函數)
- [ ] 檔案I/O (10個函數)
- [ ] 資料庫操作 (30個函數)
- [ ] GUI開發 (25個函數)
- [ ] PCells (15個函數)

**目標：** 每週學習並記錄至少10個新函數

---

## 快速參考索引

### 常用函數速查
| 功能 | 函數 | 頁面 |
|------|------|------|
| 設定變數 | `setq` | [基礎語法](#基礎語法) |
| 區域變數 | `let` | [基礎語法](#基礎語法) |
| 字串連接 | `strcat` | [字串操作](#字串操作) |
| 列表第一個元素 | `car` | [列表操作](#列表操作) |
| 開啟檔案讀取 | `infile` | [檔案I/O](#檔案io) |
| 開啟CellView | `dbOpenCellViewByType` | [資料庫操作](#資料庫操作) |

---

## 參考資源

- Cadence SKILL Language User Guide
- Cadence SKILL Language Reference
- [EDA Board - SKILL Forum](https://www.edaboard.com/forums/)
- 個人專案程式碼路徑：待填寫

---

*提示：定期回顧和更新此手冊，將學習到的新知識及時記錄下來！*
