# constants.py

class RET:
    # 通用状态码
    OK = "0"  # 成功
    DBERR = "4001"  # 数据库错误
    NODATA = "4002"  # 无数据
    DATAEXIST = "4003"  # 数据已存在
    DATAERR = "4004"  # 数据错误

    # 用户相关
    SESSIONERR = "4101"  # 用户未登录
    LOGINERR = "4102"  # 登录失败
    PARAMERR = "4103"  # 参数错误
    USERERR = "4104"  # 用户不存在或未激活
    ROLEERR = "4105"  # 用户身份错误
    PWDERR = "4106"  # 密码错误

    # 请求相关
    REQERR = "4201"  # 非法请求
    IPERR = "4202"  # IP受限

    # 第三方服务
    THIRDERR = "4301"  # 第三方系统错误
    IOERR = "4302"  # 文件读写错误

    # 系统错误
    SERVERERR = "4500"  # 内部错误
    UNKOWNERR = "4501"  # 未知错误
    REGISTERERR = "4503"  # 注册失败


# 错误信息映射
error_map = {
    RET.OK: "成功",
    RET.DBERR: "数据库查询错误",
    RET.NODATA: "无数据",
    RET.DATAEXIST: "数据已存在",
    RET.DATAERR: "数据错误",
    RET.SESSIONERR: "用户未登录",
    RET.LOGINERR: "用户登录失败",
    RET.PARAMERR: "参数错误",
    RET.USERERR: "用户不存在或未激活",
    RET.ROLEERR: "用户身份错误",
    RET.PWDERR: "密码错误",
    RET.REQERR: "非法请求或请求次数受限",
    RET.IPERR: "IP受限",
    RET.THIRDERR: "第三方系统错误",
    RET.IOERR: "文件读写错误",
    RET.SERVERERR: "内部错误",
    RET.UNKOWNERR: "未知错误",
    RET.REGISTERERR: "注册失败",
}
