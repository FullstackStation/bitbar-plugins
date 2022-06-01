#!/usr/bin/env /usr/local/bin/python
# coding=utf-8
#
# <bitbar.title>Vietnam's stock market information</bitbar.title>
# <bitbar.version>v2</bitbar.version>
# <bitbar.author>Nhan Nguyen</bitbar.author>
# <bitbar.author.github>virusvn</bitbar.author.github>
# <bitbar.desc>Displays Vietnam's stock market information</bitbar.desc>
# <bitbar.image>https://i.imgur.com/Qufrx8G.png</bitbar.image>
# <bitbar.dependencies>python</bitbar.dependencies>
#
# by virusvn

import os
import json
import base64
from urllib.request import urlopen
import subprocess

STOCK_SYMBOLS = (
    # "YEG",
    #  "MBB",
    # "VCI",
    # "VJC",
    # "SCR",
    # "CTD",
    # "PNJ",
    # "E1VFVN30",
    # "VNM",
    # "SSI",
    # "FPT",
    "HAG",
    "HNG",
    "DBC",
    # "VPB",
    # "CTG",
    # "VHM",
    # "NLG",
    # "VRE",
    # "ACB",
    # "YEG",
    # "DXG",
    # "BID",
    # "GAS",
    # "VGC",
    # "HSG",
    # "HCM",
    # "VIC",
    # "VCB",
    "VNM",
    "GEX",
    "STB",
)
NO_CHART = 0
CHART_IN_MAINMENU = 1
CHART_IN_SUBMENU = 2
USE_COLOR_IN_MAIN_TITLE = False

ENABLE_CHART_STOCKS = {
    # "YEG": {
    #     "type": CHART_IN_MAINMENU
    # },
    # "MBB": {
    #     "type": CHART_IN_MAINMENU
    # },
    # "PNJ": {
    #     "type": CHART_IN_MAINMENU
    # },
    # "VCI": {
    #     "type": CHART_IN_MAINMENU
    # },
    # "VNM": {
    #     "type": CHART_IN_SUBMENU
    # }
}

""" If True, the script will notify an alert if it meet the conditions """
ENABLE_NOTIFICATION = False


DATA_API_ENDPOINT = "http://solieu3.vcmedia.vn/ProxyHandler.ashx?RequestName=StockSymbolSlide&RequestType=json&sym={}".format(
    ";".join(STOCK_SYMBOLS)
)
IMAGE_API_ENDPOINT_FORMAT = "http://s.cafef.vn/chartindex/pricechart.ashx?type=price&width=260&height=160&symbol={}"

r = urlopen(DATA_API_ENDPOINT)
"""The data will be received:
var StockSymbolSlide = ({
	"Symbols":[
		{"Symbol":"VNM","Datas":[170.3,0.40000000000000568,0.2,181.7,158.1]},
		{"Symbol":"SSI","Datas":[27.6,0.20000000000000284,0.7,29.3,25.5]},
		{"Symbol":"FPT","Datas":[42.5,0.29999999999999716,0.7,45.15,39.25]},
		{"Symbol":"MBB","Datas":[22.8,0.19999999999999929,0.9,24.15,21.05]},
	],
	"ListNews":[],
	"ListDoanhNghiep":[],
	"HeaderBox":""
});
"""
jsonValue = "{%s}" % (r.read().decode("utf-8").split("{", 1)[1].rsplit("}", 1)[0],)
value = json.loads(jsonValue)

ENABLE_CHART = True

COLORFUL = False

lines = []
if "Symbols" in value:
    for sym in value["Symbols"]:
        color = "black"
        if COLORFUL:
            if sym["Datas"][0] == sym["Datas"][3]:
                color = "magenta"
            elif sym["Datas"][0] == sym["Datas"][4]:
                color = "cyan"
            elif float(sym["Datas"][1]) < 0:
                color = "red"
            elif float(sym["Datas"][1]) > 0:
                color = "green"
            else:
                pass

        # Process for +/- sign
        changed = sym["Datas"][1] or ""
        if changed:
            changed = round(float(changed), 2)
            if changed > 0:
                changed = "+" + str(changed)

        # Don't want to display HNX Index
        if sym["Symbol"] == "HNX":
            continue

        # Use HSX Index for main title
        if sym["Symbol"] == "HSX":
            if not USE_COLOR_IN_MAIN_TITLE:
                color = "black"

            main_title = "{: <5} {: <5} {: <5}| color={} trim=false".format(
                sym["Symbol"], sym["Datas"][0], changed, color
            )
            continue

        # Append the current symbol
        lines.append(
            "{: <10} {: <10} {}| color={} trim=false font=Monaco".format(
                sym["Symbol"], sym["Datas"][0], changed, color
            )
        )

        # Process to add image
        if (
            ENABLE_CHART
            and sym["Symbol"] in ENABLE_CHART_STOCKS.keys()
            and ENABLE_CHART_STOCKS[sym["Symbol"]]["type"] != NO_CHART
        ):

            image_response = urlopen(IMAGE_API_ENDPOINT_FORMAT.format(sym["Symbol"]))
            # print image_response.content
            base64_image = str(base64.b64encode(image_response.read()))
            if ENABLE_CHART_STOCKS[sym["Symbol"]]["type"] == CHART_IN_SUBMENU:
                lines.append("-- | image={} refresh=true".format(base64_image))
            else:
                lines.append("| image={} refresh=true".format(base64_image))

# Get index's image
image_response = urlopen("http://s.cafef.vn/chartindex/chartheader.ashx")
vnindex_image = str(base64.b64encode(image_response.read()))
lines.insert(0, "---")
lines.insert(0, "| image={}".format(vnindex_image))
lines.insert(0, "---")
lines.insert(0, main_title)

for line in lines:
    print(line)

# [WIP] need to define some conditions for notifications
if ENABLE_NOTIFICATION:
    command = 'osascript -e \'display notification "Tăng/Giảm nhiều quá" with title "Cảnh báo"\''
    curenv = os.environ
    curenv["LC_ALL"] = "en_US.UTF-8"

    p = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=curenv,
    )
