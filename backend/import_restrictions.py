#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从桌面Excel表导入限定规则到数据库
"""
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 数据库连接
DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/style_print_manager?charset=utf8mb4"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def import_special_style_positions():
    """导入特殊款式限定位置表"""
    print("=== 导入特殊款式限定位置1.xlsx ===")
    df = pd.read_excel('C:/Users/Administrator/Desktop/特殊款式限定位置1.xlsx')
    print(f"读取到 {len(df)} 行数据")
    print(f"列名: {list(df.columns)}")

    session = Session()
    try:
        # 清空现有的款式位置规则
        result = session.execute(text("DELETE FROM style_position_rules WHERE rule_type = 'style_position'"))
        deleted = result.rowcount
        print(f"删除了 {deleted} 条旧的款式位置规则")

        inserted = 0
        skipped = 0

        for idx, row in df.iterrows():
            style_code = row['款式']
            position_name = row['位置']
            allowed_prints = row.get('印花', None)

            # 跳过空行
            if pd.isna(style_code) or pd.isna(position_name):
                skipped += 1
                continue

            style_code = str(style_code).strip()
            position_name = str(position_name).strip()

            # 查询款式ID
            style_result = session.execute(
                text("SELECT id FROM styles WHERE code = :code"),
                {"code": style_code}
            ).fetchone()

            if not style_result:
                print(f"  警告: 款式 '{style_code}' 不存在，跳过")
                skipped += 1
                continue

            style_id = style_result[0]

            # 查询位置ID
            position_result = session.execute(
                text("SELECT id FROM positions WHERE name = :name"),
                {"name": position_name}
            ).fetchone()

            if not position_result:
                print(f"  警告: 位置 '{position_name}' 不存在，跳过")
                skipped += 1
                continue

            position_id = position_result[0]

            # 处理允许印花
            allowed_prints_str = None
            if pd.notna(allowed_prints):
                allowed_prints_str = str(allowed_prints).strip()
                if allowed_prints_str:
                    # 清理印花编码（去除空格）
                    allowed_prints_str = ','.join([p.strip() for p in allowed_prints_str.split(',')])

            # 插入规则
            session.execute(text("""
                INSERT INTO style_position_rules
                (rule_type, style_id, position_id, allowed_prints, is_active, remark)
                VALUES ('style_position', :style_id, :position_id, :allowed_prints, 1, '从特殊款式限定位置表导入')
            """), {
                "style_id": style_id,
                "position_id": position_id,
                "allowed_prints": allowed_prints_str
            })
            inserted += 1

        session.commit()
        print(f"[OK] 成功导入 {inserted} 条款式位置规则，跳过 {skipped} 条")

    except Exception as e:
        session.rollback()
        print(f"[ERROR] 导入失败: {e}")
        raise
    finally:
        session.close()

def import_velcro_restrictions():
    """导入魔术贴限定表"""
    print("\n=== 导入魔术贴限定表1.xlsx ===")
    df = pd.read_excel('C:/Users/Administrator/Desktop/魔术贴限定表1.xlsx')
    print(f"读取到 {len(df)} 行数据")
    print(f"列名: {list(df.columns)}")

    session = Session()
    try:
        # 清空现有的位置印花规则
        result = session.execute(text("DELETE FROM style_position_rules WHERE rule_type = 'position_print'"))
        deleted = result.rowcount
        print(f"删除了 {deleted} 条旧的位置印花规则")

        inserted = 0
        skipped = 0

        for idx, row in df.iterrows():
            print_code = row['印花编码']
            position_name = row['限定位置']
            allowed_styles_str = row.get('款式', None)

            # 跳过空行
            if pd.isna(print_code) or pd.isna(position_name):
                skipped += 1
                continue

            print_code = str(print_code).strip()
            position_name = str(position_name).strip()

            # 查询位置ID
            position_result = session.execute(
                text("SELECT id FROM positions WHERE name = :name"),
                {"name": position_name}
            ).fetchone()

            if not position_result:
                print(f"  警告: 位置 '{position_name}' 不存在，跳过")
                skipped += 1
                continue

            position_id = position_result[0]

            # 处理允许款式
            allowed_style_ids = None
            if pd.notna(allowed_styles_str):
                style_codes = [s.strip() for s in str(allowed_styles_str).split(',')]
                style_ids = []

                for style_code in style_codes:
                    if not style_code:
                        continue

                    style_result = session.execute(
                        text("SELECT id FROM styles WHERE code = :code"),
                        {"code": style_code}
                    ).fetchone()

                    if style_result:
                        style_ids.append(str(style_result[0]))
                    else:
                        print(f"  警告: 款式 '{style_code}' 不存在")

                if style_ids:
                    allowed_style_ids = ','.join(style_ids)

            # 插入规则
            session.execute(text("""
                INSERT INTO style_position_rules
                (rule_type, position_id, print_code, allowed_styles, is_active, remark)
                VALUES ('position_print', :position_id, :print_code, :allowed_styles, 1, '从魔术贴限定表导入')
            """), {
                "position_id": position_id,
                "print_code": print_code,
                "allowed_styles": allowed_style_ids
            })
            inserted += 1

        session.commit()
        print(f"[OK] 成功导入 {inserted} 条位置印花规则，跳过 {skipped} 条")

    except Exception as e:
        session.rollback()
        print(f"[ERROR] 导入失败: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    try:
        import_special_style_positions()
        import_velcro_restrictions()
        print("\n[OK] 所有数据导入完成！")
    except Exception as e:
        print(f"\n[ERROR] 导入过程出错: {e}")
        sys.exit(1)
