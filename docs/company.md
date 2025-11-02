Here are the methods to fetch information about a company using Vnstock, along with their corresponding data types, sample outputs, and data structures:

### 1. Company Overview
**Method**
```python
company.overview()
```

**Sample Output**
Shell
```
>>> company.overview()
  symbol     id  issue_share                                            history  ...  icb_name2  icb_name4 financial_ratio_issue_share charter_capital
0    ACB  67505   4466657912   - Ngày 24/04/1993: Ngân hàng Thương mại Cổ ph...  ...  Ngân hàng  Ngân hàng                  4466657900  44666579120000

[1 rows x 10 columns]
```

**Data Structure**
```
 #   Column                       Non-Null Count  Dtype 
---  ------                       --------------  ----- 
 0   symbol                       1 non-null      object
 1   id                           1 non-null      object
 2   issue_share                  1 non-null      int64 
 3   history                      1 non-null      object
 4   company_profile              1 non-null      object
 5   icb_name3                    1 non-null      object
 6   icb_name2                    1 non-null      object
 7   icb_name4                    1 non-null      object
 8   financial_ratio_issue_share  1 non-null      int64 
 9   charter_capital              1 non-null      int64 
```

### 2. Shareholders
**Method**
```python
company.shareholders()
```

**Sample Output**
Shell
```
>>> company.shareholders().head()
         id                            share_holder   quantity  share_own_percent update_date
0  76437158  Vietnam Enterprise Investments Limited  212880184           0.054809  2024-09-13
1  76432034         Sather Gate Investments Limited  193907186           0.049900  2024-05-15
2  76413536               Estes Investments Limited   83010435           0.049900  2024-05-15
3  76429810                         Phạm Thị Thu Hà     285000           0.049900  2016-05-20
4  76434014                           Trần Hùng Huy  153062159           0.039400  2025-01-24
```

**Data Structure**
```
 #   Column             Non-Null Count  Dtype  
---  ------             --------------  -----  
 0   id                 5 non-null      object 
 1   share_holder       5 non-null      object 
 2   quantity           5 non-null      int64  
 3   share_own_percent  5 non-null      float64
 4   update_date        5 non-null      object 
```

### 3. Officers
**Method**
```python
company.officers(filter_by='working')
```

**Parameters**
- `filter_by` can be 'working', 'resigned', or 'all'.

**Sample Output**
Shell
```
>>> company.officers(filter_by='all').head()
   id       officer_name                officer_position position_short_name update_date  officer_own_percent   quantity           type
0   6      Trần Hùng Huy      Chủ tịch Hội đồng Quản trị       Chủ tịch HĐQT  2025-01-24               0.0394  153062159  đang làm việc
1   7      Đặng Thu Thủy    Thành viên Hội đồng Quản trị             TV HĐQT  2025-01-24               0.0137   53350036  đang làm việc
2  11      Đặng Phú Vinh                   Giám đốc khối             GĐ Khối  2025-01-24               0.0042   16454507  đang làm việc
3  13       Đỗ Minh Toàn                   Tổng Giám đốc                 TGĐ  2025-01-24               0.0008    3202886  đang làm việc
4   8  Nguyễn Thành Long  Phó Chủ tịch Hội đồng Quản trị   Phó Chủ tịch HĐQT  2025-01-24               0.0004    1647067  đang làm việc
```

**Data Structure**
```
 #   Column               Non-Null Count  Dtype  
---  ------               --------------  -----  
 0   id                   5 non-null      object 
 1   officer_name         5 non-null      object 
 2   officer_position     5 non-null      object 
 3   position_short_name  5 non-null      object 
 4   update_date          5 non-null      object 
 5   officer_own_percent  5 non-null      float64
 6   quantity             5 non-null      int64  
 7   type                 5 non-null      object
```

### 4. Subsidiaries
**Method**
```python
company.subsidiaries()
```

**Parameters**
- `filter_by` can be 'all' or 'subsidiary'.

**Sample Output**
Shell
```
>>> company.subsidiaries()
         id sub_organ_code ownership_percent                                         organ_name              type
0  21632918           ACBA                 1  Công Ty TNHH Quản Lý Nợ Và Khai Thác Tài Sản N...       công ty con
1  21632919           ACBL                 1  Công Ty TNHH Một Thành Viên Cho Thuê Tài Chính...       công ty con
2  21632920           ACBS                 1                       Công ty TNHH Chứng khoán ACB       công ty con
0  21632922           ACBD              None    CÔNG TY CỔ PHẦN DỊCH VỤ BẢO VỆ NGÂN HÀNG Á CHÂU  công ty liên kết
1  21632921           SGGS              None          Công ty Cổ phần Sài Gòn Kim hoàn ACB- SJC  công ty liên kết
```

