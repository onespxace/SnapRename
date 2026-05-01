"""Generate 40 test files with 大学号/小学号 and diverse majors."""

import os
import random

SURNAMES = ["李", "王", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴", "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗"]
GIVEN_NAMES = [
    "伟", "芳", "娜", "秀英", "敏", "静", "丽", "强", "磊", "洋", "勇", "军", "杰", "涛", "明", "超", "平", "刚",
    "华", "文", "辉", "玲", "桂", "兰", "凤", "梅", "红", "鑫", "斌", "峰", "乐", "建华", "秀丽", "慧", "云", "海",
    "波", "燕", "鹏飞", "龙", "志强", "晓明", "雪梅", "雨涵", "浩然", "子轩", "博文", "思远",
]
ASSIGNMENT_TYPES = ["作业", "实验报告", "课程论文", "项目报告", "习题解答", "期末论文", "平时作业", "大作业"]
COURSES_BY_MAJOR = {
    "计科": [
        "数据结构", "操作系统", "计算机网络", "数据库原理", "软件工程", "人工智能",
        "计算机组成", "编译原理", "算法设计", "机器学习", "计算机图形学", "信息安全",
    ],
    "临床医学": [
        "人体解剖学", "生理学", "生物化学", "病理学", "药理学", "内科学", "外科学",
    ],
    "金融学": [
        "微观经济学", "宏观经济学", "计量经济学", "投资学", "公司金融", "国际金融",
    ],
    "法学": [
        "宪法学", "民法学", "刑法学", "行政法学", "经济法学", "国际法学",
    ],
    "英语": [
        "综合英语", "英语听力", "英语口语", "英美文学", "翻译理论与实践",
    ],
    "机械": [
        "机械制图", "工程力学", "机械设计", "机械制造", "数控技术",
    ],
}
MAJORS = ["计算机科学与技术", "软件工程", "临床医学", "金融学", "法学", "英语", "机械电子工程", "数据科学"]
EXTS = [".docx", ".pdf", ".doc", ".txt"]

TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_files")
os.makedirs(TEST_DIR, exist_ok=True)
# Clear old files
for f in os.listdir(TEST_DIR):
    os.remove(os.path.join(TEST_DIR, f))

random.seed(42)

def random_name():
    return random.choice(SURNAMES) + random.choice(GIVEN_NAMES)

def random_big_id():
    """Generate 12-digit 大学号 like 250808010202"""
    year = str(random.randint(20, 25))
    dept = str(random.randint(1, 99)).zfill(2)
    cls_id = str(random.randint(1, 99)).zfill(2)
    seq = str(random.randint(1, 99)).zfill(2)
    rest = str(random.randint(1, 99)).zfill(2)
    return f"{year}{dept}{cls_id}{seq}{rest}"

generated = []

for i in range(40):
    name = random_name()
    big_id = random_big_id()
    major = random.choice(MAJORS)
    # pick course from matching major group
    major_key = "计科" if major in ("计算机科学与技术", "软件工程", "数据科学") else (
        "临床医学" if major == "临床医学" else (
            "金融学" if major == "金融学" else (
                "法学" if major == "法学" else (
                    "英语" if major == "英语" else "机械"
                )
            )
        )
    )
    course = random.choice(COURSES_BY_MAJOR.get(major_key, ["高等数学"]))
    atype = random.choice(ASSIGNMENT_TYPES)
    num = random.randint(1, 8)
    ext = random.choice(EXTS)
    # Format: Name_BigID_Major_CourseTypeNum.ext
    filename = f"{name}_{big_id}_{major}_{course}{atype}{num}{ext}"
    path = os.path.join(TEST_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"学生姓名: {name}\n大学号: {big_id}\n专业: {major}\n课程: {course}{atype}{num}\n")
    generated.append(filename)

print(f"已生成 {len(generated)} 个测试文件到: {TEST_DIR}")
for f in sorted(generated):
    print(f"  {f}")
