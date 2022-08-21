
功能：微信公众号推送消息到 [memos](https://github.com/usememos/memos)的代理服务。

文档：https://zhaouncle.com/memos%E5%A4%87%E5%BF%98%E5%BD%95%E5%8A%A0%E5%85%A5%E5%BE%AE%E4%BF%A1%E5%85%AC%E4%BC%97%E5%8F%B7%E5%8A%9F%E8%83%BD/


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

