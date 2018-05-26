# TyDesk - 统医桌面
一个超级简单、功能全面的、专为中国医院设计的WEB应用启动器

## 医院为什么需要“桌面入口”程序？
主要包含以下几个理由：

- 医院系统种类繁多，且都有WEB接口
- WEB入口URL过长，不易部署；普通用户不易使用
- 无统一入口情况下，医生浪费时间在寻找、定位、打开等时间上
- 医院公用电脑较多，个性化的收藏和桌面都不适用
- 有些系统需要IE，有些系统需要谷歌;这让无技术背景的医生很疲惫
- 桌面云的失败，给“桌面入口”程序更多的存在合理性

## 主要功能
- 实现了多系统的桌面集成
- 对Web应用的集中分发
- 对医院内、外网环境的适应
- 对多种浏览器的支持
- 对离线的支持
- 为医院IT自动化管理提供接口与支持

## IT 管理上的功能与特色
- 自动收集各种终端的物理参数
- 终端USB存储的集中管理
- 多角度、自动化对IT终端的盘点
- 为防统方等应用提供位置API服务
- 为核心业务系统提供安全的IP/主机绑定
- 为信息系统安全和审计提供技术基础与保障

## 使用指南

### 下载服务器
[https://github.com/tydesk/tyserver/releases](https://github.com/tydesk/tyserver/releases "服务器下载页面")， 下载TyServer.zip

### 配置服务器
下载完毕后，解压缩TyServer.zip。直接启动里面的Exe即可启动服务器。 要发布新应用，需要配置config.json


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

为了尽量简单和更容易扩展，分发的服务器端没有使用GUI界面，而是使用配置JSON的方式来实现。下面来解释几个注意事项：
- outApps为门诊应用；inApps为住院应用；otherApps为其他应用；admins管理端界面访问授权
- url 当包括参数时，使用双下划线来代替
- open为可选打开URL的浏览器类型：IE, chrome, firefox
- 内外网：out为外网, in为内网

另外，如果你略懂一些Python和JSON的知识，你完全可以对桌面入口程序进行深度定制。config.json实际上就是一个JSON数据库，您可以采取Rest方式访问它，这也是没有使用GUI的好处。

### 下载客户端
[https://github.com/tydesk/tydesk/releases](https://github.com/tydesk/tydesk/releases)，下载tydesk.zip

### 配置客户端
下载完毕后，解压缩tydesk.zip。 同样，无需安装点击里面的Exe文件即可。事先需修改config.ini，指向正确的内网、外网服务器IP
```ini
inner.host=172.20.10.100
outer.host=192.168.30.101
```
> inner.host为服务器的内网IP；outer.host为服务器的外网IP

### 可以使用了
新分发的WEB应用在30分钟后会自动更新到所有的客户端上。 根据所在内外网，管理员可以往访问管理界面了：
```html
http://<inner.host>:5678/admin/index
http://<outer.host>:5678/admin/index
```

## 环境与配置

### 客户端
支持Win xp, Win 7, win 8, Win 10

### 服务器
64位的任何版本的Windows Server或者64位的Win 7/10, 内存4G以上

### 浏览器
支持各种浏览器，并能自适应

### 构建Exe
需要懂一点Python知识。

1. 下载安装Python 2, 安装requests等依赖
2. pip install pyinstaller
3. pyinstaller --onefile --noconsole tydesk.py




