# LightWeight_VNR

---

## 截图

- 抓取界面
![screenshot_01](Screenshot/screenshot_01.png)
- 小窗口
![screenshot_02](Screenshot/screenshot_02.png)

---

## 说明

- 本项目可调用`Textractor`来抓取`Galgame`的游戏文本
- 本项目可调用`Tesseract-OCR`来抓取文字，支持`日文`、`简体中文`、`繁体中文`、`英文`
- 本项目可调用`JBeijing`、`有道词典`、`百度翻译`来实现翻译功能
- 本项目可调用`Yukari`、`Tamiyasu`、`VOICEROID2`等来实现文本阅读功能
- 本项目可满足离线使用的需求

---

## 使用方法

### 游戏列表

- 填好`游戏名称`（可不填）、`程序目录`、`启动方式`、`特殊码`（没有可不填）后`添加`即可
    - `程序目录`、`启动方式`必须填，`游戏名称`若为空，添加时将`程序名`作为`游戏名称`
    - 转区运行需在`设置-游戏`中设置`Locale Emulator路径`
- 修改游戏信息后按`添加`即可修改信息
- 选择一项游戏后按`删除`即可删除
- 选择一项游戏后按`启动游戏`即可启动游戏，并自动启动`Textractor`注入`dll`

### Textractor

- 设置`Textractor目录`，确保目录下有`TextractorCLI.exe`和`texthook.dll`
- 点击`启动TR`，选择`游戏进程`，再`Attach`注入`dll`
    - 若从`游戏列表`中启动游戏，则无需进行此步骤
    - `游戏进程`栏也可手动输入游戏进程的pid
- 选择`钩子`并`固定`
    - 若`钩子列表`频繁刷新，可先`暂停`再选择并固定，之后再`继续`
    - 若`钩子`过长导致看不到文本内容，可按住`鼠标左键`向右拖动
- `dll`注入后，游戏进程不关，则再次打开程序只需`启动TR`并选择、固定`钩子`即可
- `特殊码`使用之前必须确保`dll`已注入，且`特殊码`格式必须正确

### OCR

- 设置`Tesseract-OCR路径`
    - 确保该路径下至少包含：
        <details>
        <summary>展开查看</summary>
        <pre>
        <code>
        ├── tessdata
        │   ├── chi_sim.traineddata
        │   ├── chi_sim_vert.traineddata
        │   ├── chi_tra.traineddata
        │   ├── chi_tra_vert.traineddata
        │   ├── eng.traineddata
        │   ├── jpn.traineddata
        │   └── jpn_vert.traineddata
        │
        ├── libgcc_s_seh-1.dll
        ├── libgif-7.dll
        ├── libgomp-1.dll
        ├── libjbig-2.dll
        ├── libjpeg-8.dll
        ├── liblept-5.dll
        ├── liblzma-5.dll
        ├── libopenjp2.dll
        ├── libpng16-16.dll
        ├── libstdc++-6.dll
        ├── libtesseract-5.dll
        ├── libtiff-5.dll
        ├── libwebp-7.dll
        ├── libwinpthread-1.dll
        ├── tesseract.exe
        └── zlib1.dll
        </code>
        </pre>
        </details>
- `截取`屏幕上的某一区域，用鼠标划定区域，划定完按`Enter`
    - 截取完会直接显示截图图片和文本
    - 按`ESC`键退出截取界面
- `截取`后按`连续`，则开始以某一间隔在同一位置进行连续识别
    - 按`结束`则结束连续识别
- 根据程序显示的图片效果，可以调整`阈值化方式`和`阈值`，来减小背景的影响

### 翻译

#### JBeijing

- `JBeijing`启用并保存即可
    - 需要在 `Python 32 bit` 环境下

#### 有道

- 注意：`有道`调用的不是API，而是本地的有道词典程序（不可`最小化`）
- 设置好`有道词典路径`后，点击`启动有道`，并切换到词典`翻译`页面
- 若本程序获取的翻译文本`错位`，可尝试增加`翻译间隔`
- 可以取消`抓取翻译`，并将词典的翻译栏拖在游戏窗口下方

#### 百度

- 注意：`百度翻译`是在线翻译，需要使用百度账号免费申请api，流程如下：
1. [https://api.fanyi.baidu.com/](https://api.fanyi.baidu.com/)进入百度翻译开放平台
2. 按照指引完成api开通，只需要申请`通用翻译API`
3. 完成申请后点击顶部`管理控制台`，在申请信息一栏可获取`APP ID`与`密钥`
- 启用百度翻译前需要填写`APP ID`与`密钥`并且**保存**

### 语音

#### Yukari（VOICEROID+ 结月缘）

- 设置好`Yukari路径`后，点击`启动Yukari`即可（可`最小化`）
- `连续阅读`：连续阅读`抓取文本`，即抓取到`新文本`时读取`新文本`
    - `阅读内容`：勾上的内容会读取，反之忽略
    - 判断依据：有`「`、`『`、`（`、`(`的为`角色对话`，反之为`旁白`

#### Tamiyasu（VOICEROID+ 民安ともえ）

- 同上

#### VOICEROID2

- 设置好`VOICEROID2路径`并`启用`即可（不需要打开）
- 可选择`VOICEROID2`已拥有的的角色阅读
    - 角色名字为`VOICEROID2`路径下的`Voice`文件夹内的各个子文件夹名称
- 可调整各项参数，同`VOICEROID2`软件界面

### 文本

- `文本去重数`：文本重复的次数
    - 类型（重复2次为例）
        - `aabbcc -> abc`
        - `abcabc -> abc`
    - `智能去重`：根据句子自动判断重复次数并去重，勾上后`文本去重数`失效
- `垃圾字符表`：去除文本中含的`垃圾字符`，`垃圾字符`以`空格`分隔
- `正则表达式`：将`正则表达式`中的所有`()`部分连接，剩下的去除

### 浮动窗口

- 打开浮动窗口，会隐藏主窗口，并显示设置中启用的条目，包括原文、各种翻译
    - 可在`抓取`和`光学`界面中打开`浮动`
- 浮动窗口可通过按`ESC`和`右键关闭`的方式退出
- 浮动窗口包含`暂停`和`阅读`的功能键，快捷键以及功能如下：
    - `暂停`：`;`，即暂停`Textractor`或`OCR`的文本抓取
    - `阅读`：`'`，即阅读当前抓取的文本

### 打包

- 本项目可用`Pyinstaller`打包，命令：`pyinstaller -Fw main.py`
    - 注意要在32位`Python`环境下，否则某些功能可能会不可用

---

## 额外说明

- 调用`J北京`、`Yukari`、`Tamiyasu`的代码参考了`VNR`的源码
- 调用`VOICEROID2`的代码参考了`Nkyoku/pyvcroid2`项目
