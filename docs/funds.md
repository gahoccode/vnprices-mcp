Below are the methods to get information on funds using the `vnstock` module, including sample outputs and parameters:

### 1. Liệt kê quỹ (Listing Funds)
**Method:** 
```python
fund.listing(fund_type="")
```

**Parameters:**
- `fund_type` (str, optional): Category of the fund. Default is an empty string to list all funds. Options include:
  - `BALANCED`: Balanced Fund
  - `BOND`: Bond Fund
  - `STOCK`: Stock Fund
  - `""`: Lists all funds (default)

**Sample Output:**
```shell
>>> fund.listing().head()
Total number of funds currently listed on Fmarket:  49
  short_name                                               name     fund_type                                    fund_owner_name  ...  nav_update_at fund_id_fmarket  fund_code   vsd_fee_id
0     SSISCA         QUỸ ĐẦU TƯ LỢI THẾ CẠNH TRANH BỀN VỮNG SSI  Quỹ cổ phiếu                       CÔNG TY TNHH QUẢN LÝ QUỸ SSI  ...     2024-07-09              11     SSISCA   SSISCAN001
1      VESAF  QUỸ ĐẦU TƯ CỔ PHIẾU TIẾP CẬN THỊ TRƯỜNG VINACA...  Quỹ cổ phiếu            CÔNG TY CỔ PHẦN QUẢN LÝ QUỸ VINACAPITAL  ...     2024-07-09              23      VESAF    VESAFN002
...
```

### 2. Tìm kiếm quỹ (Searching Funds)
**Method:**
```python
fund.filter(symbol)
```

**Parameters:**
- `symbol` (str, required): Abbreviation of the fund to search. Enter part of the name to list matching results.

**Sample Output:**
```shell
>>> fund.filter('DC')
   id shortName
0  40     VNDCF
1  67      DCIP
...
```

### 3. Thông tin chi tiết quỹ (Detailed Information on Funds)

#### a. Báo cáo tăng trưởng NAV (NAV Growth Report)
**Method:** 
```python
fund.details.nav_report(symbol)
```

**Parameters:**
- `symbol` (str, required): Abbreviation of the fund to search.

**Sample Output:**
```shell
>>> fund.details.nav_report('SSISCA')
Retrieving data for SSISCA
            date  nav_per_unit short_name
0     2017-01-04      14412.31     SSISCA
1     2017-01-11      14527.86     SSISCA
...
```

#### b. Danh mục đầu tư lớn (Top Holdings)
**Method:**
```python
fund.details.top_holding(symbol)
```

**Parameters:**
- `symbol` (str, required): Abbreviation of the fund to search.

**Sample Output:**
```shell
>>> fund.details.top_holding('SSISCA')
Retrieving data for SSISCA
  stock_code                industry  net_asset_percent type_asset ...
0        FPT  Công nghệ và thông tin              17.10      STOCK ...
1        MWG                  Bán lẻ               6.65      STOCK ...
...
```

#### c. Phân bổ theo ngành (Industry Allocation)
**Method:**
```python
fund.details.industry_holding(symbol)
```

**Parameters:**
- `symbol` (str, required): Abbreviation of the fund to search.

**Sample Output:**
```shell
>>> fund.details.industry_holding('SSISCA')
Retrieving data for SSISCA
                      industry  net_asset_percent short_name
0                    Ngân hàng              20.46     SSISCA
1       Công nghệ và thông tin              17.10     SSISCA
...
```

#### d. Phân bổ theo tài sản (Asset Allocation)
**Method:**
```python
fund.details.asset_holding(symbol)
```

**Parameters:**
- `symbol` (str, required): Abbreviation of the fund to search.

**Sample Output:**
```shell
>>> fund.details.asset_holding('SSISCA')
Retrieving data for SSISCA
   asset_percent                asset_type short_name
0          83.08                  Cổ phiếu     SSISCA
1          16.92  Tiền và tương đương tiền     SSISCA
```

Each method returns a pandas DataFrame that can be further analyzed or stored in various formats such as Excel or CSV.
