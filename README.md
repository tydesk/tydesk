# 统一桌面
桌面IT自动化云端解决方案

## 适用场景
拥有大量PC终端的；应用部署较多的；终端分布较分散的；终端岗位轮班的；需对接入终端控制的；IT支持人员较紧张的。包含以上一种或几种的大中型企事业单位。

## 设计目标
针对繁杂信息系统环境，优化普通用户使用体验，提升IT自动化服务水平

## 主要功能与模块
- 终端接入管理
- 应用分发管理
- IT软硬件资产管理
- 面向终端的消息平台
- 终端友好的考勤管理
- 面向终端位置的集成平台


# 快速入门
统一桌面的用户有三种类型：管理员、支持工程师和普通用户，下面分别进行介绍。

## 管理员入门
管理员作为企业用户的唯一联系人，需要在网站上注册。

### 1. 下载客户端
点击链接 [https://github.com/tydesk/tydesk/releases](https://github.com/tydesk/tydesk/releases "服务器下载页面")， 下载tydesk.zip
### 2. 部署前的准备工作
登录网站，点击设置菜单，记录下用户唯一代码。然后，解压缩tydesk.zip, 打开config.ini文件，将key的值设置为前面提到的用户唯一代码。
### 3. 部署客户端
客户端不需要单独安装，您可以将上述准备好的文件压缩后，发布到公司的局域网上，然后分别下载到各个终端上。 

## 普通用户入门
普通用户不需注册，不需登录，直接点击tydesk.exe执行即可。 

### 终端接入
终端接入代码需要联系公司的管理员。获得正确的接入代码，终端设备才可以接入公司网络。终端变更使用场所，需要再次申请接入。

## TODO
基于终端位置的和动态加密Token等，使得WEB应用无需用户码登录并可获取工作站的具体信息，基于此，可以开发以下应用：

### 文档管理
### 报修管理
### 企业密码管理器（简化其他应用的登录）


