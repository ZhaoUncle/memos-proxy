
功能：微信公众号推送消息到 [memos](https://github.com/usememos/memos)的代理服务。

文档：
# 启动
## 1. docker
```
docker run -d -p 5000:5000  -v "/data/go/memos-proxy/config.ini:/app/config.ini" --name memos-proxy zhaoweiping/memos-proxy
```

## 2. docker-compose


# 构建

```
docker build -t memos-proxy .
docker tag memos-proxy zhaoweiping/memos-proxy
docker push zhaoweiping/memos-proxy
```

