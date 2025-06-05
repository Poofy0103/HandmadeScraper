import pymysql
import os
from datetime import datetime, timedelta



class Database:
    def __init__(self, username, password, host, port, database):
        self.user = username
        self.password = password
        self.host = host
        self.port = int(port)
        self.database = database
        self.conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                cursorclass=pymysql.cursors.DictCursor,  # Dùng Cursor để lấy dữ liệu dạng tuple
                autocommit=False
            )
        self.cursor = self.conn.cursor()

    def fetch_data(self, query, *arg):
        """
        Truy vấn dữ liệu từ cơ sở dữ liệu.
        Ví dụ sử dụng:
        --------------
        query = "SELECT * FROM fooditem WHERE CategoryID = %s;"
        data = fetch_data(query, 1) #Truy vấn danh sách fooditem có nhóm món id là 1
        Nếu có dữ liệu, sẽ hiển thị như sau:
        -------------------------------------
        Dữ liệu từ bảng fooditem:
        (row1_data)
        (row2_data)
        ...
        Tham số:
        --------
        query : str
            Câu lệnh SQL cần thực thi.
        arg: any, any,...
            Các format string cần truyền vào câu query
        Trả về:
        -------
        list
            Danh sách các dòng dữ liệu từ truy vấn.
        """
        try:
            self.cursor.execute(query, arg)
            result = self.cursor.fetchall()

            return result

        except pymysql.MySQLError as err:
            self.conn.rollback()
            print(f"Error when executing '{__name__}': {err}")
            return None

    def do_any_sql(self, query, *arg):
        """
        Làm hành động bất kì với db (UPDATE, DELETE, INSERT, CREATE,...)
        Ví dụ sử dụng:
        --------------
        query = "UPDATE order SET status = 4 WHERE ID = %s;" #cập nhật trạng thái đơn hàng thành "Đã huỷ"
        data = do_any_sql(query, 1) #Truy vấn danh sách fooditem có nhóm món id là 1
        Nếu có dữ liệu, sẽ hiển thị như sau:
        -------------------------------------
        Dữ liệu từ bảng fooditem:
        (row1_data)
        (row2_data)
        ...
        Tham số:
        --------
        query : str
            Câu lệnh SQL cần thực thi.
        arg: any, any,...
            Các format string cần truyền vào câu query
        Trả về:
        -------
        list
            Danh sách các dòng dữ liệu từ truy vấn.
        """
        try:
            self.cursor.execute(query, arg)
            self.conn.commit()

            affected_rows = self.cursor.rowcount

            return affected_rows

        except pymysql.MySQLError as err:
            self.conn.rollback()
            print(f"Database error: {err}")
            return None

    def call_stored_procedure(self, stored_proc_name, *params):
        """
        Kết nối đến MySQL và gọi một Stored Procedure bất kỳ.

        Tham số:
            - stored_proc_name (str): Tên stored procedure cần gọi.
            - *params: Các tham số truyền vào stored procedure.

        Ví dụ:
            call_stored_procedure("InsertTestData", "Alice", 22)
            call_stored_procedure("UpdateUserAge", 5, 30)
        """
        try:
            with self.cursor as cursor:
                cursor.callproc(stored_proc_name, params)
                result = cursor.fetchall()

                if result:
                    print(f"✅ Stored Procedure '{stored_proc_name}' executed successfully! Result: {result}")
                else:
                    print(f"⚠ Stored Procedure '{stored_proc_name}' does not return anything!")

            self.conn.commit()
        except pymysql.MySQLError as err:
            self.conn.rollback()
            print(f"❌ Error when executing '{stored_proc_name}': {err}")
        
    def close_connection(self):
        try:
            self.cursor.close()
            self.conn.close()
            print(f"✅ DB is closed successfully.")

        except pymysql.MySQLError as err:
            print(f"Error when executing {__name__}: {err}")
            return None
    
    @staticmethod
    def convert_into_date_type(str_date):
        """str_date should be formatted as dd:mm:yyyy and will be converted into YYYY-MM-DD"""
        return datetime.strptime(str_date, "%d/%m/%Y").date()

class FinanceDatabase(Database):
    def __init__(self, username, password, host, port, database):
        super().__init__(username, password, host, port, database)
    
    def submit_stockprice_data(self, stockCode, crawlResults):
        affected_rows = 0
        try:
            #Query stock
            stockIDQuery = "SELECT ID FROM stock WHERE StockCode = %s LIMIT 1"
            stockIDQueryResult = self.fetch_data(stockIDQuery, stockCode)
            if stockIDQueryResult:
                stockID = stockIDQueryResult[0]['ID']
            else:
                #Insert new stock if it's not existing in the db
                stockIDQuery = "INSERT INTO stock (StockCode) VALUES (%s)"
                self.cursor.execute(stockIDQuery, (stockCode))
                stockID = self.cursor.lastrowid
                affected_rows += 1

            # Insert order details
            stockPriceInsertQuery = """
                INSERT INTO `stockprice` (StockID, Date, ClosePrice, ModifiedClosePrice, TransactionVolume) 
                VALUES (%s, %s, %s, %s, %s)
            """

            stockPriceDetailsData = [(stockID, self.convert_into_date_type(crawlResult['date']), crawlResult['close_price'], crawlResult['modified_close_price'], crawlResult['transaction_volume']) for crawlResult in crawlResults]
            insertedStockPrice = self.cursor.executemany(stockPriceInsertQuery, stockPriceDetailsData)

            affected_rows += insertedStockPrice
            # Commit transaction
            self.conn.commit()
            print(f"✅ StockPrice Data inserted successfully. Affected rows: {affected_rows}")
        except pymysql.MySQLError as err:
            # Rollback transaction if anything fails
            self.conn.rollback()
            print(f"❌ Transaction failed: {err}")

    def submit_news_data(self, stockCode, crawlResults):
        affected_rows = 0
        try:
            #Query stock
            stockIDQuery = "SELECT ID FROM stock WHERE StockCode = %s LIMIT 1"
            stockIDQueryResult = self.fetch_data(stockIDQuery, stockCode)
            if stockIDQueryResult:
                stockID = stockIDQueryResult[0]['ID']
            else:
                #Insert new stock if it's not existing in the db
                stockIDQuery = "INSERT INTO stock (StockCode) VALUES (%s)"
                self.cursor.execute(stockIDQuery, (stockCode))
                stockID = self.cursor.lastrowid
                affected_rows += 1

            # Insert order details
            newsInsertQuery = """
                INSERT INTO `news` (StockID, Date, Title, URLLink) 
                VALUES (%s, %s, %s, %s)
            """

            newsData = [(stockID, self.convert_into_date_type(crawlResult['date']), crawlResult['title'], crawlResult['url_link']) for crawlResult in crawlResults]
            insertedNews = self.cursor.executemany(newsInsertQuery, newsData)

            affected_rows += insertedNews
            # Commit transaction
            self.conn.commit()
            print(f"✅ News Data inserted successfully. Affected rows: {affected_rows}")
        except pymysql.MySQLError as err:
            # Rollback transaction if anything fails
            self.conn.rollback()
            print(f"❌ Transaction failed: {err}")