**Data Structure**
```
 #   Column             Non-Null Count  Dtype 
---  ------             --------------  ----- 
 0   id                 5 non-null      object
 1   sub_organ_code     5 non-null      object
 2   ownership_percent  3 non-null      object
 3   organ_name         5 non-null      object
 4   type               5 non-null      object
```

### 5. Events
**Method**
```python
company.events()
```

**Sample Output**
Shell
```
>>> company.events().head(3)
      id                                  event_title                            en__event_title  ... exright_date           event_list_name en__event_list_name
0  18149  ACB- Niêm yết bổ sung 498.821.183 cổ phiếu   ACB- Lists additional 498,821,183 shares   ...   1753-01-01             Niêm yết thêm  Additional Listing
1  18128                     Trả cổ tức bằng tiền mặt                                             ...   2010-11-08  Trả cổ tức bằng tiền mặt       Cash Dividend
2  18133                     Trả cổ tức bằng tiền mặt                                             ...   2012-01-03  Trả cổ tức bằng tiền mặt       Cash Dividend

[3 rows x 13 columns]
```

**Data Structure**
```
 #   Column               Non-Null Count  Dtype  
---  ------               --------------  -----  
 0   id                   3 non-null      object 
 1   event_title          3 non-null      object 
 2   en__event_title      3 non-null      object 
 3   public_date          3 non-null      object 
 4   issue_date           3 non-null      object 
 5   source_url           3 non-null      object 
 6   event_list_code      3 non-null      object 
 7   ratio                1 non-null      float64
 8   value                1 non-null      float64
 9   record_date          3 non-null      object 
 10  exright_date         3 non-null      object 
 11  event_list_name      3 non-null      object 
 12  en__event_list_name  3 non-null      object
```

### 6. News
**Method**
```python
company.news()
```

**Sample Output**
Shell
```
>>> company.news().head(3)
        id                                         news_title news_sub_title friendly_sub_title  ... ref_price  floor ceiling  price_change_pct
0  6944486  ACB:  Công ty TNHH MTV Nhật Quân HQ đăng ký bá...                                    ...     26200  24400   28000          0.003817
1  6944221  ACB:  Nghị quyết HĐQT về phương án phát hành t...                                    ...     26000  24200   27800          0.007692
2  6894216  ACB:  Thông báo tổ chức ĐHĐCĐ thường niên năm ...                                    ...     26450  24600   28300         -0.005671

[3 rows x 18 columns]
```

**Data Structure**
```
 #   Column              Non-Null Count  Dtype  
---  ------              --------------  -----  
 0   id                  3 non-null      object 
 1   news_title          3 non-null      object 
 2   news_sub_title      3 non-null      object 
 3   friendly_sub_title  3 non-null      object 
 4   news_image_url      3 non-null      object 
 5   news_source_link    3 non-null      object 
 6   created_at          0 non-null      object 
 7   public_date         3 non-null      int64  
 8   updated_at          0 non-null      object 
 9   lang_code           3 non-null      object 
 10  news_id             3 non-null      object 
 11  news_short_content  3 non-null      object 
 12  news_full_content   3 non-null      object 
 13  close_price         3 non-null      int64  
 14  ref_price           3 non-null      int64  
 15  floor               3 non-null      int64  
 16  ceiling             3 non-null      int64  
 17  price_change_pct    3 non-null      float64
```

### 7. Analysis Reports
**Method**
```python
company.reports()
```

**Sample Output**
Shell
```
>>> company.reports()
                   date  ...                                               name
0  2025-01-22T00:00:00Z  ...  ACB - Tập trung vào tăng trưởng tín dụng hơn t...
1  2024-10-24T00:00:00Z  ...  ACB – NOII thấp hơn dự kiến, ảnh hưởng tiêu cự...
2  2024-09-09T00:00:00Z  ...  ACB [MUA +35,0%] - Tăng dự báo tăng trưởng tín...

[3 rows x 4 columns]
```

**Data Structure**
```
 #   Column       Non-Null Count  Dtype 
---  ------       --------------  ----- 
 0   date         3 non-null      object
 1   description  3 non-null      object
 2   link         3 non-null      object
 3   name         3 non-null      object
```

