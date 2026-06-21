
# 咻咻打包 IP 角色圖庫
# Google Drive 直連 URL，供 kie.ai API image_input / input_urls 使用

def _gdrive_url(file_id):
    # export=download 強制取得原始檔案，比 export=view 更可靠
    return f"https://drive.google.com/uc?export=download&id={file_id}"

CHARACTERS = {
    "咻咻":   _gdrive_url("1nKHKHljt4A3X8QLoQJhgeU4ubhcuHxt5"),
    "行政喵喵": _gdrive_url("10rCSo3o9gKqj2xX_rWl6cQXYkTEN_jmT"),
    "揀貨喵喵": _gdrive_url("19hncQSYnQOFeS4ihoxUdhyNlV1Ql6NJY"),
    "咚咚膠帶": _gdrive_url("1SfqOrB8tjUEWhXR2TOl9TTzf430a-zWS"),
    "福福叉車": _gdrive_url("1wBuzYAZxPXdLOgi0e9XBFQbgVurQWlzs"),
    "卡卡刀刀": _gdrive_url("1_7lMTV0mHmvmdR5bhOQHuOFD1rvs36wQ"),
    "倉倉老闆": _gdrive_url("11rB9avhrdR3eiHusu2pzi36jGZWkijxq"),
    "咻卡":   _gdrive_url("1Rr0MqK2Jg4DN4hQJhiiOFCZnJBbFZP0v"),
    "電商老闆": _gdrive_url("1vPeOv82fPgvm6GqwNEfdSI20WdM7yE4M"),
}


def get_character_url(name):
    """取得角色的 Google Drive 直連 URL"""
    url = CHARACTERS.get(name)
    if not url:
        raise ValueError(f"找不到角色：{name}，可用角色：{list(CHARACTERS.keys())}")
    return url


def get_character_urls(names):
    """取得多個角色的 URL 列表"""
    return [get_character_url(n) for n in names]
