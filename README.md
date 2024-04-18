# 电子科技大学统一身份认证平台逆向USETC_IDAS

## 2024/04/18

- 动态获取Salt和lt
- 解决密码加密问题
- 解决滑块验证码验证问题

![](./assets/1.png)

滑块验证码解决方案：手动标记滑块起始位置，计算二者之差作为moveLength，示意图如下：

![](./assets/2.png)

目前问题：500 Server Inner Error。推测**IDS**流量分析，如果不加载css和js被检测。

```html
<div class="tab-content warn-content">
    <div class="ibox-content">
        <div id="welcome" class="warn">
            <h4>IDS is Unavailable</h4>
            <p>
                IDS is unavailable, please try again later or contact the administrator for help.
            </p>
        </div>
        <div class="welcome-button">
            <p id="back" style="text-align: center">
                <a href="javascript:history.back();" class="btn btn-primary">Previous</a>
            </p>
        </div>
    </div>
</div>
```

