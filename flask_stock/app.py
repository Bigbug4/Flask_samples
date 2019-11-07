# coding = utf-8
"""
@author: zhou
@time:2019/11/7 11:22
@File: app.py
"""

from flask import Flask, render_template, request
from pyecharts import options as opts
from pyecharts.charts import Kline
import tushare as ts
import pandas as pd
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


def get_stock_data(code, ctime):
    df = ts.get_hist_data(code)
    mydate = df[:ctime].index.tolist()
    mydata = df[:ctime][['open', 'close', 'low', 'high']].values.tolist()
    return [mydate, mydata]


def kline_base(mydate, data, name) -> Kline:
    c = (
        Kline()
        .add_xaxis(mydate)
        .add_yaxis("%s" % name, data)
        .set_global_opts(
            yaxis_opts=opts.AxisOpts(is_scale=True,
                                    splitarea_opts=opts.SplitAreaOpts(
                    is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                ),
            ),
            xaxis_opts=opts.AxisOpts(is_scale=True,
                                    axislabel_opts=opts.LabelOpts(rotate=-30)),
            title_opts=opts.TitleOpts(title="股票走势"),
            datazoom_opts=[opts.DataZoomOpts()],
            toolbox_opts=opts.ToolboxOpts(is_show=True),
        )
    )
    return c


@app.route("/")
def index():
    return render_template("index.html")


def check_stock(code):
    n = 0
    l = []
    stock_code = pd.read_csv("stock_code_name.csv", dtype=object)
    stock_code.drop('Unnamed: 0', axis=1, inplace=True)
    stock_list = stock_code.values.tolist()
    for i in stock_list:
        if code in i:
            n += 1
            l = i
        else:
            continue
    return n, l


@app.route("/Kline", methods=['GET', 'POST'])
def get_kline_chart():
    stock_name = request.form.get('stockName')
    query_time = request.form.get('queryTime')
    if not stock_name:
        stock_name = '平安银行'
    if not query_time:
        query_time = 30
    status, stock_code = check_stock(stock_name)
    if status == 0:
        return 'error stock code or name'
    mydate, mydata = get_stock_data(stock_code[0], int(query_time))
    c = kline_base(mydate, mydata, stock_code[1])
    return c.dump_options()


if __name__ == '__main__':
    app.run(debug=True)
