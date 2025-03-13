// 手机号码正则表达式
const telphoneRegExp = /^1[3-9]\d{9}$/;

// 电子邮箱正则表达式
const emailRegExp = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

// 订单编号正则表达式
const orderIdRegExp = /^[A-Za-z0-9]{6,20}$/;

// 中文姓名正则表达式 (增强版-支持生僻字和少数民族姓名)
const chineseNameRegExp = /^[\u3400-\u9fa5·•]{2,15}$/;

// 身份证号码正则表达式
const idCardRegExp = /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/;

// 银行卡号正则表达式
const bankCardRegExp = /^[1-9]\d{15,18}$/;


export { telphoneRegExp, idCardRegExp, bankCardRegExp, emailRegExp, orderIdRegExp, chineseNameRegExp };
