# TyDesk - 统医桌面
一个超级简单、功能全面的、专为中国医院设计的WEB应用启动器

## 医院为什么需要“桌面入口”程序？
主要包含以下几个理由：

- 医院系统种类繁多，且都有WEB接口
- WEB入口URL过长，不易部署；普通用户不易使用
- 无统一入口情况下，医生浪费时间在寻找、定位、打开等时间上
- 有些系统需要IE，有些系统需要谷歌;这让无技术背景的医生很疲惫
- 桌面云的失败，给“桌面入口”程序更多的存在合理性

## 主要功能
- 实现了多系统的桌面集成
- 对Web应用的集中分发
- 对医院内、外网环境的适应
- 对多种浏览器的支持
- 对离线的支持
- 为医院IT自动化管理提供接口与支持

## 使用指南

### 下载服务器
[https://github.com/tydesk/tyserver/releases](https://github.com/tydesk/tyserver/releases "服务器下载页面")

### 配置服务器
下载完毕后，解压缩TyServer.zip。直接启动里面的Exe即可启动服务器。 不要，要发布新应用需要配置config.json


```json
{
	"outApps": [
    { "id":1, "title": "病理报告", "url": "http://baidu.com/__", "open": "chrome", "net": "out"},
    { "id":2, "title": "百度URL测试", "url": "http://baidu.com", "open": "chrome", "net": "in"}
  ],
  "inApps": [
    { "id":1, "title": "测试住院", "url": "http://baidu.com", "open": "IE", "net": "in"}
  ],
  "otherApps": [
    { "id":1, "title": "测试其他", "url": "http://baidu.com", "open": "firefox", "net": "out"}
  ],
  "admins": [
    { "ip": "192.168.30.101", "name": "Panzhang Wang"},
    { "ip": "192.168.40.34", "name": "Panzhang Wang"}
  ]
}
```






