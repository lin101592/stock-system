from flask import Flask, render_template, request
import sqlite3
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your-secret-key-123'

# 建立資料庫
with sqlite3.connect('data.db') as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS purchases (
                    barcode TEXT,
                    purchase_id TEXT,
                    price REAL)''')

@app.route('/', methods=['GET', 'POST'])
def index():
    msg = None
    if request.method == 'POST':
        if 'file' not in request.files:
            msg = '沒有選擇檔案'
        else:
            file = request.files['file']
            if file.filename == '':
                msg = '沒有選擇檔案'
            elif file.filename.lower().endswith(('.xlsx', '.xls')):
                try:
                    df = pd.read_excel(file)
                    conn = sqlite3.connect('data.db')
                    count = 0
                    for _, row in df.iterrows():
                        barcode = str(row.iloc[0]).strip()
                        purchase_id = str(row.iloc[1]).strip() if len(row) > 1 else ""
                        price = float(row.iloc[2]) if len(row) > 2 else 0.0
                        if barcode and barcode.lower() not in ['nan', '條碼', 'barcode']:
                            conn.execute('INSERT INTO purchases VALUES (?, ?, ?)',
                                       (barcode, purchase_id, price))
                            count += 1
                    conn.commit()
                    conn.close()
                    msg = f'Excel 匯入成功！新增 {count} 筆資料'
                except Exception as e:
                    msg = f'匯入失敗：{str(e)}'
            else:
                msg = '只支援 .xlsx 或 .xls 檔案'

    return render_template('index.html', msg=msg)

@app.route('/search/<barcode>')
def search(barcode):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute('SELECT purchase_id, price FROM purchases WHERE barcode=? ORDER BY price DESC', (barcode,))
    rows = cur.fetchall()
    conn.close()
    if rows:
        return '<br>'.join([f"{pid if pid else '無編號'} → {price} 元" for pid, price in rows])
    return '查無資料'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)