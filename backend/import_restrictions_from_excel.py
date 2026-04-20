"""
从特殊款式限定位置表导入限定规则
支持三种规则类型：
1. 类型1 (style_position): 款式+位置 -> 印花白名单（可为空表示不限）
2. 类型2 (position_restriction): 位置 -> 印花白名单+款式白名单
3. 类型3 (style_ban): 款式全禁
"""
import pandas as pd
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import sys

# 添加app目录到路径
sys.path.append(os.path.dirname(__file__))
from app import models

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:123456@localhost:3306/style_print_manager?charset=utf8mb4")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_style_id_by_code(db, code):
    """根据款式编码获取ID"""
    style = db.query(models.Style).filter(models.Style.code == code).first()
    return style.id if style else None

def get_position_id_by_name(db, name):
    """根据位置名称获取ID"""
    position = db.query(models.Position).filter(models.Position.name == name).first()
    return position.id if position else None

def get_print_id_by_code(db, code):
    """根据印花编码获取ID"""
    print_obj = db.query(models.Print).filter(models.Print.code == code).first()
    return print_obj.id if print_obj else None

def import_from_excel(excel_path):
    db = SessionLocal()
    try:
        # 读取Excel
        df = pd.read_excel(excel_path)
        print(f"读取Excel: {excel_path}")
        print(f"总行数: {len(df)}")
        print(f"列名: {df.columns.tolist()}")

        # 统计
        stats = {
            'style_position': 0,
            'position_restriction': 0,
            'style_ban': 0,
            'skipped': 0,
            'errors': []
        }

        # 清空旧规则
        print("\n清空旧规则...")
        deleted = db.query(models.StylePositionRule).delete()
        db.commit()
        print(f"删除了 {deleted} 条旧规则")

        # 先识别类型，再填充款式列
        print("\n开始导入...")
        current_style = None
        for idx, row in df.iterrows():
            try:
                # 读取原始值（不填充）
                style_raw = row['款式']
                position_name = str(row['位置']).strip() if pd.notna(row['位置']) else None
                print_codes_str = str(row['印花']).strip() if pd.notna(row['印花']) else None
                limit_styles_str = str(row['限定款式']).strip() if pd.notna(row['限定款式']) else None

                # 更新当前款式（用于TYPE1和TYPE3）
                if pd.notna(style_raw):
                    current_style = str(style_raw).strip()

                # 判断规则类型（基于原始款式列是否为空）
                style_is_empty = pd.isna(style_raw)

                # 类型2: 位置限定（款式列为空，位置有值，印花和限定款式都有值）
                if style_is_empty and position_name and print_codes_str and limit_styles_str and limit_styles_str != '不限':
                    position_id = get_position_id_by_name(db, position_name)
                    if not position_id:
                        stats['errors'].append(f"行{idx+2}: 位置 {position_name} 不存在")
                        stats['skipped'] += 1
                        continue

                    # 转换印花编码为ID（允许印花）
                    print_codes = [c.strip() for c in print_codes_str.split(',') if c.strip()]
                    print_ids = []
                    for code in print_codes:
                        pid = get_print_id_by_code(db, code)
                        if pid:
                            print_ids.append(str(pid))
                        else:
                            stats['errors'].append(f"行{idx+2}: 印花 {code} 不存在")

                    # 转换款式编码为ID（允许款式）
                    style_codes = [c.strip() for c in limit_styles_str.split(',') if c.strip()]
                    style_ids = []
                    for code in style_codes:
                        sid = get_style_id_by_code(db, code)
                        if sid:
                            style_ids.append(str(sid))
                        else:
                            stats['errors'].append(f"行{idx+2}: 款式 {code} 不存在")

                    # 必须同时有允许印花和允许款式
                    if print_ids and style_ids:
                        rule = models.StylePositionRule(
                            rule_type='position_restriction',
                            position_id=position_id,
                            allowed_print_ids=','.join(print_ids),
                            allowed_style_ids=','.join(style_ids),
                            is_active=True
                        )
                        db.add(rule)
                        stats['position_restriction'] += 1
                    else:
                        stats['skipped'] += 1

                # 类型3: 款式全禁（款式列有值，位置和印花都为空）
                elif not style_is_empty and current_style and not position_name and not print_codes_str:
                    style_id = get_style_id_by_code(db, current_style)
                    if not style_id:
                        stats['errors'].append(f"行{idx+2}: 款式 {current_style} 不存在")
                        stats['skipped'] += 1
                        continue

                    rule = models.StylePositionRule(
                        rule_type='style_ban',
                        style_id=style_id,
                        is_active=True
                    )
                    db.add(rule)
                    stats['style_ban'] += 1

                # 类型1: 款式位置限定（款式列有值，位置有值）
                elif not style_is_empty and current_style and position_name:
                    style_id = get_style_id_by_code(db, current_style)
                    position_id = get_position_id_by_name(db, position_name)

                    if not style_id:
                        stats['errors'].append(f"行{idx+2}: 款式 {current_style} 不存在")
                        stats['skipped'] += 1
                        continue
                    if not position_id:
                        stats['errors'].append(f"行{idx+2}: 位置 {position_name} 不存在")
                        stats['skipped'] += 1
                        continue

                    # 转换印花编码为ID（可为空）
                    allowed_print_ids = None
                    if print_codes_str:
                        print_codes = [c.strip() for c in print_codes_str.split(',') if c.strip()]
                        print_ids = []
                        for code in print_codes:
                            pid = get_print_id_by_code(db, code)
                            if pid:
                                print_ids.append(str(pid))
                            else:
                                stats['errors'].append(f"行{idx+2}: 印花 {code} 不存在")
                        if print_ids:
                            allowed_print_ids = ','.join(print_ids)

                    rule = models.StylePositionRule(
                        rule_type='style_position',
                        style_id=style_id,
                        position_id=position_id,
                        allowed_print_ids=allowed_print_ids,
                        is_active=True
                    )
                    db.add(rule)
                    stats['style_position'] += 1

                else:
                    stats['skipped'] += 1

            except Exception as e:
                stats['errors'].append(f"行{idx+2}: {str(e)}")
                stats['skipped'] += 1

        db.commit()

        # 打印统计
        print("\n导入完成!")
        print(f"类型1 (款式+位置): {stats['style_position']} 条")
        print(f"类型2 (位置限定): {stats['position_restriction']} 条")
        print(f"类型3 (款式全禁): {stats['style_ban']} 条")
        print(f"跳过: {stats['skipped']} 条")

        if stats['errors']:
            print(f"\n错误 ({len(stats['errors'])} 个):")
            for err in stats['errors'][:10]:  # 只显示前10个错误
                print(f"  - {err}")
            if len(stats['errors']) > 10:
                print(f"  ... 还有 {len(stats['errors']) - 10} 个错误")

    finally:
        db.close()

if __name__ == "__main__":
    excel_path = r"C:\Users\Administrator\Desktop\特殊款式限定位置1.xlsx"
    if not os.path.exists(excel_path):
        print(f"错误: 文件不存在 {excel_path}")
        sys.exit(1)

    import_from_excel(excel_path)
