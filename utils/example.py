"""utils工具包使用示例

展示如何使用各种工具模块。
"""

import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import (
    calculate_percentage,
    clean_string,
    days_between,
    ensure_dir,
    get_logger,
    group_by,
    now,
    parse_datetime,
    read_json,
    setup_logger,
    validate_class_data,
    validate_student_data,
    write_json,
)


def main():
    """主函数 - 演示工具包使用"""

    # 1. 设置日志系统
    setup_logger(name="utils_example", level="INFO", console_output=True, file_output=True)

    logger = get_logger("example")
    logger.info("开始演示utils工具包功能 ✨")

    # 2. 数据验证示例
    logger.info("=== 数据验证示例 ===")

    student_data = {
        "name": "张三",
        "student_number": "2024010001",
        "class_id": 1,
        "email": "zhangsan@example.com",
        "phone": "13800138000",
    }

    validation_result = validate_student_data(student_data)
    logger.info(f"学生数据验证结果: {validation_result}")

    class_data = {"name": "计算机科学与技术1班", "teacher_name": "李老师", "description": "优秀的班级"}

    class_validation = validate_class_data(class_data)
    logger.info(f"班级数据验证结果: {class_validation}")

    # 3. 文件操作示例
    logger.info("=== 文件操作示例 ===")

    # 确保目录存在
    data_dir = ensure_dir("data/examples")
    logger.info(f"创建目录: {data_dir}")

    # 写入JSON文件
    sample_data = {"students": [student_data], "classes": [class_data], "created_at": now()}

    json_file = data_dir / "sample_data.json"
    if write_json(sample_data, json_file):
        logger.info(f"写入JSON文件成功: {json_file}")

    # 读取JSON文件
    loaded_data = read_json(json_file)
    if loaded_data:
        logger.info(f"读取JSON文件成功, 包含 {len(loaded_data['students'])} 个学生")

    # 4. 数据处理示例
    logger.info("=== 数据处理示例 ===")

    # 字符串清理
    messy_text = "  这是一个   有很多空格的   字符串  "
    clean_text = clean_string(messy_text)
    logger.info(f"清理前: '{messy_text}'")
    logger.info(f"清理后: '{clean_text}'")

    # 百分比计算
    percentage = calculate_percentage(85, 100)
    logger.info(f"85/100 = {percentage}%")

    # 数据分组
    students = [
        {"name": "张三", "class_id": 1, "score": 85},
        {"name": "李四", "class_id": 1, "score": 92},
        {"name": "王五", "class_id": 2, "score": 78},
        {"name": "赵六", "class_id": 2, "score": 88},
    ]

    grouped = group_by(students, "class_id")
    for class_id, class_students in grouped.items():
        logger.info(f"班级 {class_id}: {len(class_students)} 个学生")

    # 5. 时间处理示例
    logger.info("=== 时间处理示例 ===")

    # 当前时间
    current_time = now()
    logger.info(f"当前时间: {current_time}")

    # 解析时间字符串
    time_str = "2024-01-15 10:30:00"
    parsed_time = parse_datetime(time_str)
    if parsed_time:
        logger.info(f"解析时间: {time_str} -> {parsed_time}")

        # 计算天数差
        now_dt = datetime.now()
        days_diff = days_between(parsed_time, now_dt)
        logger.info(f"距离现在 {days_diff} 天")

    # 6. 综合示例 - 学生成绩统计
    logger.info("=== 综合示例 - 学生成绩统计 ===")

    from utils.data_ops import calculate_mean, calculate_median

    scores = [85, 92, 78, 88, 95, 73, 89, 91]
    mean_score = calculate_mean(scores)
    median_score = calculate_median(scores)

    logger.info(f"成绩列表: {scores}")
    logger.info(f"平均分: {mean_score:.2f}")
    logger.info(f"中位数: {median_score:.2f}")

    # 按分数段分组
    score_ranges = []
    for score in scores:
        if score >= 90:
            range_name = "优秀"
        elif score >= 80:
            range_name = "良好"
        elif score >= 70:
            range_name = "中等"
        else:
            range_name = "需要提高"
        score_ranges.append({"score": score, "range": range_name})

    range_groups = group_by(score_ranges, "range")
    for range_name, range_scores in range_groups.items():
        count = len(range_scores)
        percentage = calculate_percentage(count, len(scores))
        logger.info(f"{range_name}: {count}人 ({percentage:.1f}%)")

    logger.info("utils工具包演示完成! 🎉")


if __name__ == "__main__":
    main()
