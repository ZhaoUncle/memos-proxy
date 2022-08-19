from flask import Flask
from flask import request
import hashlib
import xml.etree.ElementTree as ET
import json
import time
import requests
import configparser

file = 'config.ini'
con = configparser.ConfigParser()
con.read(file, encoding='utf-8')

app=Flask(__name__)

@app.route("/")
def index():
    return "hello,world"

@app.route("/wechat", methods=["GET", "POST"])
def wexin():
    if request.method == "GET":
        my_signature = request.args.get('signature')
        my_timestamp = request.args.get('timestamp')
        my_nonce = request.args.get('nonce')
        my_echostr = request.args.get('echostr')

        token = con.get('prod', 'wechat_token') ### 微信公众号的token
        data = [token,my_timestamp,my_nonce]
        data.sort()
        temp = ''.join(data)
        s = hashlib.sha1()
        s.update(temp.encode("utf-8"))
        mysignature = s.hexdigest()
        if my_signature == mysignature:
            return my_echostr
        else:
            return ""
    else:
        xml = ET.fromstring(request.data)        
        toUser = xml.find('ToUserName').text
        fromUser = xml.find('FromUserName').text
        msgType = xml.find("MsgType").text
        createTime = xml.find("CreateTime")
        if msgType == "text":
            content = xml.find('Content').text
            memos_reponse_id = memos_post_api(content)
            print(content)
            if len(str(memos_reponse_id)) != "":
                return reply_text(fromUser, toUser, "%s") %(con.get('prod', 'messages_success'))
            else:
                return reply_text(fromUser, toUser, "%s").format(con.get('prod', 'messages_failed'))
        else:
            return reply_text(fromUser, toUser, "微信公众号连接出问题了")

def memos_post_api(content):
    """
    这个函数是把微信公众号用户的提交信息推送到memos，然后返回提交id。
    """
    url =  con.get('prod', 'memos_url')
    payload = json.dumps({
        "content": "%s" %(content)
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    r1 = json.loads(response.text)
    return r1["data"]["id"]

def reply_text(to_user, from_user, content):
    """
    以文本类型的方式回复请求
    """
    return """
    <xml>
        <ToUserName><![CDATA[{}]]></ToUserName>
        <FromUserName><![CDATA[{}]]></FromUserName>
        <CreateTime>{}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{}]]></Content>
    </xml>
    """.format(to_user, from_user,int(time.time() * 1000), content)


if __name__ == "__main__":
    host = con.get('prod', 'flask_host')
    port = con.get('prod', 'flask_port')
    app.run(host=host, port=port)
