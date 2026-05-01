"""Business blacklist — exclude long major/department names from field extraction."""

DEPARTMENT_BLACKLIST: set[str] = {
    # 计算机/软件
    "计算机科学与技术", "计算机科学", "软件工程", "网络工程", "信息安全",
    "物联网工程", "数字媒体技术", "数据科学", "人工智能", "智能科学与技术",

    # 医学
    "临床医学", "基础医学", "预防医学", "口腔医学", "中医学", "中西医结合",
    "临床药学", "护理学", "医学检验技术", "医学影像学", "康复治疗学",
    "药学", "中药学", "制药工程",

    # 工程
    "电子信息工程", "通信工程", "电气工程及其自动化", "自动化",
    "机械设计制造及其自动化", "机械电子工程", "车辆工程",
    "土木工程", "建筑学", "环境工程", "材料科学与工程",
    "化学工程与工艺", "生物工程",

    # 理科
    "数学与应用数学", "信息与计算科学", "物理学", "应用物理学",
    "化学", "应用化学", "生物科学", "生物技术",

    # 经管
    "工商管理", "市场营销", "会计学", "财务管理", "人力资源管理",
    "国际经济与贸易", "金融学", "经济学",

    # 文法
    "汉语言文学", "新闻学", "法学", "行政管理", "社会学",
    "英语", "日语",

    # 其他
    "思想政治教育", "体育教育",
}

MAJOR_BLACKLIST = DEPARTMENT_BLACKLIST

NOISE_KEYWORDS = [
    "专业", "学院", "大学", "系", "班", "级",
    "实验", "报告", "作业", "论文", "习题", "考试",
    "第", "次", "份", "组", "队",
]

# Fields that should NOT be filtered by blacklist (they ARE the values we want)
KEEP_FIELDS = {"专业", "课程", "班级"}


def is_blacklisted(text: str) -> bool:
    """Check if text matches a known department/major blacklist entry."""
    return text.strip() in DEPARTMENT_BLACKLIST


def is_noise(text: str) -> bool:
    """Check if text contains keywords that suggest it's not a person name."""
    for kw in NOISE_KEYWORDS:
        if kw in text:
            return True
    return False


def filter_blacklist(candidates: dict[str, str]) -> dict[str, str]:
    """Remove blacklisted entries from candidate fields, except keep-fields like 专业."""
    return {k: v for k, v in candidates.items()
            if k in KEEP_FIELDS or (not is_blacklisted(v) and not is_noise(v))}