### 8. Financial Ratios Summary
**Method**
```python
company.ratio_summary()
```

**Sample Output**
Shell
```
>>> company.ratio_summary()
  symbol  year_report  length_report    update_date         revenue  revenue_growth      net_profit  net_profit_growth  ...  rtq10  dividend  ebitda  ebit  le  de   ccc  rtq17
0    ACB         2024              5  1741199572843  50902749000000       -0.027586  16789768000000           0.046435  ...      0         0       0     0   0   0  None      0

[1 rows x 46 columns]
```

**Data Structure**
```
 #   Column                 Non-Null Count  Dtype  
---  ------                 --------------  -----  
 0   symbol                 1 non-null      object 
 1   year_report            1 non-null      int64  
 2   length_report          1 non-null      int64  
 3   update_date            1 non-null      int64  
 4   revenue                1 non-null      int64  
 5   revenue_growth         1 non-null      float64
 6   net_profit             1 non-null      int64  
 7   net_profit_growth      1 non-null      float64
 8   ebit_margin            1 non-null      int64  
 9   roe                    1 non-null      float64
 10  roic                   1 non-null      int64  
 11  roa                    1 non-null      float64
 12  pe                     1 non-null      float64
 13  pb                     1 non-null      float64
 14  eps                    1 non-null      float64
 15  current_ratio          1 non-null      int64  
 16  cash_ratio             1 non-null      int64  
 17  quick_ratio            1 non-null      int64  
 18  interest_coverage      0 non-null      object 
 19  ae                     1 non-null      float64
 20  fae                    1 non-null      float64
 21  net_profit_margin      1 non-null      float64
 22  gross_margin           1 non-null      int64  
 23  ev                     1 non-null      int64  
 24  issue_share            1 non-null      int64  
 25  ps                     1 non-null      float64
 26  pcf                    1 non-null      float64
 27  bvps                   1 non-null      float64
 28  ev_per_ebitda          1 non-null      int64  
 29  at                     1 non-null      int64  
 30  fat                    1 non-null      int64  
 31  acp                    0 non-null      object 
 32  dso                    1 non-null      int64  
 33  dpo                    1 non-null      int64  
 34  eps_ttm                1 non-null      float64
 35  charter_capital        1 non-null      int64  
 36  rtq4                   1 non-null      int64  
 37  charter_capital_ratio  1 non-null      float64
 38  rtq10                  1 non-null      int64  
 39  dividend               1 non-null      int64  
 40  ebitda                 1 non-null      int64  
 41  ebit                   1 non-null      int64  
 42  le                     1 non-null      int64  
 43  de                     1 non-null      int64  
 44  ccc                    0 non-null      object 
 45  rtq17                  1 non-null      int64 
```

### 9. Trading Statistics
**Method**
```python
company.trading_stats()
```

**Sample Output**
Shell
```
>>> company.trading_stats()
  symbol exchange               ev  ceiling  floor  ...  foreign_room  avg_match_volume_2w  foreign_holding_room  current_holding_ratio  max_holding_ratio
0    ACB     HOSE  117249769875000    28000  24400  ...    1339997373              8108407            1339997373                    0.3                0.3
```

**Data Structure**
```
 #   Column                 Non-Null Count  Dtype  
---  ------                 --------------  -----  
 0   symbol                 1 non-null      object 
 1   exchange               1 non-null      object 
 2   ev                     1 non-null      int64  
 3   ceiling                1 non-null      int64  
 4   floor                  1 non-null      int64  
 5   ref_price              1 non-null      int64  
 6   open                   1 non-null      int64  
 7   match_price            1 non-null      int64  
 8   close_price            1 non-null      int64  
 9   price_change           1 non-null      int64  
 10  price_change_pct       1 non-null      float64
 11  high                   1 non-null      int64  
 12  low                    1 non-null      int64  
 13  total_volume           1 non-null      int64  
 14  high_price_1y          1 non-null      int64  
 15  low_price_1y           1 non-null      int64  
 16  pct_low_change_1y      1 non-null      float64
 17  pct_high_change_1y     1 non-null      float64
 18  foreign_volume         1 non-null      int64  
 19  foreign_room           1 non-null      int64  
 20  avg_match_volume_2w    1 non-null      int64  
 21  foreign_holding_room   1 non-null      int64  
 22  current_holding_ratio  1 non-null      float64
 23  max_holding_ratio      1 non-null      float64
```


