1.執行 main.py --query 加上想查詢文字 即可

2.文件檔都包含在壓縮檔裡，不用額外更改

3.cosine 使用教授程式碼中util本來寫好的公式

4. Euclidean Distance: 將兩個vector裡的每一個數字相減然後平方，最後加總起來開根號
	Ex: (1,2,3) , (2,3,4)
	sqrt((1-2)^2 +(2-3)^2+ (3-4)^2) = sqrt(3)

5.idf計算：在一開始 document 建立好丟進VectorSpace裡的build時計算，統計每一條document Vector裡的數值
		   ，然後保存起來，只保存第一次，因為此值不會隨查詢輸入而更改，故設立self.count做判斷處理

＊範例輸入：
python main.py --query "drill wood sharp"

