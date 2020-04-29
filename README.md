#  My_LightWeight_VNR

---

## 说明

- 本项目可调用`Textractor`来抓取`Galgame`的游戏文本
- 本项目可调用`Tesseract-OCR`抓取文字，支持日文、简体中文、繁体中文、英文
- 本项目可调用`JBeijing`、`有道词典`、`百度翻译API`来实现翻译功能
- 本项目可调用`Yukari2`等TTS来实现文本阅读功能

---

## 使用方法

### Textractor
- 设置`Textractor目录`，确保目录下有`TextractorCLI.exe`和`texthook.dll`
- 点击`启动TR`，选择`游戏线程`，再`Attach`注入`dll`，之后选择`钩子`并`固定`即可
- `dll`注入后，游戏进程不关，则再次打开程序只需`启动TR`即可，无需再`Attach`
- `特殊码`使用之前必须确保dll已注入，且`特殊码`格式必须正确
- 若文本抓取出现问题，可尝试`终止TR`后再`启动TR`

### OCR
- 截取屏幕上的某一区域，用鼠标划定区域，划定完按`Enter`；若想取消划定操作，按`ESC`键
- 若设置中选择`单次截屏`，则截取完直接显示
- 若设置中选择`连续截屏`，则截取完开始以某一间隔进行连续识别；按`结束`则结束识别；按`开始`则开始识别
- 根据程序显示的图片效果，可以调整`阈值`和`阈值化方式`来使得图片中的文字更加容易被识别

### 翻译
#### 百度
注意：百度翻译API是在线翻译，需要使用百度账号免费申请api
1. https://api.fanyi.baidu.com/ 进入百度翻译开放平台
2. 按照指引完成api开通，只需要申请“通用翻译API”
3. 完成申请后点击顶部"管理控制台"，在申请信息一栏可获取APP ID与密钥

- 启动百度翻译前需要填写APP ID与密钥并且**保存**
- 如需修改APP ID与密钥，请先关闭`浮动窗口`
#### 有道
- 注意：`有道`调用的不是API，而是本地的有道词典程序
- 设置好`有道词典路径`后，点击`启动有道`，并切换到词典`翻译`页面，即可获取翻译文本（不可`最小化`）
- `有道词典`的调用方式为复制文本到`剪切板`并复制到`原文栏`，并获取`翻译栏`的文本，所以速度会偏慢
- 若本程序获取的翻译文本`错位`，可尝试增加`翻译间隔`，或取消`抓取翻译`并将词典的翻译栏拖在游戏窗口下方
- 若`有道词典`的翻译有问题，可尝试`终止有道`后再`启动有道`
#### JBeijing
- `JBeijing`启用并保存后，即可获得翻译文本

### 文本
- `文本去重数`：文本重复的次数，比如`aabbcc`为重复2次
- `垃圾字符表`：去除文本中含的`垃圾字符`，`垃圾字符`以`空格`分隔
- `正则表达式`：将`正则表达式`中的所有`()`部分连接，剩下的去除

### 语音
#### Yukari2
- 设置好`Yukari2路径`后，点击`启动Yukari2`即可（可`最小化`）
- `阅读当前文本`：读出当前`抓取文本`
- `连续阅读`：连续阅读`抓取文本`，即抓取到`新文本`时读取`新文本`
- `阅读内容`：勾上的内容会读取，反之忽略；判断依据，有`「`的为`角色对话`，反之为`旁白`

### 打包
- 本项目可用`Pyinstaller`打包，注意要在32位`Python`环境下，否则`JBeijing`不可用

---
## 额外说明
- 本项目作为本人业余学习`Python`的一个实战项目，同时也为了满足我对于`Galgame`的追求