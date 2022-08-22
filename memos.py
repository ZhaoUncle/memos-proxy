# -*- coding: UTF-8 -*-

from flask import Flask
from flask import request
import hashlib
import xml.etree.ElementTree as ET
import json
import time
import requests
import configparser
import urllib.request
import os
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
        if con.get('prod', 'wechat_open_id') == "all":
            pass
        elif str(fromUser) not in con.get('prod', 'wechat_open_id'):
            print("该用户的微信 openid 是【 %s 】，如果你允许该用户访问 memos，要记得写入 config.ini 配置文件才行" %(fromUser),flush=True)
            return reply_text(fromUser, toUser, "该用户没有权限")
        
        if msgType == "text":
            content = xml.find('Content').text
            memos_reponse_id = memos_post_api(content)
            if len(str(memos_reponse_id)) != "":
                return reply_text(fromUser, toUser, "%s") %(con.get('prod', 'messages_success'))
            else:
                return reply_text(fromUser, toUser, "%s").format(con.get('prod', 'messages_failed'))
        elif msgType == "image":
            content1 = xml.find('PicUrl').text
            content2 = xml.find('MediaId').text
            img_name, img_path = wechat_image(content1,content2)
            id,filename = memos_post_file_api(img_name, img_path)
            image_content = "![](/h/r/%s/%s)" % (id,filename)
            memos_reponse_id = memos_post_api(image_content)
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
    url =  con.get('prod', 'memos_url') + "/api/memo?openId=" + con.get('prod', 'memos_openid')

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

def wechat_image(picurl,mediaId):
    if not os.path.exists("./resource"):
        os.makedirs("./resource")

    img_name = "%s.png" % (mediaId)
    img_path =  "./resource/%s.png" % (mediaId)

    i_response = urllib.request.urlopen(picurl)
    img = i_response.read()
    
    with open(img_path,'wb') as f:
        f.write(img)
    return img_name, img_path


def memos_post_file_api(file_name,file_path):
    url =  con.get('prod', 'memos_url') + "/api/resource?openId=" +  con.get('prod', 'memos_openid')
    payload={}
    files=[
        ('file', (file_name, open(file_path ,'rb'),'image/png'))
    ]
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    del_local_file(file_path) 
    res_json = json.loads(response.text)
    return res_json ["data"]["id"],res_json ["data"]["filename"]

def del_local_file(file_path):
    files_del = con.get('prod', 'files_del')
    if files_del == "yes":
        print("临时缓存图片 %s 已经删除"%(file_path) )
        os.remove(file_path)
    else:
        pass

if __name__ == "__main__":
    host = con.get('prod', 'flask_host')
    port = con.get('prod', 'flask_port')
    app.run(host=host, port=port)
